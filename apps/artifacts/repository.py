"""
CONCEPT: OOP (inheritance) + MongoDB + Dict + Regex
------------------------------------------------------
ArtifactRepository INHERITS the generic CRUD methods from
BaseRepository (find_one, find_many, insert, update, delete, count)
and adds artifact-specific behaviour on top: free-text search across
several fields, filtering by era/material/origin/category/status,
category statistics (a MongoDB aggregation pipeline returned as a
plain dict), and auto-generated accession numbers (AV-0001, AV-0002,
...) computed with a regex over existing ids.
"""
from datetime import date

from apps.common.repository import BaseRepository
from apps.common.validators import sanitize_search_term, extract_numeric_suffix


class ArtifactRepository(BaseRepository):
    collection_name = 'artifacts'

    def next_id(self) -> str:
        max_num = 0
        for doc in self.collection.find({}, {'id': 1}):
            num = extract_numeric_suffix(doc.get('id', ''), 'AV')
            if num is not None:
                max_num = max(max_num, num)
        return f'AV-{max_num + 1:04d}'

    def search(self, filters: dict) -> list[dict]:
        """Build a MongoDB query dict from a dict of optional filters."""
        query: dict = {}

        if filters.get('category'):
            query['category'] = filters['category']
        if filters.get('era'):
            query['eraGroup'] = filters['era']
        if filters.get('material'):
            query['materialGroup'] = filters['material']
        if filters.get('origin'):
            query['originGroup'] = filters['origin']
        if filters.get('status'):
            query['status'] = filters['status']

        q = filters.get('q')
        if q:
            term = sanitize_search_term(q)
            pattern = {'$regex': term, '$options': 'i'}
            query['$or'] = [
                {'name': pattern}, {'era': pattern}, {'material': pattern},
                {'origin': pattern}, {'category': pattern},
            ]

        return self.find_many(query, sort=('dateAdded', -1))

    def related(self, artifact: dict, limit: int = 3) -> list[dict]:
        results = self.find_many({'category': artifact['category'], 'id': {'$ne': artifact['id']}})
        return results[:limit]

    def stats(self) -> dict:
        """Returns a stats dict, including a category breakdown computed
        with a MongoDB aggregation pipeline."""
        pipeline = [{'$group': {'_id': '$category', 'count': {'$sum': 1}}}]
        by_category = {row['_id']: row['count'] for row in self.collection.aggregate(pipeline)}
        return {
            'total': self.count(),
            'displayed': self.count({'status': 'Displayed'}),
            'inStorage': self.count({'status': 'In Storage'}),
            'onLoan': self.count({'status': 'On Loan'}),
            'byCategory': by_category,
        }

    def create_artifact(self, data: dict) -> dict:
        doc = dict(data)
        doc['id'] = self.next_id()
        doc.setdefault('status', 'In Storage')
        doc.setdefault('icon', 'artifacts')
        doc['dateAdded'] = date.today().isoformat()
        return self.insert(doc)
