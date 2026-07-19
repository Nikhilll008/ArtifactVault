"""
CONCEPT: Threading
--------------------
When a new loan is registered, the borrowing institution should be
"notified" — in a real system this might be an email/SMS API call that
takes a second or two. We don't want the curator's POST request to sit
there waiting on that, so the notification is fired on its own daemon
thread and the HTTP response returns immediately.
"""
import threading
import time


def _send_notification(loan_id: str, borrower: str, artifact_name: str):
    time.sleep(2)  # simulated network latency for an email/SMS gateway
    print(f"[notification-thread] Loan {loan_id}: notified '{borrower}' "
          f"about the loan of '{artifact_name}'.")


def notify_loan_created_async(loan_id: str, borrower: str, artifact_name: str):
    threading.Thread(
        target=_send_notification,
        args=(loan_id, borrower, artifact_name),
        daemon=True,
    ).start()
