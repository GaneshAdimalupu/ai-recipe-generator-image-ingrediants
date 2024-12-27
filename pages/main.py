import streamlit as st
from pages.widgets import __login__

# Initialize login UI
login_ui = __login__(
    auth_token="your_courier_auth_token",
    company_name="Be My Chef AI",
    width=200,
    height=200,
)

# Check if user is logged in and show navigation
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")
else:
    # Show navigation sidebar
    login_ui.nav_sidebar()



# Assuming your main page content is inside this file
def load_main_page():
    st.title("Welcome to the Main Page")
    # Add more content here as required


# Check if user is logged in, if not, redirect to login page
if st.session_state.get("LOGGED_IN", False):
    load_main_page()
else:
    st.write("Please log in to access the main page.")
