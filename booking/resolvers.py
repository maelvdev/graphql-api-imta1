import json

from flask import jsonify, request, make_response
import requests


def write_bookings_to_file():
    with open('{}/databases/bookings.json'.format("."), "w") as jsf:
        json.dump({"bookings": bookings}, jsf, indent=4)

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


# à changer quand user sera complété
def verify_user_role(_, info, _userid):
	return True

def create_booking(_,info,_userid):
	with open('{}/data/bookings.json'.format("."), "r") as file:
		''''''
		booking_data, error = get_booking_data()
		if error is not None:
			return make_response(jsonify({"error": error[0]}), error[1])

		date, movies = booking_data
		error = validate_schedule(date, movies)
		if error is not None:
			return make_response(jsonify({"error": error[0]}), error[1])

		save_booking(userid, date, movies)
		return make_response(jsonify({"message": "booking added"}), 200)
		''''''
		bookings = json.load(file)
		for booking in bookings['bookings']:
			if booking['userid'] == _userid:
				return booking

def read_all_bookings(_,info, _userid):
	verify_user_role(_, info, _userid)
	with open('{}/data/bookings.json'.format("."), "r") as file:
		bookings = json.load(file)
		return bookings['bookings']

def delete_booking(_,info, _userid, _movieid):
	with open('{}/data/bookings.json'.format("."), "r") as file:
		bookings = json.load(file)
		for booking in bookings['bookings']:
			if booking['userid'] == _userid:
				for date in booking['dates']:
					if _movieid in date['movies']:
						date['movies'].remove(_movieid)
						with open('{}/data/bookings.json'.format("."), "w") as file:
							json.dump(bookings, file, indent=4)
						return True
	return False

def get_detailed_booking(_,info, _userid, _bookingid):
	with open('{}/data/bookings.json'.format("."), "r") as file:
		bookings = json.load(file)
		for booking in bookings['bookings']:
			if booking['userid'] == _userid:
				for date in booking['dates']:
					if str(date['id']) == str(_bookingid):
						return date
	return None

def get_booking_dates_from_user(_,info, _userid):
	with open('{}/data/bookings.json'.format("."), "r") as file:
		bookings = json.load(file)
		for booking in bookings['bookings']:
			if booking['userid'] == _userid:
				return booking['dates']
	return []