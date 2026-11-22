from flask import Flask, request, jsonify, make_response
import time

from utils import load_users, write_users, find_user

PORT = 3004
HOST = '0.0.0.0'
app = Flask(__name__)

ROLES = ("user", "admin")

def error_response(message, code):
    return make_response(jsonify({"error": message}), code)

@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_users():
    return make_response(jsonify(load_users()), 200)

@app.route("/users/<user_id>", methods=['GET'])
def get_user(user_id):
    user = find_user(load_users(), user_id)
    if user is None:
        return error_response("user ID not found", 404)
    return make_response(jsonify(user), 200)

# body: { "name": "...", "role": "user" | "admin" }
@app.route("/users/<user_id>", methods=['POST'])
def add_user(user_id):
    req = request.get_json(silent=True) or {}
    if not req.get("name") or req.get("role") not in ROLES:
        return error_response("malformed user body", 400)
    if "id" in req and str(req["id"]) != str(user_id):
        return error_response("body id does not match URL id", 400)

    users = load_users()
    if find_user(users, user_id) is not None:
        return error_response("user already exists", 409)

    user = {
        "id": user_id,
        "name": req["name"],
        "role": req["role"],
        "last_active": req.get("last_active", int(time.time())),
    }
    users.append(user)
    write_users(users)
    return make_response(jsonify(user), 201)

# body: { "name": "..." }
@app.route("/users/<user_id>", methods=['PUT'])
def update_user(user_id):
    req = request.get_json(silent=True) or {}
    if not req.get("name"):
        return error_response("name is required", 400)

    users = load_users()
    user = find_user(users, user_id)
    if user is None:
        return error_response("user ID not found", 404)

    user["name"] = req["name"]
    write_users(users)
    return make_response(jsonify(user), 200)

@app.route("/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    users = load_users()
    user = find_user(users, user_id)
    if user is None:
        return error_response("user ID not found", 404)
    if user.get("role") != "user":
        return error_response("cannot delete an admin", 403)

    users.remove(user)
    write_users(users)
    return make_response(jsonify(user), 200)

# 200 if admin, 403 if not, 404 if unknown
@app.route("/users/<user_id>/admin", methods=['GET'])
def is_admin(user_id):
    user = find_user(load_users(), user_id)
    if user is None:
        return error_response("user ID not found", 404)
    if user.get("role") != "admin":
        return error_response("user is not admin", 403)
    return make_response(jsonify({"message": "user is admin"}), 200)

if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
