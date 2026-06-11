import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/merchant_voice_pos")
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_database():
    client = get_client()
    database_name = os.getenv("MONGODB_DB", "merchant_voice_pos")
    return client[database_name]


def ensure_indexes(db) -> None:
    db.users.create_index("email", unique=True)
    db.inventory.create_index("name")
    db.inventory.create_index("displayName")
    db.inventory.create_index("aliases")
    db.voice_events.create_index("createdAt")
    db.orders.create_index("createdAt")


def seed_default_data(db, items) -> None:
    if db.inventory.count_documents({}) > 0:
        return

    now = datetime.now(timezone.utc)
    records = []
    for item in items:
        record = dict(item)
        record.setdefault("category", "general")
        record["createdAt"] = now
        record["updatedAt"] = now
        records.append(record)

    if records:
        db.inventory.insert_many(records)
