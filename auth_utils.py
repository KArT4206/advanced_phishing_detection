import pyrebase
from firebase_config import firebase_config
from getmac import get_mac_address
import requests

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

def get_client_ip():
    return requests.get('https://api.ipify.org').text

def get_mac():
    return get_mac_address()

def store_login_info(email, ip, mac, password=None):
    data = {
        "email": email,
        "ip": ip,
        "mac": mac
    }
    # For development/debugging only
    if password is not None:
        data["password"] = password
    
    db.child("login_info").push(data)
