from flask import Flask, request, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Use a proper secret key in production

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['laundromat']
users = db['users']
machines = db['machines']
bookings = db['bookings']

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
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = bcrypt.hashpw(data['password'], bcrypt.gensalt())
    user_id = users.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password
    }).inserted_id
    return jsonify({'user_id': str(user_id)}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users.find_one({'email': data['email']})
    if user and bcrypt.hashpw(data['password'], user['password']):
        session['user_id'] = str(user['_id'])
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Unauthorized'}), 401

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'}), 200

@app.route('/availableMachines', methods=['GET'])
def available_machines():
    all_machines = machines.find({})
    result = {'washers': [], 'dryers': []}
    for machine in all_machines:
        machine_data = {
            'id': str(machine['_id']),
            'status': machine['status'],
            'bookedSlots': [[slot['start'].strftime('%Y-%m-%d %H:%M'), slot['end'].strftime('%Y-%m-%d %H:%M')] for slot in machine['bookedSlots']]
        }
        if machine['type'] == 'washer':
            result['washers'].append(machine_data)
        elif machine['type'] == 'dryer':
            result['dryers'].append(machine_data)
    return jsonify(result)

@app.route('/bookMachine', methods=['POST'])
def book_machine():
    data = request.json
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    start_time = datetime.strptime(data['dateTime'], '%Y-%m-%d %H:%M')
    end_time = start_time + timedelta(minutes=30 * data['cycles'])

    if data['cycles'] > 2:
        return jsonify({'message': 'Cannot book more than 2 cycles'}), 400

    if check_availability(data['machineId'], start_time, end_time):
        booking_id = bookings.insert_one({
            'machineId': ObjectId(data['machineId']),
            'userId': ObjectId(user_id),
            'start': start_time,
            'end': end_time
        }).inserted_id
        return jsonify({'booking_id': str(booking_id)}), 200
    return jsonify({'message': 'Machine not available'}), 409