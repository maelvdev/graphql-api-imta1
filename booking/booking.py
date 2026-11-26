from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify
import json

import resolvers as r

PORT = 3002
HOST = '0.0.0.0'
app = Flask(__name__)

type_defs = load_schema_from_path('booking.graphql')

query = QueryType()
mutation = MutationType()

booking = ObjectType('Booking')
movieDate = ObjectType('MovieDate')

# Queries
query.set_field('read_all_bookings', r.read_all_bookings)
query.set_field('get_detailed_booking', r.get_detailed_booking)
query.set_field('get_booking_dates_from_user', r.get_booking_dates_from_user)

# Mutations
mutation.set_field('create_booking', r.create_booking)
mutation.set_field('delete_booking', r.delete_booking)

schema = make_executable_schema(type_defs, query, mutation, booking, movieDate)

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
	print("Server running in port %s" % (PORT))
	app.run(host=HOST, port=PORT)