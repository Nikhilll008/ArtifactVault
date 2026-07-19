"""
CONCEPT: Django + DRF + Dict + CSV + Threading + Regex (search) + OOP
--------------------------------------------------------------------------
Class-based APIViews. GET endpoints are public (AllowAny) to match the
public catalog on the frontend; write endpoints (POST/PATCH/DELETE,
plus CSV import/export) require a logged-in curator (IsCurator).
"""
import csv
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.common.permissions import IsCurator
from apps.common.pagination import paginate_list
from apps.common.csv_utils import dicts_to_csv_response
from apps.common.threads import start_job, get_job, JOBS, _jobs_lock

from .repository import ArtifactRepository
from .serializers import ArtifactSerializer
from .constants import CSV_FIELDS


class ArtifactListCreateView(APIView):
    """GET  /api/artifacts/   -> search + filter + paginate (public)
       POST /api/artifacts/   -> create a new artifact (curator only)"""

    def get_permissions(self):
        return [IsCurator()] if self.request.method == 'POST' else [AllowAny()]

    def get(self, request):
        filters = {
            'category': request.query_params.get('category'),
            'era': request.query_params.get('era'),
            'material': request.query_params.get('material'),
            'origin': request.query_params.get('origin'),
            'status': request.query_params.get('status'),
            'q': request.query_params.get('q'),
        }
        results = ArtifactRepository().search(filters)
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 9)
        return Response(paginate_list(results, page, page_size))

    def post(self, request):
        serializer = ArtifactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        artifact = ArtifactRepository().create_artifact(serializer.validated_data)
        return Response(artifact, status=status.HTTP_201_CREATED)


class ArtifactDetailView(APIView):
    """GET    /api/artifacts/<id>/  -> artifact + related artifacts (public)
       PATCH  /api/artifacts/<id>/  -> partial update (curator only)
       DELETE /api/artifacts/<id>/  -> remove (curator only)"""

    def get_permissions(self):
        return [AllowAny()] if self.request.method == 'GET' else [IsCurator()]

    def get(self, request, artifact_id):
        repo = ArtifactRepository()
        artifact = repo.find_one({'id': artifact_id})
        if not artifact:
            return Response({'detail': 'Artifact not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'artifact': artifact, 'related': repo.related(artifact)})

    def patch(self, request, artifact_id):
        repo = ArtifactRepository()
        if not repo.find_one({'id': artifact_id}):
            return Response({'detail': 'Artifact not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ArtifactSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        repo.update({'id': artifact_id}, serializer.validated_data)
        return Response(repo.find_one({'id': artifact_id}))

    def delete(self, request, artifact_id):
        if not ArtifactRepository().delete({'id': artifact_id}):
            return Response({'detail': 'Artifact not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArtifactStatsView(APIView):
    """GET /api/artifacts/stats/ -> dict of totals + per-category breakdown (public,
    powers the Home page stat cards and the Dashboard's collection-statistics bars)."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(ArtifactRepository().stats())


class ArtifactExportCSVView(APIView):
    """GET /api/artifacts/export/ -> downloadable CSV of the full catalog (curator only)."""
    permission_classes = [IsCurator]

    def get(self, request):
        rows = ArtifactRepository().find_many({})
        return dicts_to_csv_response(rows, CSV_FIELDS, 'artifacts_export.csv')


def _process_artifact_csv_import(job_id: str, csv_text: str) -> dict:
    """Runs on a background thread (see apps/common/threads.py). Parses
    the uploaded CSV row by row, validates each row through the same
    ArtifactSerializer used by the API, and inserts valid rows into
    MongoDB — updating the shared JOBS dict as it goes so the client can
    poll progress."""
    repo = ArtifactRepository()
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    with _jobs_lock:
        JOBS[job_id]['total'] = len(rows)

    created, errors = 0, []
    for i, raw_row in enumerate(rows, start=1):
        row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw_row.items() if k}
        try:
            serializer = ArtifactSerializer(data=row)
            serializer.is_valid(raise_exception=True)
            repo.create_artifact(serializer.validated_data)
            created += 1
        except Exception as exc:
            errors.append({'row': i, 'error': str(exc)})
        with _jobs_lock:
            JOBS[job_id]['processed'] = i

    return {'created': created, 'skipped': len(errors), 'errors': errors}


class ArtifactImportCSVView(APIView):
    """POST /api/artifacts/import/ -> upload a CSV file under the "file"
    field. Returns immediately with a job_id; the actual parsing/insert
    happens on a background thread so the request never blocks on a
    large file (curator only)."""
    permission_classes = [IsCurator]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'detail': 'Attach a CSV file under the "file" form field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        csv_text = file_obj.read().decode('utf-8-sig')
        job_id = start_job(_process_artifact_csv_import, args=(csv_text,))
        return Response(
            {'job_id': job_id, 'detail': 'Import started in the background. Poll /import/status/<job_id>/.'},
            status=status.HTTP_202_ACCEPTED,
        )


class ArtifactImportStatusView(APIView):
    """GET /api/artifacts/import/status/<job_id>/ -> poll background import progress."""
    permission_classes = [IsCurator]

    def get(self, request, job_id):
        job = get_job(job_id)
        if job is None:
            return Response({'detail': 'Unknown job id.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(job)
