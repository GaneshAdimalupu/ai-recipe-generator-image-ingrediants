import streamlit as st


# 1. Set the page configuration
st.set_page_config(
    page_title="Be My Chef AI",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

from time import sleep
from login_auth_ui.widgets import __login__

# 2. Initialize the login widget
__login__obj = __login__(
    auth_token="courier_auth_token",
    company_name="Be My Chef AI",
    width=200,
    height=250,
    logout_button_name="Logout",
    hide_menu_bool=False,
    hide_footer_bool=False,
    lottie_url="https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json",
)

LOGGED_IN = __login__obj.build_login_ui()
username = __login__obj.get_username()

# 3. After successful login
if LOGGED_IN:
    # Save username to session state
    # st.session_state["username"] = username

    # Display a welcome message
    # st.title(f"Welcome, {username}!")
    st.success("You are now logged in!")

    # Navigate to the home page
    sleep(0.5)
    st.switch_page("pages/home.py")  # Ensure 'home.py' exists in the 'pages' directory
else:
    st.warning("Please log in to access the application.")

