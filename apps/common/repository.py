
from .mongo import MongoConnection


class BaseRepository:
    collection_name: str = None  # subclasses must set this

    def __init__(self):
        if not self.collection_name:
            raise NotImplementedError('Set collection_name on the repository subclass.')
        self.collection = MongoConnection().collection(self.collection_name)

    @staticmethod
    def _strip_internal_id(doc):
        """Mongo's auto _id (ObjectId) isn't JSON serialisable and isn't
        part of our public API shape, so we always drop it before a
        document leaves the repository layer."""
        if not doc:
            return doc
        doc = dict(doc)
        doc.pop('_id', None)
        return doc

    def find_one(self, query: dict) -> dict | None:
        return self._strip_internal_id(self.collection.find_one(query, {'_id': 0}))

    def find_many(self, query: dict, sort: tuple | None = None) -> list[dict]:
        cursor = self.collection.find(query, {'_id': 0})
        if sort:
            field, direction = sort
            cursor = cursor.sort(field, direction)
        return list(cursor)

    def insert(self, document: dict) -> dict:
        self.collection.insert_one(dict(document))
        return self._strip_internal_id(document)

    def update(self, query: dict, updates: dict) -> bool:
        result = self.collection.update_one(query, {'$set': dict(updates)})
        return result.matched_count > 0

    def delete(self, query: dict) -> bool:
        result = self.collection.delete_one(query)
        return result.deleted_count > 0

    def count(self, query: dict | None = None) -> int:
        return self.collection.count_documents(query or {})
