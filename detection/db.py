from django.conf import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]
detections_collection = db[settings.MONGODB_COLLECTION]
