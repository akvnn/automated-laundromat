from flask import Flask, request, jsonify, session, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import os
app = Flask(__name__)
app.secret_key = 'some_secret_key'
# MongoDB setup
uri = os.environ.get('MONGODB_URI')
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client['laundromat']
users = db['users']
machines = db['machines']
bookings = db['bookings']
# End of MongoDB setup

# Helper Functions


def check_availability(machine_id, start_time, end_time):
    """ Check if the machine is available between the given times """
    conflicts = bookings.find_one({
        'machineId': ObjectId(machine_id),
        'start': {'$lt': end_time},
        'end': {'$gt': start_time}
    })
    return conflicts is None

# API Endpoints


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/machines', methods=['GET'])
def machines_html():
    return render_template('machines.html')


@app.route('/login', methods=['GET'])
@app.route('/signup', methods=['GET'])
def login_html():
    return render_template('login.html')


@app.route('/bookings/<machine_type>/<machine_id>/<machine_name>', methods=['GET'])
def bookings_html(machine_type, machine_id, machine_name):
    return render_template('bookings.html')


@app.route('/payment', methods=['GET'])
def payment_html():
    return render_template('payment.html')


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json

    # Check if the email is already in use
    existing_user = users.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'message': 'Email already in use'}), 409

    hashed_password = bcrypt.hashpw(
        data['password'], bcrypt.gensalt())
    user_id = users.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password
    }).inserted_id
    return jsonify({'user_id': str(user_id)}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print(data)
    try:
        user = users.find_one({'email': data['email']})
        if user and bcrypt.hashpw(data['password'], user['password']):
            session['user_id'] = str(user['_id'])
            return jsonify({'message': 'Login successful'}), 200
    except Exception as e:
        print(e)
    return jsonify({'message': 'Unauthorized'}), 401


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'}), 200


@app.route('/machineBookings', methods=['POST'])
def machine_bookings():
    data = request.json
    machine_id = data['machineId']
    bookings_this_week = bookings.find({
        'machineId': ObjectId(machine_id),
        'start': {'$gte': datetime.now() - timedelta(days=datetime.now().weekday() + 1),
                  '$lt': datetime.now() + timedelta(days=7 - datetime.now().weekday())}
    })
    result = []
    for booking in bookings_this_week:
        booking_data = {
            'booking_id': str(booking['_id']),
            'userId': str(booking['userId']),
            'start': booking['start'].strftime('%Y-%m-%d %H:%M'),
            'end': booking['end'].strftime('%Y-%m-%d %H:%M'),
            'title': booking['title']
        }
        result.append(booking_data)
    return jsonify(result)


@app.route('/getMachines', methods=['GET'])
def get_machines():
    all_machines = machines.find({})
    result = {'washers': [], 'dryers': []}
    for machine in all_machines:
        machine_data = {
            'id': str(machine['_id']),
            'status': machine['status'],
            'type': machine['type'],
            'name': machine['name']  # added
        }
        if machine['type'] == 'washer':
            result['washers'].append(machine_data)
        elif machine['type'] == 'dryer':
            result['dryers'].append(machine_data)
    return jsonify(result)


@app.route('/bookMachine', methods=['POST'])
def book_machine():
    data = request.json
    user_id = data['userId']  # later change to use jwt
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    start_time = datetime.strptime(data['start'][:19], '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(data['end'][:19], '%Y-%m-%dT%H:%M:%S')
    # end_time = start_time + timedelta(minutes=30 * data['cycles']) # not needed

   # if data['cycles'] > 2: # handled in frontend, can keep by calcuating the cycles from the time
   #     return jsonify({'message': 'Cannot book more than 2 cycles'}), 400

    if check_availability(data['machineId'], start_time, end_time):
        booking_id = bookings.insert_one({
            'machineId': ObjectId(data['machineId']),
            'userId': ObjectId(user_id),
            'start': start_time,
            'end': end_time,
            'title': data['title']
        }).inserted_id
        return jsonify({'booking_id': str(booking_id)}), 200
    return jsonify({'message': 'Machine not available'}), 409


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080, threads=100)
