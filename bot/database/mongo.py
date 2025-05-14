from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import config

import logging


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                host=config.mongo_host,
                port=config.mongo_port,
                username=config.mongo_user,
                password=config.mongo_password.get_secret_value(),
                authSource="admin"
            )
            self.db = self.client[config.mongo_db]
            
            await self.client.admin.command('ping')
            logging.info("Successfully connected to MongoDB!")
            
        except ConnectionFailure as e:
            logging.error(f"MongoDB connection error: {e}")
            raise

    async def close(self):
        if self.client:
            await self.client.close()
            logging.info("MongoDB connection closed.")


mongo = MongoDB()

async def get_reviews_collection():
    await mongo.connect()
    return mongo.db.reviews

async def get_users_collection():
    await mongo.connect()
    return mongo.db.users