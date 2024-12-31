import streamlit as st
from pages.widgets import __login__
from PIL import Image
import time


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


# Custom CSS for styling
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .title {
            font-size: 50px !important;
            color: #1E1E1E;
            text-align: center;
            padding: 30px;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
            margin-bottom: 30px;
        }
        .subtitle {
            font-size: 24px !important;
            color: #4A4A4A;
            text-align: center;
            font-family: 'Helvetica Neue', sans-serif;
            margin-bottom: 50px;
        }
        .card {
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .center {
            text-align: center;
        }
        .btn {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            font-size: 16px;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background-color: #45a049;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Simulate page loading
def load_page():
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    progress_bar.empty()


# Dynamic feature card generator
def create_card(title, description, image_url):
    return f"""
    <div class="card">
        <h3 style='text-align: center;'>{title}</h3>
        <img src="{image_url}" style='width: 100%; border-radius: 5px;'>
        <p style='text-align: center; margin-top: 10px;'>{description}</p>
    </div>
    """


# Main page content
def main_page():
    load_page()

    # Display Title and Subtitle
    st.markdown('<p class="title">Welcome to Be My Chef AI</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Your personalized AI-powered kitchen assistant</p>',
        unsafe_allow_html=True,
    )

    # Dynamic Features Section
    features = [
        {
            "title": "AI Recipe Suggestions",
            "description": "Get customized recipes based on your ingredients and preferences.",
            "image_url": "https://via.placeholder.com/150",
        },
        {
            "title": "Ingredient Recognition",
            "description": "Upload food images to recognize ingredients instantly.",
            "image_url": "https://via.placeholder.com/150",
        },
        {
            "title": "Nutritional Insights",
            "description": "Analyze the nutritional value of your meals effortlessly.",
            "image_url": "https://via.placeholder.com/150",
        },
    ]

    # Create columns for cards
    cols = st.columns(len(features))
    for col, feature in zip(cols, features):
        with col:
            st.markdown(
                create_card(
                    feature["title"], feature["description"], feature["image_url"]
                ),
                unsafe_allow_html=True,
            )

    # Call-to-Action Button
    st.markdown(
        """
        <div class="center">
            <button class="btn" onclick="location.href='#'">Explore More</button>
        </div>
        """,
        unsafe_allow_html=True,
    )
