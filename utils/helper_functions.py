import pandas as pd
import hashlib
import pyodbc
import base64
import json
import os

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

def fetch_data_from_sql(query, server, database, user_id, password):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Authentication=ActiveDirectoryPassword;"
        f"UID={user_id};"
        f"PWD={password};"
    )
    
    with pyodbc.connect(conn_str) as conn:
        df = pd.read_sql(query, conn)
    
    return df

def push_data_to_sql(df, full_table_name, server, database, user_id, password):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Authentication=ActiveDirectoryPassword;"
        f"UID={user_id};"
        f"PWD={password};"
    )
    
    # Split full_table_name into schema_name and table_name
    schema_name, table_name = full_table_name.split('.')
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute(f"""
            IF OBJECT_ID('{schema_name}.{table_name}', 'U') IS NULL
            BEGIN
                CREATE TABLE [{schema_name}].[{table_name}] (
                    {', '.join([f'[{col}] NVARCHAR(MAX)' for col in df.columns])}
                )
            END
        """)
        
        # Create an insert statement with proper quoting
        columns = ', '.join([f"[{col}]" for col in df.columns])
        placeholders = ', '.join(['?'] * len(df.columns))
        sql = f"INSERT INTO [{schema_name}].[{table_name}] ({columns}) VALUES ({placeholders})"
        
        # Print the SQL statement for debugging purposes
        print(sql)  # You can comment this out or remove it after debugging

        # Convert DataFrame rows to tuples
        data = [tuple(row) for row in df.to_numpy()]
        
        # Execute the insert statement for each row
        cursor.executemany(sql, data)
        conn.commit()

    return True