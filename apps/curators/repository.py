"""
CONCEPT: OOP (inheritance) + MongoDB + Regex + Dict
------------------------------------------------------
Two small repositories living in one file since they're tightly
related: CuratorRepository (the curator's profile/credentials) and
SessionRepository (login tokens). Both inherit the same BaseRepository
CRUD surface but point at different MongoDB collections.
"""
import secrets
from datetime import datetime, timezone

from apps.common.repository import BaseRepository
from apps.common.validators import extract_numeric_suffix


class CuratorRepository(BaseRepository):
    collection_name = 'curators'

    def email_exists(self, email: str) -> bool:
        return self.find_one({'email': email.lower()}) is not None

    def next_id(self) -> str:
        max_num = 0
        for doc in self.collection.find({}, {'id': 1}):
            num = extract_numeric_suffix(doc.get('id', ''), 'CUR')
            if num is not None:
                max_num = max(max_num, num)
        return f'CUR-{max_num + 1:03d}'

    def create_curator(self, data: dict) -> dict:
        """`data['password']` must already be a Django password hash —
        hashing happens in the view, this layer only persists it."""
        doc = {
            'id': self.next_id(),
            'name': data['name'],
            'email': data['email'].lower(),
            'password': data['password'],
            'department': data.get('department') or 'General',
            'role': data.get('role') or 'Curator',
            'dateJoined': datetime.now(timezone.utc).date().isoformat(),
        }
        return self.insert(doc)


class SessionRepository(BaseRepository):
    collection_name = 'sessions'

    def create_session(self, curator_id: str) -> str:
        token = secrets.token_hex(32)
        self.insert({
            'token': token,
            'curatorId': curator_id,
            'createdAt': datetime.now(timezone.utc).isoformat(),
        })
        return token

    def destroy(self, token: str) -> bool:
        return self.delete({'token': token})
