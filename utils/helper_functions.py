import hashlib
import json
import base64

# File to store user data
USER_DATA_FILE = 'users.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

def authenticate_user(username, password):
    users = load_users()
    if username in users:
        hashed_password = hash_password(password)
        if users[username]['password'] == hashed_password:
            return True
    return False

def register_user(username, password):
    users = load_users()
    if username not in users:
        users[username] = {
            "password": hash_password(password)
        }
        save_users(users)
        return True
    return False

# Function to load and apply CSS to background image
def load_css(background_css_file_path, image_base64):
    with open(background_css_file_path, "r") as css_file:
        css_content = css_file.read()
    css_content = css_content.replace("{background_image_placeholder}", image_base64)
    return f"<style>{css_content}</style>"

# Function to encode an image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()