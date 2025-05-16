from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from config.config import config

class MongoDatabase:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(config.mongo_url)
            self.db = self.client[config.MONGO_DB]
            await self.client.admin.command('ping')
            print("✅ MongoDB connected")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            raise

    async def init_indexes(self):
        try:
            collection = self.db.reviews
            await collection.create_indexes([
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("rating", DESCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("is_approved", ASCENDING)])
            ])
            print("✅ MongoDB indexes created")
        except Exception as e:
            print(f"❌ MongoDB index creation error: {e}")
            raise
        
    def get_reviews_collection(self):
        return self.db.reviews

    async def save_review(self, review_data: dict):
        return await self.get_reviews_collection().insert_one(review_data)