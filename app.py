import streamlit as st
import pandas as pd
from tabulate import tabulate
import openai
import os
import io
from utils.helper_functions import *
from utils.metadata import *

# Define paths
BACKGROUND_CSS_FILE_PATH = os.path.join("styles", "background.css")
BACKGROUND_IMAGE_PATH = os.path.join("utils", "images", "background.jpg")
OPENAI_LOGO_PATH = os.path.join("utils", "images", "openai-lockup.png")
SQL_SERVER_LOGO_PATH = os.path.join("utils", "images", "sql_server_logo.png")
APACHE_SPARK_LOGO_PATH = os.path.join("utils", "images", "apache_spark_logo.png")

# Convert images to base64 format
base64_image_background = get_base64_image(BACKGROUND_IMAGE_PATH)
base64_image_openai = get_base64_image(OPENAI_LOGO_PATH)
base64_image_sql_server = get_base64_image(SQL_SERVER_LOGO_PATH)
base64_image_apache_spark = get_base64_image(APACHE_SPARK_LOGO_PATH)

# Initialize session state for authentication and data
st.session_state.setdefault('authentication_status', None)
st.session_state.setdefault('authenticated', False)
st.session_state.setdefault('metadata', None)
st.session_state.setdefault('df', None)
st.session_state.setdefault('processed_df', None)

# Load CSS files
css_files = ["styles/header_texts.css", "styles/buttons.css", "styles/logo.css", "styles/sidebar_sections.css"]
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
st.sidebar.image("utils/images/bain_logo.png", width=340)

# Navigation menu
menu = st.sidebar.selectbox("**Login or Sign Up**", ["Login", "Register"])

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)

# Sidebar content
st.sidebar.markdown(
    f"""
    <a href="https://platform.openai.com/api-keys" target="_blank" style="text-decoration: none;">
        <div class="logo-container-openai">
            <img src="data:image/png;base64,{base64_image_openai}">
        </div>
    </a>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Documentation and user guide button
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

# Main application
if st.session_state.authenticated:
    openai.api_key = st.session_state.openai_api_key

    data_source = st.radio("**Select data source**", ["Upload CSV", "Fetch from SQL Server"])

    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("**Upload your dataset (CSV file)**", type=["csv"])

        if uploaded_file:
            # Generate and display metadata for the uploaded file
            metadata = generate_metadata(uploaded_file)
            st.session_state['metadata'] = metadata  # Store metadata in session state
            uploaded_file.seek(0)  # Rewind the file pointer to the beginning
            st.session_state.df = pd.read_csv(uploaded_file)  # Store the DataFrame in session state

    elif data_source == "Fetch from SQL Server":
        # Input fields for SQL Server credentials
        server = st.text_input("**Server**", key="sql_server")
        database = st.text_input("**Database**", key="database")
        user_id = st.text_input("**User ID** (Please enter your work email)", key="user_id")
        password = st.text_input("**Password** (Please enter your system password)", type="password", key="password")

        query = st.text_area("**Enter SQL query to retrieve data**")

        if st.button("Fetch Data"):
            try:
                # Pass the credentials and query to the fetch function
                df = fetch_data_from_sql(query, server, database, user_id, password)
                st.success("Data fetched successfully.")

                # Convert the DataFrame to a CSV string for further processing
                csv_string = df.to_csv(index=False)

                # Since this is SQL data, we create an in-memory buffer
                csv_buffer = io.StringIO(csv_string)
                csv_buffer.seek(0)  # Rewind the buffer

                # Generate and display metadata for the fetched data
                metadata = generate_metadata(csv_buffer)
                st.session_state['metadata'] = metadata  # Store metadata in session state
                st.session_state.df = df  # Store the DataFrame in session state

            except Exception as e:
                st.error(f"Error fetching data: {e}")

    # Retrieve and display metadata if it exists in session state
    if st.session_state.metadata:
        display_metadata(st.session_state['metadata'])  # Display metadata

    # If df is not None (i.e., data has been loaded either via upload or SQL fetch)
    if st.session_state.df is not None:
        st.markdown("#### Dataset Preview:")
        styled_df = st.session_state.df.style.apply(
            lambda x: ['background-color: #efefef' if i % 2 == 0 else 'background-color: #ffffff' for i in range(len(x))], axis=0
        )
        st.dataframe(styled_df)

        csv_string = st.session_state.df.to_csv(index=False)
        prompt = st.text_area("**Enter your data cleaning prompt**")

        if st.button("Submit Prompt"):
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert data analyst specialized in cleaning, transforming, and preparing datasets for analysis. Your task is to understand user prompts and directly apply the necessary operations to clean and format datasets, ensuring data quality, consistency, and readiness for further analysis. You should return the cleaned or processed data strictly in CSV format, without any additional text, descriptions, or formatting."},
                    {"role": "user", "content": f"Here is the dataset in CSV format:\n{csv_string}\n\n{prompt}\n\nPlease return the cleaned dataset in CSV format only, without any text or explanations."}
                ]
            )

            # Assuming the API now returns the processed dataset as a CSV string
            processed_csv_string = response.choices[0].message.content.strip()

            # Convert the processed CSV string back to a DataFrame using io.StringIO
            processed_df = pd.read_csv(io.StringIO(processed_csv_string))

            print(tabulate(processed_df.head(), headers='keys', tablefmt='psql'))

            st.session_state['processed_df'] = processed_df  # Store the processed DataFrame in session state

    # Display the processed DataFrame if it exists in session state
    if st.session_state.processed_df is not None:
        st.markdown("#### Processed Dataset:")
        st.dataframe(st.session_state['processed_df'])

        # Prompt user to specify the hyper file name
        hyper_file_name = st.text_input("**Enter the .hyper file name** (default set as 'output_file.hyper')", value="output_file.hyper")
        table_name = st.text_input("**Enter the table name for the .hyper file** (default set as 'Extract')", value="Extract")

        # Construct the full file path within the 'hyper_exports' directory
        hyper_file_path = os.path.join("hyper_exports", hyper_file_name)

        # Button to export data as .hyper file
        if st.button("Export as .hyper file"):
            try:
                write_hyper_file(st.session_state.processed_df, hyper_file_path, table_name)
                st.success(f"Data has been successfully written to {hyper_file_path}")
            except Exception as e:
                st.error(f"Failed to write data to .hyper file: {e}")

        table_name = st.text_input(
            "**Enter the table name to push the data**\n\n*The table name is expected to be in the following format, schema_name.table_name.*"
        )

        if st.button("Writeback to SQL Server"):
            success = push_data_to_sql(st.session_state.processed_df, table_name, server, database, user_id, password)
            if success:
                st.success(f"Data successfully pushed to table `{table_name}`.")
            else:
                st.error(f"Failed to push data to table `{table_name}`.")