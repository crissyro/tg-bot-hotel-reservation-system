from motor.motor_asyncio import AsyncIOMotorClient
from config import config

client = AsyncIOMotorClient(
    f"mongodb://{config.mongo_user}:{config.mongo_password.get_secret_value()}"
    f"@{config.mongo_host}:{config.mongo_port}"
)
db = client[config.mongo_db]
feedback_collection = db["feedback"]