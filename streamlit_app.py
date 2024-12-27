import streamlit as st
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


if __name__ == "__main__":
    main()
