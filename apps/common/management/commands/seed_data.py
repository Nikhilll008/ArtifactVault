"""
CONCEPT: Django (management command) + CSV + Dict + MongoDB + OOP
----------------------------------------------------------------------
Run with:   python manage.py seed_data
Optionally: python manage.py seed_data --reset   (wipes collections first)

This is a normal Django management command (BaseCommand subclass —
OOP again) that reads the two CSV files in data/, turns each row into
a dict via csv.DictReader, and inserts them into MongoDB through the
same repository classes the API views use — so the seeded data is
guaranteed to be shaped exactly like what the API expects. It also
creates one demo curator account so you can log in immediately.
"""
import csv
from pathlib import Path

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from apps.artifacts.repository import ArtifactRepository
from apps.loans.repository import LoanRepository
from apps.curators.repository import CuratorRepository

DATA_DIR = Path(settings.BASE_DIR) / 'data'

DEMO_CURATOR = {
    'name': 'Dr. Anjali Deshmukh',
    'email': 'curator@artifactvault.example.org',
    'password': 'Heritage@123',
    'department': 'Maratha History & Archaeology',
    'role': 'Senior Curator',
}


def read_csv_as_dicts(path: Path) -> list[dict]:
    with open(path, newline='', encoding='utf-8-sig') as f:
        return [dict(row) for row in csv.DictReader(f)]


class Command(BaseCommand):
    help = 'Seed MongoDB with sample artifacts, loans and a demo curator account from data/*.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Delete all existing documents in artifacts/loans/curators/sessions before seeding.',
        )

    def handle(self, *args, **options):
        artifact_repo = ArtifactRepository()
        loan_repo = LoanRepository()
        curator_repo = CuratorRepository()

        if options['reset']:
            from apps.curators.repository import SessionRepository
            for repo in (artifact_repo, loan_repo, curator_repo, SessionRepository()):
                repo.collection.delete_many({})
            self.stdout.write(self.style.WARNING('Cleared existing artifacts, loans, curators and sessions.'))

        # ---- Artifacts ----
        artifact_rows = read_csv_as_dicts(DATA_DIR / 'artifacts_seed.csv')
        inserted = 0
        for row in artifact_rows:
            if artifact_repo.find_one({'id': row['id']}):
                continue
            artifact_repo.insert(row)
            inserted += 1
        self.stdout.write(self.style.SUCCESS(f'Artifacts: inserted {inserted} / {len(artifact_rows)} rows.'))

        # ---- Loans ----
        loan_rows = read_csv_as_dicts(DATA_DIR / 'loans_seed.csv')
        inserted = 0
        for row in loan_rows:
            if loan_repo.find_one({'id': row['id']}):
                continue
            loan_repo.insert(row)
            inserted += 1
        self.stdout.write(self.style.SUCCESS(f'Loans: inserted {inserted} / {len(loan_rows)} rows.'))

        # ---- Demo curator ----
        if not curator_repo.email_exists(DEMO_CURATOR['email']):
            payload = dict(DEMO_CURATOR)
            payload['password'] = make_password(payload['password'])
            curator_repo.create_curator(payload)
            self.stdout.write(self.style.SUCCESS(
                f"Demo curator created -> email: {DEMO_CURATOR['email']}  password: {DEMO_CURATOR['password']}"
            ))
        else:
            self.stdout.write('Demo curator already exists, skipping.')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
