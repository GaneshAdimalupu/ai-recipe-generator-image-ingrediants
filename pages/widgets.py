from datetime import time
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os
from .utils import (
    check_usr_pass,
    load_lottieurl,
    check_valid_name,
    check_valid_email,
    check_unique_email,
    check_unique_usr,
    register_new_usr,
    check_email_exists,
    generate_random_passwd,
    send_passwd_in_email,
    change_passwd,
    check_current_passwd,
)


class __login__:
    """
    Builds the UI for the Login/ Sign Up page with MongoDB backend.
    """

    def __init__(
        self,
        auth_token: str,
        company_name: str,
        width,
        height,
        logout_button_name: str = "Logout",
        hide_menu_bool: bool = False,
        hide_footer_bool: bool = False,
        lottie_url: str = "https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json",
    ):
        """
        Arguments:
        -----------
        auth_token : The unique authorization token for email service
        company_name : Organization name for password reset emails
        width : Width of the login page animation
        height : Height of the login page animation
        logout_button_name : Custom logout button text
        hide_menu_bool : Whether to hide the streamlit menu
        hide_footer_bool : Whether to hide the streamlit footer
        lottie_url : URL for the lottie animation
        """
        self.auth_token = auth_token
        self.company_name = company_name
        self.width = width
        self.height = height
        self.logout_button_name = logout_button_name
        self.hide_menu_bool = hide_menu_bool
        self.hide_footer_bool = hide_footer_bool
        self.lottie_url = lottie_url

        # Initialize session state variables
        if "LOGGED_IN" not in st.session_state:
            st.session_state["LOGGED_IN"] = False
        if "LOGOUT_BUTTON_HIT" not in st.session_state:
            st.session_state["LOGOUT_BUTTON_HIT"] = False
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "home"

        # Add these new initializations for navigation state
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'home'
        if 'page_transition' not in st.session_state:
            st.session_state.page_transition = False
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = 'home'

        self.cookies = EncryptedCookieManager(
            prefix="streamlit_login_ui_yummy_cookies",
            password="9d68d6f2-4258-45c9-96eb-2d6bc74ddbb5-d8f49cab-edbb-404a-94d0-b25b1d4a564b",
        )

        if not self.cookies.ready():
            st.stop()
    def get_username(self):
        """Retrieves username from cookies if user is logged in."""
        if not st.session_state["LOGOUT_BUTTON_HIT"]:
            fetched_cookies = self.cookies
            if "__streamlit_login_signup_ui_username__" in fetched_cookies.keys():
                return fetched_cookies["__streamlit_login_signup_ui_username__"]
        return None

    def get_current_page(self):
        """Get the current page filename."""
        try:
            return os.path.basename(st.script_run_ctx.script_path)
        except:
            return "home.py"

    def login_widget(self):
        """Creates the login widget and handles authentication."""
        if not st.session_state["LOGGED_IN"]:
            del_login = st.empty()
            with del_login.form("Login Form"):
                username = st.text_input("Username", placeholder="Your unique username")
                password = st.text_input(
                    "Password", placeholder="Your password", type="password"
                )

                st.markdown("###")
                login_submit_button = st.form_submit_button(label="Login")

                if login_submit_button:
                    if check_usr_pass(username, password):
                        st.session_state["LOGGED_IN"] = True
                        st.session_state["current_page"] = "home"
                        self.cookies["__streamlit_login_signup_ui_username__"] = username
                        self.cookies.save()
                        del_login.empty()
                        st.switch_page("pages/home.py")
                    else:
                        st.error("Invalid Username or Password!")

    def animation(self):
        """Renders the lottie animation."""
        lottie_json = load_lottieurl(self.lottie_url)
        st_lottie(lottie_json, width=self.width, height=self.height)

    def sign_up_widget(self):
        """Creates the sign-up widget and handles user registration."""
        with st.form("Sign Up Form"):
            name_sign_up = st.text_input("Name *", placeholder="Please enter your name")
            valid_name_check = check_valid_name(name_sign_up)

            email_sign_up = st.text_input("Email *", placeholder="Please enter your email")
            valid_email_check = check_valid_email(email_sign_up)
            unique_email_check = check_unique_email(email_sign_up)

            username_sign_up = st.text_input(
                "Username *", placeholder="Enter a unique username"
            )
            unique_username_check = check_unique_usr(username_sign_up)

            password_sign_up = st.text_input(
                "Password *", placeholder="Create a strong password", type="password"
            )

            st.markdown("###")
            sign_up_submit_button = st.form_submit_button(label="Register")

            if sign_up_submit_button:
                if not valid_name_check:
                    st.error("Please enter a valid name!")
                elif not valid_email_check:
                    st.error("Please enter a valid Email!")
                elif not unique_email_check:
                    st.error("Email already exists!")
                elif not unique_username_check:
                    st.error(f"Sorry, username {username_sign_up} already exists!")
                elif unique_username_check is None:
                    st.error("Please enter a non-empty Username!")
                elif all(
                    [
                        valid_name_check,
                        valid_email_check,
                        unique_email_check,
                        unique_username_check,
                    ]
                ):
                    register_new_usr(
                        name_sign_up, email_sign_up, username_sign_up, password_sign_up
                    )
                    st.success("Registration Successful!")

    def forgot_password(self):
        """Handles the forgot password functionality."""
        with st.form("Forgot Password Form"):
            email_forgot_passwd = st.text_input(
                "Email", placeholder="Please enter your email"
            )
            email_exists_check, username_forgot_passwd = check_email_exists(
                email_forgot_passwd
            )

            st.markdown("###")
            forgot_passwd_submit_button = st.form_submit_button(label="Get Password")

            if forgot_passwd_submit_button:
                if not email_exists_check:
                    st.error("Email ID not registered with us!")
                else:
                    random_password = generate_random_passwd()
                    send_passwd_in_email(
                        self.auth_token,
                        username_forgot_passwd,
                        email_forgot_passwd,
                        self.company_name,
                        random_password,
                    )
                    change_passwd(email_forgot_passwd, random_password)
                    st.success("Secure Password Sent Successfully!")

    def reset_password(self):
        """Handles password reset functionality."""
        with st.form("Reset Password Form"):
            email_reset_passwd = st.text_input(
                "Email", placeholder="Please enter your email"
            )
            email_exists_check, username_reset_passwd = check_email_exists(
                email_reset_passwd
            )

            current_passwd = st.text_input(
                "Temporary Password",
                placeholder="Please enter the password you received in the email",
            )
            current_passwd_check = check_current_passwd(
                email_reset_passwd, current_passwd
            )

            new_passwd = st.text_input(
                "New Password",
                placeholder="Please enter a new, strong password",
                type="password",
            )
            new_passwd_1 = st.text_input(
                "Re-Enter New Password",
                placeholder="Please re-enter the new password",
                type="password",
            )

            st.markdown("###")
            reset_passwd_submit_button = st.form_submit_button(label="Reset Password")

            if reset_passwd_submit_button:
                if not email_exists_check:
                    st.error("Email does not exist!")
                elif not current_passwd_check:
                    st.error("Incorrect temporary password!")
                elif new_passwd != new_passwd_1:
                    st.error("Passwords don't match!")
                elif all(
                    [
                        email_exists_check,
                        current_passwd_check,
                        new_passwd == new_passwd_1,
                    ]
                ):
                    change_passwd(email_reset_passwd, new_passwd)
                    st.success("Password Reset Successfully!")

    def nav_sidebar(self):
        """Creates the side navigation bar that persists across pages."""
        with st.sidebar:
            st.markdown('<h1 class="sidebar-title">💎 Be My Chef AI</h1>', unsafe_allow_html=True)
            st.write("AI-Powered Recipe Assistance")

            if st.session_state["LOGGED_IN"]:
                # Initialize current view if not exists
                if 'current_view' not in st.session_state:
                    st.session_state.current_view = 'home'

                # Define menu items
                menu_items = [
                    {"id": "home", "title": "Recipe AI Model", "icon": "house-fill"},
                    {"id": "posts", "title": "Community Feed", "icon": "people-fill"},
                    {"id": "recipe", "title": "Recipe Explorer", "icon": "book"},
                    {"id": "search", "title": "Recipe Search", "icon": "search"},
                    {
                        "id": "chatbot",
                        "title": "Recipe Assistant",
                        "icon": "chat-dots-fill",
                    },
                    {"id": "profile", "title": "Profile", "icon": "person-circle"},
                ]

                # Get current page and index
                current_id = st.session_state.current_view  # Default to current view
                try:
                    current_path = os.path.basename(st.script_run_ctx.script_path)
                    if current_path.endswith('.py'):
                        current_id = current_path[:-3]  # Remove .py extension
                except Exception:
                    pass  # Keep using the default current_id

                # Find current index
                current_index = next((i for i, item in enumerate(menu_items) 
                                    if item["id"] == current_id), 0)

                # Create navigation menu
                selected = option_menu(
                    menu_title=None,
                    options=[item["title"] for item in menu_items],
                    icons=[item["icon"] for item in menu_items],
                    default_index=current_index,
                    styles={
                        "container": {"padding": "0!important", "background-color": "transparent"},
                        "icon": {"font-size": "1rem", "margin-right": "8px"},
                        "nav-link": {
                            "font-size": "0.9rem",
                            "text-align": "left",
                            "padding": "0.75rem",
                            "margin": "0.2rem 0",
                            "transition": "all 0.3s ease"
                        },
                        "nav-link-selected": {
                            "background-color": "#FF4B4B",
                            "font-weight": "600"
                        }
                    }
                )

                # Handle navigation
                selected_item = next((item for item in menu_items if item["title"] == selected), None)
                if selected_item:
                    page_name = selected_item["id"]
                    if current_id != page_name:
                        st.session_state.current_view = page_name
                        st.switch_page(f"pages/{page_name}.py")

                # Logout section
                st.markdown("---")
                if st.button("🔒 Logout", key="logout", use_container_width=True):
                    self.handle_logout()

            else:
                # Login-related navigation
                selected = option_menu(
                    menu_title=None,
                    options=[
                        "Login",
                        "Create Account",
                        "Forgot Password?",
                        "Reset Password"
                    ],
                    icons=[
                        "box-arrow-in-right",
                        "person-plus-fill",
                        "question-circle-fill",
                        "arrow-counterclockwise"
                    ],
                    styles={
                        "container": {"padding": "0!important", "background-color": "transparent"},
                        "icon": {"font-size": "1rem", "margin-right": "8px"},
                        "nav-link": {
                            "font-size": "0.9rem",
                            "text-align": "left",
                            "padding": "0.75rem",
                            "margin": "0.2rem 0",
                        },
                        "nav-link-selected": {
                            "background-color": "#FF4B4B",
                            "font-weight": "600"
                        }
                    }
                )

            return selected

    def render_page_content(self):
        """Renders the content for the current view"""
        if not st.session_state.get("LOGGED_IN"):
            return

        # Add a loading spinner during transitions
        if st.session_state.get('page_transition'):
            with st.spinner("Loading..."):
                time.sleep(0.3)  # Short delay for smooth transition
            st.session_state.page_transition = False

        current_view = st.session_state.get('current_view', 'home')

        try:
            if current_view == 'home':
                from pages.home import render_home_content
                render_home_content()
            elif current_view == 'posts':
                from pages.posts import render_posts_content
                render_posts_content()
            elif current_view == 'recipe':
                from pages.recipe_xplorer import render_recipe_content
                render_recipe_content()
            elif current_view == 'search':
                from pages.search import render_search_content
                render_search_content()
            elif current_view == 'chatbot':
                from pages.chatbot import render_chatbot_content
                render_chatbot_content()
            elif current_view == 'profile':
                from pages.profile import render_profile_page
                render_profile_page()
                current_user = st.session_state.get('username')
                render_profile_page(current_user) 
        except Exception as e:
            st.error(f"Error loading content: {str(e)}")

    def handle_logout(self):
        """Handles the logout process."""
        st.session_state["LOGGED_IN"] = False
        st.session_state["LOGOUT_BUTTON_HIT"] = True
        st.session_state["current_page"] = "home"
        st.session_state.nav_selected = 'home.py'  # Reset navigation selection
        st.session_state.nav_page_changed = False  # Reset navigation change flag
        self.cookies["__streamlit_login_signup_ui_username__"] = (
            "1c9a923f-fb21-4a91-b3f3-5f18e3f01182"
        )
        self.cookies.save()
        st.switch_page("streamlit_app.py")

    def hide_menu(self):
        """Hides the streamlit menu."""
        st.markdown(
            """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
        """,
            unsafe_allow_html=True,
        )

    def hide_footer(self):
        """Hides the streamlit footer."""
        st.markdown(
            """
            <style>
            footer {visibility: hidden;}
            </style>
        """,
            unsafe_allow_html=True,
        )

    def build_login_ui(self):
        """Main method to build the complete login UI."""
        # Check if user is already logged in via cookies
        if not st.session_state["LOGGED_IN"] and not st.session_state["LOGOUT_BUTTON_HIT"]:
            if "__streamlit_login_signup_ui_username__" in self.cookies:
                if self.cookies["__streamlit_login_signup_ui_username__"] != "1c9a923f-fb21-4a91-b3f3-5f18e3f01182":
                    st.session_state["LOGGED_IN"] = True

        # Initialize view state if needed
        if st.session_state.get("LOGGED_IN") and 'current_view' not in st.session_state:
            st.session_state.current_view = 'home'

        selected_option = self.nav_sidebar()

        if st.session_state.get("LOGGED_IN"):
            # Render the main content for logged-in users
            self.render_page_content()
        else:
            # Handle non-logged-in state
            if selected_option == "Login":
                c1, c2 = st.columns([7, 3])
                with c1:
                    self.login_widget()
                with c2:
                    self.animation()
            elif selected_option == "Create Account":
                self.sign_up_widget()
            elif selected_option == "Forgot Password?":
                self.forgot_password()
            elif selected_option == "Reset Password":
                self.reset_password()

        if self.hide_menu_bool:
            self.hide_menu()
        if self.hide_footer_bool:
            self.hide_footer()

        return st.session_state["LOGGED_IN"]
