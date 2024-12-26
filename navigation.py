import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages


def get_current_page_name():
    """Retrieve the name of the currently running Streamlit page."""
    ctx = get_script_run_ctx()
    if ctx is None:
        return "streamlit_app"

    # Match the hash of the current script with known pages
    pages = st.session_state.get("pages", {})
    for key, value in pages.items():
        if value.get("page_script_hash") == ctx.page_script_hash:
            return value["page_name"]
    return "streamlit_app"


def make_sidebar():
    """Create the sidebar for navigation and user actions."""
    with st.sidebar:
        st.title("💎 Be My Chef AI")
        st.write("AI-Powered Recipe Assistance")

        # Logged-in user navigation
        if st.session_state.get("logged_in", False):
            st.write("### Navigation")
            if st.button("Recipe AI Model 👩🏻‍🍳"):
                st.switch_page("pages/home.py")
            if st.button("Posts Page 📝"):
                st.switch_page("pages/posts.py")
            if st.button("Chatbot"):
                st.switch_page("pages/chatbot.py")
            if st.button("Search Engine"):
                st.switch_page("pages/search.py")

            st.markdown("---")
            if st.button("Log out 🔓"):
                logout()
        else:
            # Redirect to login if not logged in
            current_page = get_current_page_name()
            if current_page != "streamlit_app":
                st.warning("You need to log in to access this page.")
                st.experimental_set_page("streamlit_app")


def logout():
    """Handle user logout."""
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    sleep(0.5)
    st.experimental_set_page("streamlit_app")
