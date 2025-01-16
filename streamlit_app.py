import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Be My Chef AI - Recipe Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)
from pages.widgets import __login__


def main():
    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
        logout_button_name="Logout",
        hide_menu_bool=False,
        hide_footer_bool=False,
    )

    is_logged_in = login_ui.build_login_ui()
    # If logged in, redirect to home page
    if is_logged_in and st.session_state.get("current_page") == "home":
        st.switch_page("pages/home.py")


if __name__ == "__main__":
    main()
