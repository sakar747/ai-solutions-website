import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from django.conf import settings

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except Exception:  # pragma: no cover - only used if pymongo is unavailable locally
    MongoClient = None
    PyMongoError = Exception

DATA_DIR = settings.BASE_DIR / "data_store"
DATA_DIR.mkdir(exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_reference(prefix="AIQ"):
    return f"{prefix}-{datetime.now().year}-{uuid4().hex[:8].upper()}"


class Storage:
    def __init__(self):
        self.client = None
        self.db = None
        if settings.MONGO_URI and MongoClient is not None:
            try:
                self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=4000)
                self.client.admin.command("ping")
                self.db = self.client[settings.MONGO_DB_NAME]
            except Exception:
                self.client = None
                self.db = None

    @property
    def using_mongo(self):
        return self.db is not None

    def _file(self, collection):
        return DATA_DIR / f"{collection}.json"

    def _read_file(self, collection):
        file_path = self._file(collection)
        if not file_path.exists():
            return []
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _write_file(self, collection, rows):
        self._file(collection).write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def insert(self, collection, data):
        data = dict(data)
        data.setdefault("id", uuid4().hex)
        data.setdefault("created_at", now_iso())
        data.setdefault("updated_at", now_iso())
        if self.using_mongo:
            result = self.db[collection].insert_one(data)
            data["id"] = str(result.inserted_id)
            return data
        rows = self._read_file(collection)
        rows.append(data)
        self._write_file(collection, rows)
        return data

    def all(self, collection, sort_key="created_at", reverse=True):
        if self.using_mongo:
            rows = list(self.db[collection].find({}))
            for row in rows:
                row["id"] = str(row.get("_id"))
                row.pop("_id", None)
        else:
            rows = self._read_file(collection)
        return sorted(rows, key=lambda item: item.get(sort_key, ""), reverse=reverse)

    def get(self, collection, item_id):
        if self.using_mongo:
            from bson import ObjectId
            try:
                row = self.db[collection].find_one({"_id": ObjectId(item_id)})
            except Exception:
                row = self.db[collection].find_one({"id": item_id})
            if not row:
                return None
            row["id"] = str(row.get("_id", row.get("id")))
            row.pop("_id", None)
            return row
        for row in self._read_file(collection):
            if str(row.get("id")) == str(item_id):
                return row
        return None

    def update(self, collection, item_id, updates):
        updates = dict(updates)
        updates["updated_at"] = now_iso()
        if self.using_mongo:
            from bson import ObjectId
            try:
                self.db[collection].update_one({"_id": ObjectId(item_id)}, {"$set": updates})
            except Exception:
                self.db[collection].update_one({"id": item_id}, {"$set": updates})
            return self.get(collection, item_id)
        rows = self._read_file(collection)
        for row in rows:
            if str(row.get("id")) == str(item_id):
                row.update(updates)
                self._write_file(collection, rows)
                return row
        return None


storage = Storage()
