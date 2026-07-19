"""
CONCEPT: Django + DRF + CSV + Threading
-------------------------------------------
All loan endpoints require a logged-in curator (IsCurator) — loan
tracking is an internal museum-management workflow, not a public
catalog feature.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.common.permissions import IsCurator
from apps.common.pagination import paginate_list
from apps.common.csv_utils import dicts_to_csv_response
from apps.artifacts.repository import ArtifactRepository

from .repository import LoanRepository
from .serializers import LoanSerializer
from .notifications import notify_loan_created_async

CSV_FIELDS = ['id', 'artifact', 'artifactId', 'borrower', 'loanDate', 'dueDate', 'status', 'contact']


class LoanListCreateView(APIView):
    permission_classes = [IsCurator]

    def get(self, request):
        tab = request.query_params.get('tab', 'All')
        q = request.query_params.get('q')
        results = LoanRepository().search(tab, q)
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        return Response(paginate_list(results, page, page_size))

    def post(self, request):
        serializer = LoanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.to_internal_dates(serializer.validated_data)

        if not ArtifactRepository().find_one({'id': data['artifactId']}):
            return Response(
                {'detail': 'artifactId does not match any catalogued artifact.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan = LoanRepository().create_loan(data)
        notify_loan_created_async(loan['id'], loan['borrower'], loan['artifact'])
        return Response(loan, status=status.HTTP_201_CREATED)


class LoanDetailView(APIView):
    permission_classes = [IsCurator]

    def get(self, request, loan_id):
        loan = LoanRepository().find_one({'id': loan_id})
        if not loan:
            return Response({'detail': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(loan)

    def patch(self, request, loan_id):
        repo = LoanRepository()
        if not repo.find_one({'id': loan_id}):
            return Response({'detail': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LoanSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.to_internal_dates(serializer.validated_data)
        repo.update({'id': loan_id}, data)
        return Response(repo.find_one({'id': loan_id}))


class LoanReturnView(APIView):
    """PATCH /api/loans/<id>/return/ -> mark a loan as Returned."""
    permission_classes = [IsCurator]

    def patch(self, request, loan_id):
        if not LoanRepository().mark_returned(loan_id):
            return Response({'detail': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(LoanRepository().find_one({'id': loan_id}))


class LoanSummaryView(APIView):
    permission_classes = [IsCurator]

    def get(self, request):
        return Response(LoanRepository().summary())


class LoanExportCSVView(APIView):
    permission_classes = [IsCurator]

    def get(self, request):
        rows = LoanRepository().find_many({})
        return dicts_to_csv_response(rows, CSV_FIELDS, 'loans_export.csv')
