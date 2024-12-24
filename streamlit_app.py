import streamlit as st

# 1. Set the page configuration **immediately after imports**
st.set_page_config(
    page_title="Be My Chef AI",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)
from time import sleep
from navigation import make_sidebar

make_sidebar()

# Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Handle authentication
if not st.session_state.logged_in:
    st.title("Welcome to Be My Chef AI")
    st.write("Please log in to continue (username `test`, password `test`).")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in", type="primary"):
        if username == "test" and password == "test":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            sleep(0.5)
            # st.switch_page("pages/page1.py")
            st.switch_page("pages/home.py")
        else:
            st.error("Incorrect username or password")
else:
    st.title("Welcome to Be My Chef AI")
    st.success("You are logged in!")

