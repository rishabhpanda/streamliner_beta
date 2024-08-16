import streamlit as st
import pandas as pd
import openai
import os
from utils.helper_functions import *

# Define paths relative to the project directory
BACKGROUND_CSS_FILE_PATH = os.path.join("styles", "background.css")
BACKGROUND_IMAGE_PATH = os.path.join("utils", "images", "background.jpg")
OPENAI_LOGO_PATH = os.path.join("utils", "images", "openai-lockup.png")

# Convert the images to base64 format
base64_image_background = get_base64_image(BACKGROUND_IMAGE_PATH)
base64_image_openai = get_base64_image(OPENAI_LOGO_PATH)

# Initialize authentication state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Streamlit app
# Load the header text styles
with open("styles/header_texts.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the button styles
with open("styles/buttons.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the OpenAI Logo CSS file
with open("styles/openai_logo.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Use the header text classes defined in CSS
st.markdown(
    """
    <h1 class="gradient-text">
    Streamliner AI (beta)
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h3 class="custom-subtitle">
        How can I assist you with your big data challenges?
    </h3>
    <hr class="custom-hr">
    """,
    unsafe_allow_html=True
)

# Load and apply the background CSS
if os.path.exists(BACKGROUND_CSS_FILE_PATH):
    background_css = load_css(BACKGROUND_CSS_FILE_PATH, base64_image_background)
    st.markdown(background_css, unsafe_allow_html=True)
else:
    st.error(f"CSS file not found: {BACKGROUND_CSS_FILE_PATH}")

# Display the logo at the top of the sidebar
st.sidebar.image("utils/images/bain_logo.png", use_column_width=True)

# Display the OpenAI logo
st.sidebar.markdown(
    f"""
    <div class="logo-container">
        <a href="https://platform.openai.com/api-keys" target="_blank">
            <img src="data:image/png;base64,{base64_image_openai}">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Add some space
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# Navigation menu
menu = st.sidebar.selectbox("**Login or Sign Up**", ["Login", "Register"])

if menu == "Login":
    # Login form
    username = st.text_input("**Username**")
    password = st.text_input("**Password**", type="password")
    openai_api_key = st.text_input(
        "**OpenAI API Key**\n\n*(If you do not have an API key, please click the OpenAI logo in the sidebar to generate one.)*",
        type="password"
    )
    
    # Button logic with input validation
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.authentication_status = True
            st.session_state.current_user = username
            st.session_state.authenticated = True
            st.session_state.openai_api_key = openai_api_key  # Store the API key in session state
            st.success("Login successful.")
        else:
            st.session_state.authentication_status = False
            st.error("Username/password is incorrect")

if menu == "Register":
    # Registration form
    new_username = st.text_input("**New Username**")
    new_password = st.text_input("**New Password**", type="password")
    if st.button("Register"):
        if register_user(new_username, new_password):
            st.success("Registration successful! You can now log in")
        else:
            st.error("Username already exists. Please choose a different username")

# Main application
if st.session_state.authenticated:
    # Set the OpenAI API key
    openai.api_key = st.session_state.openai_api_key
    
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
                    {"role": "system", "content": "Act as a data expert in terms of analyzing .CSV and .XLSX files."},
                    {"role": "user", "content": f"Here is the dataset:\n{csv_string}\n\n{prompt}"}
                ]
            )
            st.write("Response:", response.choices[0].message.content.strip())