
import csv
import io
from django.http import HttpResponse


def dicts_to_csv_response(rows: list[dict], fieldnames: list[str], filename: str) -> HttpResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def read_csv_text_rows(csv_text: str) -> list[dict]:
    """Parse raw CSV text into a list of plain dicts, trimming whitespace
    from every cell."""
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    for raw_row in reader:
        cleaned = {
            (k.strip() if k else k): (v.strip() if isinstance(v, str) else v)
            for k, v in raw_row.items()
        }
        rows.append(cleaned)
    return rows
