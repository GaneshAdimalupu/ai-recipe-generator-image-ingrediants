import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Be My Chef AI - Recipe Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)
<<<<<<< HEAD
from pages.widgets import __login__


def main():
=======

from pages.widgets import __login__

# Initialize session state variables
if "LOGGED_IN" not in st.session_state:
    st.session_state["LOGGED_IN"] = False
if "LOGOUT_BUTTON_HIT" not in st.session_state:
    st.session_state["LOGOUT_BUTTON_HIT"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

def main():
    """Main function to handle the application flow"""

    #     # Check if already logged in
    if st.session_state["LOGGED_IN"]:
        st.switch_page("pages/home.py")
    
>>>>>>> 65553f288aa047f6c720f3b484687aa77fb31d93
    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
        logout_button_name="Logout",
        hide_menu_bool=False,
        hide_footer_bool=False,
    )

<<<<<<< HEAD
    is_logged_in = login_ui.build_login_ui()
    # If logged in, redirect to home page
    if is_logged_in and st.session_state.get("current_page") == "home":
        st.switch_page("pages/home.py")


if __name__ == "__main__":
    main()
=======

    # Build login UI
    login_ui.build_login_ui()

if __name__ == "__main__":
    main()
>>>>>>> 65553f288aa047f6c720f3b484687aa77fb31d93
