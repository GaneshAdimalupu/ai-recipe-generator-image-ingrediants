import streamlit as st
import pandas as pd
from pages.widgets import __login__
from xplorer.recipe_styles import apply_recipe_styles
from xplorer.recipe_card import render_recipe_card
from utils.recipe_helpers import (
    load_recipe_data,
    filter_recipes,
    search_recipes
)

# Initialize session states
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
if 'should_scroll' not in st.session_state:
    st.session_state.should_scroll = False
if 'recipes_per_page' not in st.session_state:
    st.session_state.recipes_per_page = 10

# Initialize login check
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")

# Initialize login UI
login_ui = __login__(
    auth_token="your_courier_auth_token",
    company_name="Be My Chef AI",
    width=200,
    height=200,
)

# Get current user
current_user = login_ui.get_username()

# Apply styles
st.markdown(apply_recipe_styles(), unsafe_allow_html=True)

# Show navigation sidebar
login_ui.nav_sidebar()

# Page Layout
st.markdown("""
    <div class="page-header">
        <h1>🍛 Indian Recipe Explorer</h1>
        <p>Discover authentic Indian recipes and save your favorites</p>
    </div>
""", unsafe_allow_html=True)

# View selector
VIEW_OPTIONS = {
    "All Recipes": "Browse all recipes",
    "Saved Recipes": "View your saved recipes"
}

# Main content
try:
    selected_view = st.radio(
        "View",
        list(VIEW_OPTIONS.keys()),
        format_func=lambda x: VIEW_OPTIONS[x],
        horizontal=True
    )

    # Load and filter recipes
    recipes_df = load_recipe_data()
    if recipes_df is not None:
        # Filter by view
        filtered_df = filter_recipes(recipes_df, selected_view, current_user)
        
        # Search functionality
        search_query = st.text_input("🔍 Search recipes by name, ingredients, or cuisine")
        filtered_df = search_recipes(filtered_df, search_query)
        
        # Sort recipes
        sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Name (Z-A)"])
        filtered_df = filtered_df.sort_values(
            'name',
            ascending=(sort_by == "Name (A-Z)")
        )
        
        # Pagination
        total_recipes = len(filtered_df)
        RECIPES_PER_PAGE = st.session_state.recipes_per_page
        total_pages = (total_recipes + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE
        
        # Display recipe count
        st.markdown(f"""
            <div class="results-count">
                Found <span class="highlight">{total_recipes}</span> recipes
            </div>
        """, unsafe_allow_html=True)
        
        if total_pages > 0:
            # Page selector
            page_number = st.select_slider(
                "Page",
                options=range(1, total_pages + 1),
                value=st.session_state.page_number,
                format_func=lambda x: f"Page {x} of {total_pages}"
            )
            st.session_state.page_number = page_number
            
            # Display recipes
            start_idx = (page_number - 1) * RECIPES_PER_PAGE
            end_idx = min(start_idx + RECIPES_PER_PAGE, total_recipes)
            
            for i, (_, recipe) in enumerate(filtered_df.iloc[start_idx:end_idx].iterrows()):
                render_recipe_card(recipe, current_user, i + start_idx)
            
            # Pagination navigation
            col1, col2, col3 = st.columns([1,2,1])
            with col1:
                if page_number > 1:
                    if st.button("← Previous"):
                        st.session_state.page_number = page_number - 1
                        st.session_state.should_scroll = True
                        st.rerun()
            with col3:
                if page_number < total_pages:
                    if st.button("Next →"):
                        st.session_state.page_number = page_number + 1
                        st.session_state.should_scroll = True
                        st.rerun()
        else:
            st.info("No recipes found matching your criteria.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure your data file is properly formatted and try again.")