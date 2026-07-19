"""
CONCEPT: OOP (inheritance) + MongoDB + Regex + Dict
------------------------------------------------------
LoanRepository inherits the generic CRUD from BaseRepository and adds
loan-specific behaviour: tab-based filtering (Active/Returned/All) plus
free-text search, returning a loan, syncing overdue status in bulk,
and a small summary dict used by the curator dashboard.
"""
from datetime import date

from apps.common.repository import BaseRepository
from apps.common.validators import sanitize_search_term, extract_numeric_suffix


class LoanRepository(BaseRepository):
    collection_name = 'loans'

    def next_id(self) -> str:
        max_num = 0
        for doc in self.collection.find({}, {'id': 1}):
            num = extract_numeric_suffix(doc.get('id', ''), 'LN')
            if num is not None:
                max_num = max(max_num, num)
        return f'LN-{max_num + 1:04d}'

    def search(self, tab: str = 'All', q: str | None = None) -> list[dict]:
        query: dict = {}
        if tab == 'Active':
            query['status'] = {'$in': ['Active', 'Overdue']}
        elif tab == 'Returned':
            query['status'] = 'Returned'

        if q:
            term = sanitize_search_term(q)
            pattern = {'$regex': term, '$options': 'i'}
            query['$or'] = [
                {'artifact': pattern}, {'borrower': pattern},
                {'id': pattern}, {'contact': pattern},
            ]

        return self.find_many(query, sort=('dueDate', 1))

    def create_loan(self, data: dict) -> dict:
        doc = dict(data)
        doc['id'] = self.next_id()
        doc.setdefault('status', 'Active')
        return self.insert(doc)

    def mark_returned(self, loan_id: str) -> bool:
        return self.update({'id': loan_id}, {'status': 'Returned', 'returnedOn': date.today().isoformat()})

    def sync_overdue_status(self) -> int:
        """Flip any Active loan whose dueDate has passed to Overdue.
        Returns how many documents were changed. Called both by the
        background thread (background.py) and could be called manually."""
        today_iso = date.today().isoformat()
        result = self.collection.update_many(
            {'status': 'Active', 'dueDate': {'$lt': today_iso}},
            {'$set': {'status': 'Overdue'}},
        )
        return result.modified_count

    def summary(self) -> dict:
        return {
            'active': self.count({'status': 'Active'}),
            'overdue': self.count({'status': 'Overdue'}),
            'returned': self.count({'status': 'Returned'}),
        }
