
import threading
import uuid
from typing import Callable

JOBS: dict[str, dict] = {}
_jobs_lock = threading.Lock()


class BackgroundTask(threading.Thread):
    def __init__(self, job_id: str, target: Callable, args: tuple = ()):
        super().__init__(daemon=True)
        self.job_id = job_id
        self.target = target
        self.args = args

    def run(self):
        with _jobs_lock:
            JOBS[self.job_id]['status'] = 'running'
        try:
            result = self.target(self.job_id, *self.args)
            with _jobs_lock:
                JOBS[self.job_id]['status'] = 'completed'
                JOBS[self.job_id]['result'] = result
        except Exception as exc:
            with _jobs_lock:
                JOBS[self.job_id]['status'] = 'failed'
                JOBS[self.job_id]['error'] = str(exc)


def start_job(target: Callable, args: tuple = ()) -> str:
    """Register a new job dict and start its worker thread. Returns the
    job_id the client should poll."""
    job_id = uuid.uuid4().hex[:12]
    with _jobs_lock:
        JOBS[job_id] = {'status': 'queued', 'processed': 0, 'total': 0, 'errors': []}
    BackgroundTask(job_id, target, args).start()
    return job_id


def get_job(job_id: str) -> dict | None:
    with _jobs_lock:
        return dict(JOBS[job_id]) if job_id in JOBS else None


def update_job(job_id: str, **fields):
    with _jobs_lock:
        if job_id in JOBS:
            JOBS[job_id].update(fields)
