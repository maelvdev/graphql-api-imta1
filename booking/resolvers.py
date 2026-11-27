from flask import jsonify, request, make_response

import json
import requests

DATA_FILE = './data/bookings.json'

def load_bookings():
	with open(DATA_FILE, "r") as jsf:
		return json.load(jsf)["bookings"]

def write_bookings_to_file(bookings_list):
	with open(DATA_FILE, "w") as jsf:
		json.dump({"bookings": bookings_list}, jsf, indent=4)

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
			f"http://127.0.0.1:3202/schedule/{date}",
			timeout=5
		)
	except requests.RequestException:
		raise Exception("Schedule service unavailable")

	if schedule_response.status_code == 404:
		raise Exception("Session not found")
	if schedule_response.status_code != 200:
		raise Exception("Could not check session")

	scheduled_movies = schedule_response.json().get("movies", [])
	if any(movie_id not in scheduled_movies for movie_id in movies):
		raise Exception("Movie is not scheduled for this session")

def verify_user_role(_, info, _userid):
	try:
		user_response = requests.get(
			f"http://127.0.0.1:3004/users/{_userid}",
			timeout=5
		)
	except requests.RequestException:
		raise Exception("User service unavailable")

	if user_response.status_code == 404:
		raise Exception("User not found")
	if user_response.status_code != 200:
		raise Exception("Could not check user")

	user = user_response.json()
	if not isinstance(user, dict) or user.get("role") != "admin":
		raise Exception("User is not admin")
	return True

def create_booking(_, info, _userid, _date, _movie):
	validate_schedule(_date, [_movie])
	bookings_list = load_bookings()

	booking = next((item for item in bookings_list if item.get("userid") == _userid), None)
	if booking is None:
		booking = {"userid": _userid, "dates": []}
		bookings_list.append(booking)

	date_booking = next((item for item in booking["dates"] if item.get("date") == _date), None)
	if date_booking is None:
		booking["dates"].append({"date": _date, "movies": [_movie]})
	else:
		if _movie not in date_booking["movies"]:
			date_booking["movies"].append(_movie)

	write_bookings_to_file(bookings_list)
	return booking

def read_all_bookings(_, info, _userid):
	verify_user_role(_, info, _userid)
	return load_bookings()

def delete_booking(_, info, _userid, _movie_id):
	bookings_list = load_bookings()
	for booking in bookings_list:
		if booking['userid'] == _userid:
			for date_entry in booking['dates']:
				if _movie_id in date_entry['movies']:
					date_entry['movies'].remove(_movie_id)
					write_bookings_to_file(bookings_list)
					return True
	return False

def get_detailed_booking(_, info, _userid, _date):
	bookings_list = load_bookings()
	for booking in bookings_list:
		if booking['userid'] == _userid:
			for date_entry in booking['dates']:
				if str(date_entry['date']) == str(_date):
					return date_entry
	return None

def get_booking_dates_from_user(_, info, _userid):
	bookings_list = load_bookings()
	for booking in bookings_list:
		if booking['userid'] == _userid:
			return booking['dates']
	return []