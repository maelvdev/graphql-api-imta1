import json

def write_users(users):
    with open("./data/users.json", "w") as f:
        json.dump({"users": users}, f)

def load_users():
    with open("./data/users.json", "r") as f:
        return json.load(f)["users"]

def find_user(users, user_id):
    for user in users:
        if str(user["id"]) == str(user_id):
            return user
    return None
