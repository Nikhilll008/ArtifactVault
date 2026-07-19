
from pymongo import MongoClient
from django.conf import settings


class MongoConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.client = MongoClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000,
            )
            instance.db = instance.client[settings.MONGO_DB_NAME]
            cls._instance = instance
        return cls._instance

    def collection(self, name: str):
        """Return a handle to a named MongoDB collection."""
        return self.db[name]

    def ping(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
