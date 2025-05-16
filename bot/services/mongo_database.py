from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from bot.config.config import config

class MongoDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(
            f"mongodb://{config.mongo_user}:{config.mongo_password.get_secret_value()}"
            f"@{config.mongo_host}:{config.mongo_port}/{config.mongo_db}"
        )
        self.db = self.client[config.mongo_db]
        self.reviews = self.db.reviews

    async def connect(self):
        try:
            await self.client.admin.command('ping')
            
            print("✅ MongoDB connected")
            
            await self.reviews.create_indexes([
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("created_at", ASCENDING)])
            ])
            
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")

    async def save_review(self, review_data: dict):
        return await self.reviews.insert_one(review_data)

    async def get_reviews(self, filter_query: dict = None):
        return await self.reviews.find(filter_query).to_list(None)