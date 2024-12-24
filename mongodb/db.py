from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
#from dotenv import load_dotenv
import os
import urllib.parse  # Import the URL parsing library

# Load environment variables
#load_dotenv()

import streamlit as st


def get_database():
    # Retrieve the MongoDB URI from the .env file
    # uri = os.getenv("MONGODB_URI")
    uri = st.secrets["mongo"]["MONGODB_URI"]

    if not uri:
        raise ValueError("MONGODB_URI is not set in the environment variables.")

    # Parse and encode the username and password
    userinfo_start = (
        uri.find("//") + 2
    )  # Find the start of userinfo (username:password)
    userinfo_end = uri.find("@")  # Find the end of userinfo (before the '@' symbol)

    # Extract username and password from the URI
    userinfo = uri[userinfo_start:userinfo_end]
    username, password = userinfo.split(":")

    # URL encode the username and password
    encoded_username = urllib.parse.quote_plus(username)
    encoded_password = urllib.parse.quote_plus(password)

    # Replace the original username and password in the URI with the encoded ones
    uri = uri.replace(username, encoded_username).replace(password, encoded_password)

    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi("1"))

        # Test the connection
        client.admin.command("ping")
        print("Successfully connected to MongoDB!")

        # Connect to the specific database
        database_name = "be-my-chef-ai"
        return client[database_name]
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
