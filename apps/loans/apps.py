"""
CONCEPT: Threading + Django
-----------------------------
`ready()` is a Django hook that fires once, when the app registry has
fully loaded. We use it to kick off a long-running background thread
(see background.py) that periodically scans MongoDB for loans whose
due date has passed and flips their status to "Overdue" — independent
of any single HTTP request.
"""
import os
import sys

from django.apps import AppConfig


class LoansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.loans'

    def ready(self):
        # Only start the worker when actually serving requests via
        # `runserver` (not during migrate/makemigrations/shell/tests),
        # and only in the real child process spawned by the autoreloader
        # (guarded by RUN_MAIN) so we don't start it twice.
        is_runserver = 'runserver' in sys.argv
        is_reloader_child = os.environ.get('RUN_MAIN') == 'true'
        if is_runserver and (is_reloader_child or '--noreload' in sys.argv):
            from .background import start_overdue_checker
            start_overdue_checker()
