import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("MONGO_DB", "wishlistdb")

_client = None
_db = None

async def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client[DB_NAME]
        # índices útiles
        await _db.cities.create_index([("ciudad_lc", 1), ("pais", 1)])
        await _db.wishes.create_index("user_id")
    return _db
