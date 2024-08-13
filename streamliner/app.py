import streamlit as st
import pandas as pd
import openai
import hashlib
import json
import os
import base64

# Read the OpenAI API key from a file
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Set your OpenAI API key
api_key_path = 'OpenAI_API_Key.txt'
if os.path.exists(api_key_path):
    openai.api_key = read_api_key(api_key_path)
else:
    raise ValueError(f"API key file not found: {api_key_path}")

# File to store user data
USER_DATA_FILE = 'users.json'

# Helper functions
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

# Initialize authentication state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Streamlit app
st.title("Streamliner AI")
st.subheader("Solution for big data challenges in your fingertips", divider="blue")

# Function to encode an image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Path to the local image
image_path = "dependencies/images/background.jpg"
base64_image = get_base64_image(image_path)

# CSS to set the background image and add black boundary to text boxes
background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{base64_image}");
        background-size: cover;
        color: black;
    }}

    </style>
"""

# Apply the CSS
st.markdown(background_css, unsafe_allow_html=True)

# Navigation menu
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Login":
    # Login form
    username = st.text_input("**Username**")
    password = st.text_input("**Password**", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.authentication_status = True
            st.session_state.current_user = username
            st.session_state.authenticated = True
            st.success("Login successful.")
        else:
            st.session_state.authentication_status = False
            st.error("Username/password is incorrect")

if menu == "Register":
    # Registration form
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    if st.button("Register"):
        if register_user(new_username, new_password):
            st.success("Registration successful! You can now log in.")
        else:
            st.error("Username already exists. Please choose a different username.")

# Main application
if st.session_state.authenticated:
    st.write(f"Welcome, {st.session_state.current_user}!")
    
    # Data upload
    uploaded_file = st.file_uploader("Upload your dataset (CSV file)", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset preview:", df.head())
        
        # Convert dataframe to CSV string
        csv_string = df.to_csv(index=False)

        # Natural Language Prompt
        prompt = st.text_area("Enter your data cleaning prompt")
        
        if st.button("Submit Prompt"):
            # Interact with OpenAI API
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Here is the dataset:\n{csv_string}\n\n{prompt}"}
                ]
            )
            st.write("Response:", response.choices[0].message.content.strip())
