from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["hotel_bot"]

users_collection = db["users"]
feedback_collection = db["feedback"]
