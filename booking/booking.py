from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response
import json

import resolvers as r

PORT = 3001
HOST = '0.0.0.0'
app = Flask(__name__)

# todo create elements for Ariadne

query = QueryType()

movie     = ObjectType('Movie')
movieDate = ObjectType('MovieDate')

query.set_field('create_booking', r.create_booking)
query.set_field('read_all_bookings', r.read_all_bookings)
query.set_field('delete_booking', r.delete_booking)
query.set_field('get_detailed_booking', r.get_detailed_booking)
query.set_field('get_booking_dates', r.get_booking_dates)

# root message

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
	bookings = json.load(jsf)["bookings"]

def write_bookings_to_file():
	with open('{}/databases/bookings.json'.format("."), "w") as jsf:
		json.dump({"bookings": bookings}, jsf, indent=4)
'''
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

def get_booking_data():
	req = request.get_json(silent=True)
	if not isinstance(req, dict):
		return None, ("malformed request body", 400)

	date = req.get("date")
	movies = req.get("movies")
	if not isinstance(date, str) or not date or not isinstance(movies, list) or not movies:
		return None, ("date and movies are required", 400)

	return (date, movies), None

def validate_schedule(date, movies):
	try:
		schedule_response = requests.get(
			"http://127.0.0.1:3202/schedule/{}".format(date),
			timeout=5
		)
	except requests.RequestException:
		return "schedule service unavailable", 503

	if schedule_response.status_code == 404:
		return "session not found", 404
	if schedule_response.status_code != 200:
		return "could not check session", 502

	scheduled_movies = schedule_response.json().get("movies", [])
	if any(movie_id not in scheduled_movies for movie_id in movies):
		return "movie is not scheduled for this session", 400

	return None

def save_booking(userid, date, movies):
	booking = next((item for item in bookings if item.get("userid") == userid), None)
	if booking is None:
		booking = {"userid": userid, "dates": []}
		bookings.append(booking)

	date_booking = next((item for item in booking["dates"] if item.get("date") == date), None)
	if date_booking is None:
		booking["dates"].append({"date": date, "movies": movies})
	else:
		date_booking["movies"] = list(dict.fromkeys(date_booking["movies"] + movies))

	write_bookings_to_file()

@app.route("/bookings/create-booking/<userid>", methods=['POST'])
def create_booking(userid):
	booking_data, error = get_booking_data()
	if error is not None:
		return make_response(jsonify({"error": error[0]}), error[1])

	date, movies = booking_data
	error = validate_schedule(date, movies)
	if error is not None:
		return make_response(jsonify({"error": error[0]}), error[1])

	save_booking(userid, date, movies)
	return make_response(jsonify({"message": "booking added"}), 200)

@app.route("/bookings/read-all-bookings", methods=['GET'])
def read_all_bookings():
   res = make_response(jsonify(bookings),200)
   return res

@app.route("/bookings/delete-booking/<booking_id>", methods=['DELETE'])
def delete_booking(booking_id):
	for booking in bookings:
		if str(booking["id"]) == str(booking_id):
			write_bookings_to_file()
			bookings.remove(booking)
			res = make_response(jsonify({"message":"booking deleted"}),200)
			return res

	res = make_response(jsonify({"error":"booking ID not found"}),500)
	return res

@app.route("/bookings/get-detailed-booking/<booking_id>", methods=['GET'])
def get_detailed_booking(booking_id):
	for booking in bookings:
		if str(booking["id"]) == str(booking_id):
			res = make_response(jsonify(booking),200)
			return res

	res = make_response(jsonify({"error":"booking ID not found"}),500)
	return res
'''

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
                        schema,
                        data,
                        context_value=None,
                        debug=app.debug
                    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)