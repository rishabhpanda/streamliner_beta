import streamlit as st
import pandas as pd
import openai
import os
from utils.helper_functions import *
    
# Path to the local background image
image_path = "dependencies/images/background.jpg"
base64_image_background = get_base64_image(image_path)

# Get the base64 string of the OpenAI logo
base64_image_openai = get_base64_image("dependencies/images/openai-lockup.png")

# Path to the background CSS file
background_css_file_path = "styles/background.css"

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
if os.path.exists(background_css_file_path):
    background_css = load_css(background_css_file_path, base64_image_background)
    st.markdown(background_css, unsafe_allow_html=True)
else:
    st.error(f"CSS file not found: {background_css_file_path}")

# Display the logo at the top of the sidebar
st.sidebar.image("dependencies/images/bain_logo.png", use_column_width=True)

# Navigation menu
menu = st.sidebar.selectbox("**Login or Sign Up**", ["Login", "Register"])

# Display the OpenAI logo below the dropdown
# Add some space before the image
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Display the image with a rectangular border and within the box
st.sidebar.markdown(
    f"""
    <div style="border: 3px solid rgb(255,255,255); 
    padding: 10px; 
    width: 100%; 
    margin: auto; 
    text-align: center;
    background-color: white;
    border-radius: 10px;">
        <a href="https://platform.openai.com/api-keys" target="_blank">
            <img src="data:image/png;base64,{base64_image_openai}" width="150">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

if menu == "Login":
    # Login form
    username = st.text_input("**Username**")
    password = st.text_input("**Password**", type="password")
    openai_api_key = st.text_input("**OpenAI API Key**", type="password")
    
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