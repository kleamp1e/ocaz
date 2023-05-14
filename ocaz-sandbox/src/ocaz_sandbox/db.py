import pymongo

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"


def get_database(mongodb_url: str) -> pymongo.database.Database:
    return pymongo.MongoClient(mongodb_url).get_database()
