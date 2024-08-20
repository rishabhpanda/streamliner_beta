import streamlit as st
import pandas as pd
import openai
import os
import io
from utils.helper_functions import *
from utils.metadata import *

# Define paths
BACKGROUND_CSS_FILE_PATH = os.path.join("styles", "background.css")
BACKGROUND_IMAGE_PATH = os.path.join("utils", "images", "background.jpg")
OPENAI_LOGO_PATH = os.path.join("utils", "images", "openai-lockup.png")

# Convert images to base64 format
base64_image_background = get_base64_image(BACKGROUND_IMAGE_PATH)
base64_image_openai = get_base64_image(OPENAI_LOGO_PATH)

# Initialize session state for authentication
st.session_state.setdefault('authentication_status', None)
st.session_state.setdefault('authenticated', False)

# Load CSS files
css_files = ["styles/header_texts.css", "styles/buttons.css", "styles/openai_logo.css", "styles/sidebar_sections.css"]
for css_file in css_files:
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header and subtitle
st.markdown(
    """
    <h1 class="gradient-text">Streamliner AI (beta)</h1>
    <h3 class="custom-subtitle">How can I assist you with your data challenges?</h3>
    <hr class="custom-hr">
    """,
    unsafe_allow_html=True
)

# Apply background CSS if available
if os.path.exists(BACKGROUND_CSS_FILE_PATH):
    background_css = load_css(BACKGROUND_CSS_FILE_PATH, base64_image_background)
    st.markdown(background_css, unsafe_allow_html=True)
else:
    st.error(f"CSS file not found: {BACKGROUND_CSS_FILE_PATH}")

# Sidebar elements
st.sidebar.image("utils/images/bain_logo.png", use_column_width=True)

# Navigation menu
menu = st.sidebar.selectbox("**Login or Sign Up**", ["Login", "Register"])

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# Sidebar content
st.sidebar.markdown(
    f"""
    <a href="https://platform.openai.com/api-keys" target="_blank" style="text-decoration: none;">
        <div class="logo-container">
            <img src="data:image/png;base64,{base64_image_openai}">
        </div>
    </a>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.markdown(
    """
    <div class="sidebar-section-container">
        <h3>Product Documentation</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Login and registration forms
if menu == "Login":
    username = st.text_input("**Username**")
    password = st.text_input("**Password**", type="password")
    openai_api_key = st.text_input(
        "**OpenAI API Key**\n\n*If you do not have an API key, please click the OpenAI logo in the sidebar to generate one.*",
        type="password"
    )

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.update({
                'authentication_status': True,
                'authenticated': True,
                'current_user': username,
                'openai_api_key': openai_api_key
            })
            st.success("Login successful.")
        else:
            st.session_state.authentication_status = False
            st.error("Username/password is incorrect")

elif menu == "Register":
    new_username = st.text_input("**New Username**")
    new_password = st.text_input("**New Password**", type="password")

    if st.button("Register"):
        if register_user(new_username, new_password):
            st.success("Registration successful! You can now log in")
        else:
            st.error("Username already exists. Please choose a different username")

# Main application logic
if st.session_state.authenticated:
    openai.api_key = st.session_state.openai_api_key

    uploaded_file = st.file_uploader("Upload your dataset (CSV file)", type=["csv"])

    if uploaded_file:
        # Generate and display metadata
        metadata = generate_metadata(uploaded_file)
        display_metadata(metadata)

        # Reset the file pointer to the beginning
        uploaded_file.seek(0)

        # Now read the file again
        df = pd.read_csv(uploaded_file)
        st.write("Dataset preview:")

        # Applying alternating row colors
        styled_df = df.style.apply(
            lambda x: ['background-color: #efefef' if i % 2 == 0 else 'background-color: #ffffff' for i in range(len(x))], axis=0
        )
        st.dataframe(styled_df)

        csv_string = df.to_csv(index=False)

        prompt = st.text_area("Enter your data cleaning prompt")

        if st.button("Submit Prompt"):
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert data analyst specialized in cleaning, transforming, and preparing datasets for analysis. Your task is to understand user prompts and directly apply the necessary operations to clean and format datasets, ensuring data quality, consistency, and readiness for further analysis. You should return the cleaned or processed data as the final output, not the steps or code to achieve it."},
                    {"role": "user", "content": f"Here is the dataset:\n{csv_string}\n\n{prompt}"}
                ]
            )

            # Assuming the API now returns the processed dataset as a CSV string
            processed_csv_string = response.choices[0].message.content.strip()

            # Convert the processed CSV string back to a DataFrame using io.StringIO
            processed_df = pd.read_csv(io.StringIO(processed_csv_string))

            st.write("Processed Dataset:")
            st.dataframe(processed_df)

