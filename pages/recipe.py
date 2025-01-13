import streamlit as st
import pandas as pd
from pages.widgets import __login__
import requests
from PIL import Image
from io import BytesIO
from mongodb.db import get_database
import time
from datetime import datetime

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

# Show navigation sidebar
login_ui.nav_sidebar()

# Get current user
current_user = login_ui.get_username()

# Connect to MongoDB
db = get_database()
saved_recipes = db["saved_recipes"]

# Helper Functions
def parse_ingredients(ingredients_str):
    """Parse ingredients string into structured format"""
    if pd.isna(ingredients_str):
        return []
    
    # Split by newlines and clean
    ingredients = [ing.strip() for ing in ingredients_str.split('\n') if ing.strip()]
    cleaned_ingredients = []
    
    for ing in ingredients:
        # Clean the string
        ing = ing.replace('\t', '').strip()
        
        # Split by comma for quantity and name
        if ',' in ing:
            parts = ing.split(',', 1)
            quantity = parts[0].strip()
            name = parts[1].strip()
        else:
            quantity = ""
            name = ing.strip()
        
        if quantity or name:
            cleaned_ingredients.append({
                'quantity': quantity,
                'name': name
            })
    
    return cleaned_ingredients

def parse_instructions(instructions_str):
    """Parse instructions into clear steps"""
    if pd.isna(instructions_str):
        return []
    
    # Split by periods and clean
    steps = [step.strip() for step in instructions_str.split('.') if step.strip()]
    return steps

def load_image(url):
    """Load image from URL with error handling"""
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        return None

# Recipe saving functions
def is_recipe_saved(recipe_name, user):
    """Check if recipe is saved by user"""
    if not user:
        return False
    return saved_recipes.find_one({
        "user": user,
        "recipe_name": recipe_name
    }) is not None

def toggle_recipe_save(recipe_name, recipe_data, user):
    """Toggle save state of recipe"""
    if not user:
        return False
        
    if is_recipe_saved(recipe_name, user):
        saved_recipes.delete_one({
            "user": user,
            "recipe_name": recipe_name
        })
        return False
    else:
        saved_recipes.insert_one({
            "user": user,
            "recipe_name": recipe_name,
            "recipe_data": recipe_data,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True

# Load recipe data
@st.cache_data
def load_recipe_data():
    try:
        recipes_df = pd.read_csv('data/indian_recipes.csv')
        
        # Clean the data
        recipes_df['cuisine'] = recipes_df['cuisine'].fillna('Not Specified')
        recipes_df['course'] = recipes_df['course'].fillna('Not Specified')
        recipes_df['diet'] = recipes_df['diet'].fillna('Not Specified')
        recipes_df['prep_time'] = recipes_df['prep_time'].fillna('Not Specified')
        recipes_df['description'] = recipes_df['description'].fillna('No description available')
        recipes_df['ingredients'] = recipes_df['ingredients'].fillna('Not specified')
        recipes_df['instructions'] = recipes_df['instructions'].fillna('Not specified')
        
        return recipes_df
    except Exception as e:
        st.error(f"Error loading recipe data: {str(e)}")
        return None

# Initialize session state
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
    
# Add custom CSS
st.markdown("""
<style>
    /* Recipe Card */
    .recipe-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .recipe-title {
        color: #FF4B4B;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .recipe-info {
        color: #666;
        font-size: 14px;
        margin-bottom: 15px;
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }
    
    /* Recipe Content */
    .recipe-description {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-style: italic;
    }
    
    .ingredients-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        margin: 15px 0;
    }
    
    .ingredient-item {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #FF4B4B;
    }
    
    .ingredient-quantity {
        font-weight: 600;
        color: #FF4B4B;
    }
    
    .instruction-step {
        background-color: #f8f9fa;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        position: relative;
        padding-left: 35px;
    }
    
    .step-number {
        position: absolute;
        left: 10px;
        top: 50%;
        transform: translateY(-50%);
        background-color: #FF4B4B;
        color: white;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    
    /* Interactive Elements */
    .save-button {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .save-button:hover {
        transform: scale(1.1);
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }
    
    .page-button {
        padding: 5px 15px;
        border-radius: 20px;
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        cursor: pointer;
    }
    
    .page-button:hover {
        background-color: #FF4B4B;
        color: white;
    }
    
    /* Search Bar */
    .search-container {
        margin: 20px 0;
    }
    
    .search-input {
        width: 100%;
        padding: 10px 15px;
        border-radius: 20px;
        border: 1px solid #ddd;
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .recipe-card {
            background-color: #262626;
        }
        
        .recipe-description,
        .ingredient-item,
        .instruction-step {
            background-color: #363636;
            color: #ffffff;
        }
        
        .search-input {
            background-color: #363636;
            color: #ffffff;
            border-color: #444;
        }
        
        .page-button {
            background-color: #363636;
            color: #ffffff;
            border-color: #444;
        }
        
        .recipe-info {
            color: #ccc;
        }
    }
    
    /* Loading States */
    .loading {
        text-align: center;
        padding: 20px;
        color: #666;
    }
    
    /* Responsiveness */
    @media (max-width: 768px) {
        .ingredients-grid {
            grid-template-columns: 1fr;
        }
        
        .recipe-info {
            flex-direction: column;
            gap: 5px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Page Layout
st.title("🍛 Indian Recipe Explorer")
st.markdown("""
    <p style='text-align: center; color: #666; font-size: 16px;'>
        Discover authentic Indian recipes and save your favorites
    </p>
""", unsafe_allow_html=True)

# Initialize view options
VIEW_OPTIONS = {
    "All Recipes": "Browse all recipes",
    "Saved Recipes": "View your saved recipes"
}

# View selector
selected_view = st.radio(
    "View",
    list(VIEW_OPTIONS.keys()),
    format_func=lambda x: VIEW_OPTIONS[x],
    horizontal=True
)

try:
    # Load recipe data
    recipes_df = load_recipe_data()
    
    if recipes_df is not None:
        # Handle different views
        if selected_view == "All Recipes":
            # Sidebar filters
            st.sidebar.title("Filter Recipes")
            
            # Prepare filter options
            cuisines = ["All"] + sorted(recipes_df['cuisine'].unique().tolist())
            courses = ["All"] + sorted(recipes_df['course'].unique().tolist())
            diets = ["All"] + sorted(recipes_df['diet'].unique().tolist())
            
            # Filter selections
            selected_cuisine = st.sidebar.selectbox("Cuisine", cuisines)
            selected_course = st.sidebar.selectbox("Course", courses)
            selected_diet = st.sidebar.selectbox("Diet", diets)
            
            # Apply filters
            filtered_df = recipes_df.copy()
            if selected_cuisine != "All":
                filtered_df = filtered_df[filtered_df['cuisine'] == selected_cuisine]
            if selected_course != "All":
                filtered_df = filtered_df[filtered_df['course'] == selected_course]
            if selected_diet != "All":
                filtered_df = filtered_df[filtered_df['diet'] == selected_diet]
        
        else:  # Saved Recipes
            if not current_user:
                st.warning("Please log in to view saved recipes")
                filtered_df = pd.DataFrame()
            else:
                saved_recipes_list = list(saved_recipes.find({"user": current_user}))
                if not saved_recipes_list:
                    st.info("No saved recipes yet. Browse recipes and click the ❤️ to save them!")
                    filtered_df = pd.DataFrame()
                else:
                    filtered_df = pd.DataFrame([recipe['recipe_data'] for recipe in saved_recipes_list])

        # Search functionality
        search_query = st.text_input("🔍 Search recipes by name, ingredients, or cuisine")
        if search_query:
            search_terms = search_query.lower().split()
            mask = pd.Series(True, index=filtered_df.index)
            for term in search_terms:
                term_mask = (
                    filtered_df['name'].str.lower().str.contains(term, na=False) |
                    filtered_df['ingredients'].str.lower().str.contains(term, na=False) |
                    filtered_df['cuisine'].str.lower().str.contains(term, na=False)
                )
                mask &= term_mask
            filtered_df = filtered_df[mask]

        # Display results count and sorting
        total_recipes = len(filtered_df)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"### Browse your recipes")
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Name (A-Z)", "Name (Z-A)"]
            )
            filtered_df = filtered_df.sort_values(
                'name',
                ascending=(sort_by == "Name (A-Z)")
            )

        # Pagination
        RECIPES_PER_PAGE = 5
        total_pages = (total_recipes + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE
        
        if total_pages > 0:
            page_number = st.select_slider(
                "Page",
                options=range(1, total_pages + 1),
                value=st.session_state.page_number,
                format_func=lambda x: f"Page {x} of {total_pages}"
            )
            st.session_state.page_number = page_number
            
            start_idx = (page_number - 1) * RECIPES_PER_PAGE
            end_idx = min(start_idx + RECIPES_PER_PAGE, total_recipes)
            
            # Display recipes
            for _, recipe in filtered_df.iloc[start_idx:end_idx].iterrows():
                with st.container():
                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                    
                    # Recipe header
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                            <div class="recipe-title">{recipe['name']}</div>
                            <div class="recipe-info">
                                <span>🍽️ {recipe['course']}</span>
                                <span>👨‍🍳 {recipe['cuisine']}</span>
                                <span>🥗 {recipe['diet']}</span>
                                <span>⏱️ {recipe['prep_time']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        is_saved = is_recipe_saved(recipe['name'], current_user)
                        if st.button(
                            "❤️" if is_saved else "🤍",
                            key=f"save_{recipe['name']}"
                        ):
                            if current_user:
                                is_saved = toggle_recipe_save(
                                    recipe['name'],
                                    recipe.to_dict(),
                                    current_user
                                )
                                st.rerun()
                            else:
                                st.warning("Please log in to save recipes")
                    
                    # Description
                    st.markdown(
                        f'<div class="recipe-description">{recipe["description"]}</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Recipe image
                    if pd.notna(recipe.get('image_url')):
                        img = load_image(recipe['image_url'])
                        if img:
                            st.image(img, use_container_width=True)
                    
                    # Recipe details in tabs
                    tabs = st.tabs(["Ingredients", "Instructions"])
                    
                    with tabs[0]:
                        ingredients = parse_ingredients(recipe['ingredients'])
                        if ingredients:
                            st.markdown('<div class="ingredients-grid">', unsafe_allow_html=True)
                            for ing in ingredients:
                                st.markdown(f"""
                                    <div class="ingredient-item">
                                        <div class="ingredient-quantity">{ing['quantity']}</div>
                                        <div class="ingredient-name">{ing['name']}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tabs[1]:
                        instructions = parse_instructions(recipe['instructions'])
                        for i, step in enumerate(instructions, 1):
                            st.markdown(f"""
                                <div class="instruction-step">
                                    <div class="step-number">{i}</div>
                                    {step}
                                </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Pagination controls
            col1, col2, col3 = st.columns([1,2,1])
            with col1:
                if page_number > 1:
                    if st.button("← Previous"):
                        st.session_state.page_number = page_number - 1
                        st.rerun()
            with col3:
                if page_number < total_pages:
                    if st.button("Next →"):
                        st.session_state.page_number = page_number + 1
                        st.rerun()

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure your data file is properly formatted and try again.")