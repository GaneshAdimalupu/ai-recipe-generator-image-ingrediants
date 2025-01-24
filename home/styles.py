import streamlit as st


def load_custom_css():
    """Load all custom CSS styles for the application"""
    st.markdown(
        """
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Card styling */
        .recipe-card {
            background-color: #ffffff;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        /* Header styling */
        .st-emotion-cache-1v0mbdj > h1 {
            color: #1e3d59;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: #f7f9fc;
            border-radius: 10px;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            border-radius: 8px;
            color: #1e3d59;
            font-weight: 600;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 2rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Recipe sections styling */
        .recipe-section {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .recipe-title {
            color: #1e3d59;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .ingredient-item {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .instruction-step {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Nutrition card styling */
        .nutrition-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Animation container */
        .lottie-container {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

