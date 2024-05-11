import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import bcrypt
import os
from dotenv import load_dotenv
load_dotenv('.env')
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

# Clear existing data
users.drop()
machines.drop()
bookings.drop()

# Insert sample users
password = bcrypt.hashpw("password123", bcrypt.gensalt())
users.insert_many([
    {"name": "Alice", "email": "alice@example.com", "password": password},
    {"name": "Bob", "email": "bob@example.com", "password": password}
])

# Insert sample machines
machines.insert_many([
    {"type": "washer", "status": "available", "bookedSlots": [], "name": "1", "status": "locked"},
    {"type": "dryer", "status": "available", "bookedSlots": [], "name": "2", "status": "locked"}
])

# Insert a pre-existing booking (optional)
start_time = datetime.now() + timedelta(hours=1)
end_time = start_time + timedelta(minutes=30)
bookings.insert_one({
    "title": "Some booking",
    "machineId": machines.find_one({'type': 'washer'})['_id'],
    "userId": users.find_one({'email': 'alice@example.com'})['_id'],
    "start": start_time,
    "end": end_time
})


base_url = "http://127.0.0.1:8080"  # Adjust if your Flask app is hosted elsewhere

# Sign up a new user
signup_response = requests.post(f"{base_url}/signup", json={
    "name": "Charlie",
    "email": "charlie@example.com",
    "password": "securepass123"
})
print("Signup Response:", signup_response.json())

# Login
login_response = requests.post(f"{base_url}/login", json={
    "email": "charlie@example.com",
    "password": "securepass123"
})
print("Login Response:", login_response.json())

# Get available machines
machines_response = requests.get(f"{base_url}/getMachines")
print("Available Machines:", machines_response.json())

# Book a machine
machine_id = machines.find_one({'type': 'washer'})['_id']
book_machine_response = requests.post(f"{base_url}/bookMachine", json={
    "machineId": str(machine_id),
    "start": (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S'),
    "end": (datetime.now() + timedelta(hours=2.5)).strftime('%Y-%m-%dT%H:%M:%S'),
    "cycles": 1,
    "userId": str(users.find_one({'email': 'charlie@example.com'})['_id']),
    "title": "test booking"
}, cookies=login_response.cookies)  # Use cookies for session management
print("Book Machine Response:", book_machine_response.json())

# Book a machine (overlap)
machine_id = machines.find_one({'type': 'washer'})['_id']
book_machine_response = requests.post(f"{base_url}/bookMachine", json={
    "machineId": str(machine_id),
    "start": (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S'),
    "end": (datetime.now() + timedelta(hours=2.5)).strftime('%Y-%m-%dT%H:%M:%S'),
    "cycles": 1,
    "userId": str(users.find_one({'email': 'charlie@example.com'})['_id']),
    "title": "test booking"
}, cookies=login_response.cookies)  # Use cookies for session management
print("Book Machine Response:", book_machine_response.json())

# get machine bookings
machine_id = machines.find_one({'type': 'washer'})['_id']
machine_bookings_response = requests.post(f"{base_url}/machineBookings", json={
    "machineId": str(machine_id)
})
print("Machine Bookings:", machine_bookings_response.json())

# Logout
logout_response = requests.get(
    f"{base_url}/logout", cookies=login_response.cookies)
print("Logout Response:", logout_response.json())
