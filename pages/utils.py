import re
import json
import logging
import secrets
from argon2 import PasswordHasher
from mongodb.db import get_database
from trycourier import Courier
import requests
from pymongo import  errors

ph = PasswordHasher()

# MongoDB connection
db = get_database()
users_collection = db["users"]  # Collection name


def check_usr_pass(username: str, password: str) -> bool:
    """Authenticates the username and password using MongoDB."""
    user = users_collection.find_one({"username": username})
    if user:
        try:
            if ph.verify(user["password"], password):
                return True
        except Exception as e:
            logging.error(f"Password verification failed: {e}")
            return False


def load_lottieurl(url: str) -> str:
    """
    Fetches the lottie animation using the URL.
    """
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        pass


users_collection.create_index("email", unique=True)
users_collection.create_index("username", unique=True)


def check_valid_name(name_sign_up: str) -> bool:
    """Checks if the user entered a valid name while creating the account."""
    name_regex = r"^[A-Za-z][A-Za-z0-9_]{2,30}$"
    return bool(re.match(name_regex, name_sign_up))


def check_valid_email(email_sign_up: str) -> bool:
    """
    Checks if the user entered a valid email while creating the account.
    """
    email_regex = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    return bool(re.fullmatch(email_regex, email_sign_up))


def check_unique_email(email_sign_up: str) -> bool:
    """
    Checks if the email already exists (since email needs to be unique).
    """
    return users_collection.count_documents({"email": email_sign_up}) == 0


def non_empty_str_check(username_sign_up: str) -> bool:
    """
    Checks for non-empty strings.
    """
    empty_count = 0
    for i in username_sign_up:
        if i == " ":
            empty_count = empty_count + 1
            if empty_count == len(username_sign_up):
                return False

    if not username_sign_up:
        return False
    return True


def check_unique_usr(username_sign_up: str):
    """
    Checks if the username already exists (since username needs to be unique),
    also checks for non - empty username.
    """
    return users_collection.count_documents({"username": username_sign_up}) == 0


def register_new_usr(name: str, email: str, username: str, password: str) -> None:
    """Registers a new user."""
    try:
        hashed_password = ph.hash(password)
        new_user = {
            "name": name,
            "email": email,
            "username": username,
            "password": hashed_password,
        }
        users_collection.insert_one(new_user)
        logging.info(f"User {username} registered successfully.")
    except errors.DuplicateKeyError as e:
        logging.error(f"Duplicate key error: {e}")




def check_username_exists(user_name: str) -> bool:
    """
    Checks if the username exists in the MongoDB database.
    """
    # Query to check if the username exists
    user = users_collection.find_one({"username": user_name})

    return user is not None


def check_email_exists(email_forgot_passwd: str):
    """
    Checks if the email entered is present in the MongoDB database.
    """
    # Query to find the user by email
    user = users_collection.find_one({"email": email_forgot_passwd})

    if user:
        return True, user.get("username")
    return False, None


def generate_random_passwd() -> str:
    """Generates a random password to be sent in email."""
    password_length = 10
    return secrets.token_urlsafe(password_length)


def send_passwd_in_email(
    auth_token: str, username: str, email: str, company_name: str, random_password: str
) -> None:
    """Sends the generated password via email."""
    try:
        client = Courier(auth_token=auth_token)
        client.send_message(
            message={
                "to": {"email": email},
                "content": {
                    "title": f"{company_name}: Login Password!",
                    "body": f"Hi {username},\n\nYour temporary login password is: {random_password}\n\nPlease reset your password for security reasons.",
                },
            }
        )
        logging.info(f"Password email sent to {email}.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def change_passwd(email: str, new_password: str) -> None:
    """Updates the user's password."""
    try:
        hashed_password = ph.hash(new_password)
        users_collection.update_one(
            {"email": email}, {"$set": {"password": hashed_password}}
        )
        logging.info(f"Password updated for {email}.")
    except Exception as e:
        logging.error(f"Failed to update password: {e}")


def check_current_passwd(email: str, current_passwd: str) -> bool:
    """Verifies the current password."""
    try:
        user = users_collection.find_one({"email": email})
        if user and ph.verify(user["password"], current_passwd):
            return True
    except Exception as e:
        logging.error(f"Password verification error: {e}")
    return False


def validate_non_empty_str(input_str: str) -> bool:
    """Checks for non-empty strings."""
    return bool(input_str and not input_str.isspace())
