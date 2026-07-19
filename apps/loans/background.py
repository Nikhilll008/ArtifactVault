"""
CONCEPT: Threading
--------------------
A simple long-running daemon thread, separate from Django's request/
response cycle entirely. It wakes up every few minutes, asks
LoanRepository to mark any Active loan past its due date as Overdue,
and goes back to sleep. `threading.Event.wait()` is used instead of
`time.sleep()` so the loop can (in theory) be told to stop cleanly via
`_STOP_EVENT.set()`.
"""
import threading

_STOP_EVENT = threading.Event()
_started = False
CHECK_INTERVAL_SECONDS = 300  # 5 minutes


def _loop():
    from .repository import LoanRepository  # imported lazily to avoid app-loading order issues
    repo = LoanRepository()
    while not _STOP_EVENT.is_set():
        try:
            updated = repo.sync_overdue_status()
            if updated:
                print(f'[overdue-checker] marked {updated} loan(s) as Overdue')
        except Exception as exc:
            print('[overdue-checker] error while syncing overdue loans:', exc)
        _STOP_EVENT.wait(timeout=CHECK_INTERVAL_SECONDS)


def start_overdue_checker():
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_loop, name='overdue-checker', daemon=True).start()


def stop_overdue_checker():
    _STOP_EVENT.set()
