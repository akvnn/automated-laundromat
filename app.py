from dotenv import load_dotenv
from flask import Flask, request, jsonify, session, render_template, flash, redirect
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import os
import stripePayment
from flask_session import Session

# constants
MAX_CYCLES = 2

load_dotenv('.env')

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

# Flask session setup
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = client
app.config['SESSION_MONGODB_DB'] = 'laundromat'
app.config['SESSION_MONGODB_COLLECTION'] = 'sessions'
Session(app)

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


@app.route('/bookings_history', methods=['GET'])
def bookings_history_html():
    return render_template('bookings_history.html')


@app.route('/bookings/<machine_type>/<machine_id>/<machine_name>', methods=['GET'])
def bookings_html(machine_type, machine_id, machine_name):
    return render_template('bookings.html')


@app.route('/bookingConfirmation/<booking_id>', methods=['GET'])
def booking_confirmation_html(booking_id):
    return render_template('booking_confirmation.html')


@app.route('/payment', methods=['GET'])
def payment_html():
    return render_template('payment.html')


@app.route('/payment', methods=['POST'])
def start_payment():
    # call stripe function if selected payment method is card
    url = stripePayment.create_checkout_session()
    return jsonify({'redirectUrl': str(url)}), 200


@app.route('/cancel')
def paymentCancel():
    return render_template('cancel.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('login.html')
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
        'password': hashed_password,
        'role': 'user' if not 'admin' in data['name'] else 'admin'
    }).inserted_id
    session['user_id'] = str(user_id)
    return jsonify({'user_id': str(user_id)}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    data = request.json
    print(data)
    try:
        user = users.find_one({'email': data['email']})
        if user and bcrypt.hashpw(data['password'], user['password']):
            session['user_id'] = str(user['_id'])
            return jsonify({'message': 'Login successful', 'user_id': str(user['_id']), 'user_name': user['name'], 'user_email': user['email']}), 200
    except Exception as e:
        print(e)
    return jsonify({'message': 'Unauthorized'}), 401


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfuly')
    return redirect('/')


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


@app.route('/machineInfo', methods=['POST'])
def machine_info():
    data = request.json
    machine_id = data['machineId']
    machine = machines.find_one({'_id': ObjectId(machine_id)})
    machine_data = {
        'id': str(machine['_id']),
        'status': machine['status'],
        'type': machine['type'],
        'name': machine['name']
    }
    return jsonify(machine_data)


@app.route('/setMachineStatus', methods=['POST'])
def set_machine_status():
    data = request.json
    machine_id = data['machineId']
    status = data['status']
    machines.update_one({'_id': ObjectId(machine_id)}, {
                        '$set': {'status': status}})
    return jsonify({'message': 'Status updated'}), 200


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


@app.route('/getBookings', methods=['GET'])
def get_bookings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    all_bookings = bookings.find({'userId': ObjectId(user_id)})
    result = []
    for booking in all_bookings:
        booking_data = {
            'booking_id': str(booking['_id']),
            'machineId': str(booking['machineId']),
            'machineName': machines.find_one({'_id': booking['machineId']})['name'],
            'cycles': booking['cycles'],
            'machineType': machines.find_one({'_id': booking['machineId']})['type'],
            'start': booking['start'].strftime('%Y-%m-%d %H:%M'),
            'end': booking['end'].strftime('%Y-%m-%d %H:%M'),
            'title': booking['title'],
            'status': booking['status'],
            'paymentMethod': booking['paymentMethod']
        }
        result.append(booking_data)
    # sort latest to oldest
    result.sort(key=lambda x: x['start'], reverse=True)
    return jsonify(result)


@app.route('/getBooking/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    if not ObjectId.is_valid(booking_id):
        return jsonify({'message': 'Invalid booking id'}), 400
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    booking = bookings.find_one(
        {'_id': ObjectId(booking_id), 'userId': ObjectId(user_id)})
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    booking_data = {
        'machineName': machines.find_one({'_id': booking['machineId']})['name'],
        'cycles': booking['cycles'],
        'machineType': machines.find_one({'_id': booking['machineId']})['type'],
        'start': booking['start'].strftime('%Y-%m-%d %H:%M'),
        'end': booking['end'].strftime('%Y-%m-%d %H:%M'),
        'status': booking['status'],
        'paymentMethod': booking['paymentMethod']
    }
    return jsonify(booking_data)


@app.route('/userData', methods=['GET'])
def get_user_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    user = users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'name': user['name'], 'email': user['email']})


@app.route('/bookMachine', methods=['POST'])
def book_machine():
    data = request.json
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to book a machine')
        return jsonify({'message': 'Unauthorized'}), 401

    start_time = datetime.strptime(data['start'][:19], '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(data['end'][:19], '%Y-%m-%dT%H:%M:%S')

    if start_time < datetime.now():
        flash('Cannot book in the past')
        return jsonify({'message': 'Cannot book in the past'}), 400

    if end_time > start_time + timedelta(minutes=30 * MAX_CYCLES):
        flash('Cannot book more than 2 cycles')
        return jsonify({'message': 'Cannot book more than 2 cycles'}), 400

    if check_availability(data['machineId'], start_time, end_time):
        booking_id = bookings.insert_one({
            'machineId': ObjectId(data['machineId']),
            'userId': ObjectId(user_id),
            'start': start_time,
            'end': end_time,
            'title': data['title'],
            'cycles': data['cycles'],
            'status': data['status'],
            'paymentMethod': data['paymentMethod']
        }).inserted_id
        return jsonify({'booking_id': str(booking_id)}), 200
    return jsonify({'message': 'Machine not available'}), 409


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=8080)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080, threads=100)
