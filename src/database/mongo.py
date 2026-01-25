from pymongo import AsyncMongoClient
from src.core.config import settings

class MongoDB:
    client: AsyncMongoClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncMongoClient(settings.MONGODB_URI)
    print("Connected to MongoDB")

async def close_mongo_connection():
    await mongodb.client.close()
    print("Closed MongoDB connection")

def get_database():
    return mongodb.client[settings.DATABASE_NAME]

def get_users_collection():
    db = get_database()
    return db["users"]

def get_farmers_collection():
    db = get_database()
    return db["farmers"]

def get_recommendations_collection():
    db = get_database()
    return db["recommendations"]

def get_market_weather_collection():
    db = get_database()
    return db["market_weather"]
