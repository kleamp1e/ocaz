import pymongo


def get_database(mongodb_url: str) -> pymongo.database.Database:
    return pymongo.MongoClient(mongodb_url).get_database()
