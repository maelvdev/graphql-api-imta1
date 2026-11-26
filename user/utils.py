import json
import os

from pymongo import MongoClient, ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://root:example@localhost:27017/")
SEED_FILE = "./data/users.json"

client = MongoClient(MONGO_URL)
db = client["users"]
collection = db["users"]

# on ne renvoie jamais le champ interne _id de Mongo
NO_ID = {"_id": 0}


def init_db():
    """Crée l'index unique sur id et remplit la collection depuis users.json si elle est vide."""
    collection.create_index([("id", ASCENDING)], unique=True)
    if collection.estimated_document_count() == 0:
        with open(SEED_FILE, "r") as f:
            users = json.load(f)["users"]
        if users:
            collection.insert_many(users)


def load_users():
    return list(collection.find({}, NO_ID))


def find_user(user_id):
    return collection.find_one({"id": str(user_id)}, NO_ID)


def insert_user(user):
    """Insère un utilisateur. Renvoie False si l'id existe déjà."""
    try:
        collection.insert_one(dict(user))
    except DuplicateKeyError:
        return False
    return True


def update_user_name(user_id, name):
    return collection.find_one_and_update(
        {"id": str(user_id)},
        {"$set": {"name": name}},
        projection=NO_ID,
        # renvoie le document après la MAJ de l'utilisateur
        return_document=ReturnDocument.AFTER,
    )


def delete_user(user_id):
    collection.delete_one({"id": str(user_id)})
