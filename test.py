from pymongo import MongoClient
from datetime import datetime, timedelta
import bcrypt

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['laundromat']
users = db['users']
machines = db['machines']
bookings = db['bookings']

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
    {"type": "washer", "status": "available", "bookedSlots": []},
    {"type": "dryer", "status": "available", "bookedSlots": []}
])

# Insert a pre-existing booking (optional)
start_time = datetime.now() + timedelta(hours=1)
end_time = start_time + timedelta(minutes=30)
bookings.insert_one({
    "machineId": machines.find_one({'type': 'washer'})['_id'],
    "userId": users.find_one({'email': 'alice@example.com'})['_id'],
    "start": start_time,
    "end": end_time
})

import requests

base_url = "http://127.0.0.1:5000"  # Adjust if your Flask app is hosted elsewhere

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
machines_response = requests.get(f"{base_url}/availableMachines")
print("Available Machines:", machines_response.json())

# Book a machine
machine_id = machines.find_one({'type': 'washer'})['_id']
book_machine_response = requests.post(f"{base_url}/bookMachine", json={
    "machineId": str(machine_id),
    "dateTime": (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
    "cycles": 1
}, cookies=login_response.cookies)  # Use cookies for session management
print("Book Machine Response:", book_machine_response.json())

# Book a machine (overlap)
machine_id = machines.find_one({'type': 'washer'})['_id']
book_machine_response = requests.post(f"{base_url}/bookMachine", json={
    "machineId": str(machine_id),
    "dateTime": (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
    "cycles": 1
}, cookies=login_response.cookies)  # Use cookies for session management
print("Book Machine Response:", book_machine_response.json())

# get machine bookings
machine_id = machines.find_one({'type': 'washer'})['_id']
machine_bookings_response = requests.post(f"{base_url}/machineBookings", json={
    "machineId": str(machine_id)
})
print("Machine Bookings:", machine_bookings_response.json())

# Logout
logout_response = requests.get(f"{base_url}/logout", cookies=login_response.cookies)
print("Logout Response:", logout_response.json())
