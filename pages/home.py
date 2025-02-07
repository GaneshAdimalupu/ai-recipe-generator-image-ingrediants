import time
from click import prompt
from components.logo import add_logo_with_rotating_text
from home.styles import  load_custom_css
from home.utils import calculate_nutrition, display_recipe_card, img_to_base64, load_lottie_url, predict_from_image
import streamlit as st
from utils.text_generator import load_text_generator

# Initialize login check
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")

import os
import numpy as np
from pages.widgets import __login__
import plotly.express as px
from streamlit_lottie import st_lottie
from Foodimg2Ing.output import output
from chef_transformer.examples import EXAMPLES
from chef_transformer import dummy, meta
import os
import re
from utils.utils import pure_comma_separation
import json
import streamlit.components.v1 as components


# Initialize login check
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")

def stream_text(text, delay=0.03):
    """Stream text with a typewriter effect"""
    container = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        container.markdown(displayed_text)
        if char in ['.', '!', '?', '\n']:
            time.sleep(delay * 2)  # Longer pause for sentences
        else:
            time.sleep(delay)
    return container

def format_recipe_for_streaming(recipe):
    """Format recipe data into a streamable string"""
    title = f"# {recipe['title']}\n\n"
    ingredients = "## Ingredients\n" + "\n".join([f"* {ing}" for ing in recipe['ingredients']]) + "\n\n"
    directions = "## Instructions\n" + "\n".join([f"{i+1}. {step}" for i, step in enumerate(recipe['directions'])])
    return title + ingredients + directions


def render_home_content():
    # Load custom CSS
    load_custom_css()

    # Main application layout
    st.markdown('<div class="main">', unsafe_allow_html=True)

    # Add logo
    add_logo_with_rotating_text()

    # Centered header with animation
    st.markdown('<h1 class="app-title">🧑‍🍳 Be My Chef AI</h1>', unsafe_allow_html=True)
    st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
    cooking_animation = load_lottie_url(
        "https://assets9.lottiefiles.com/packages/lf20_yfsytba9.json"
    )
    if cooking_animation:
        st_lottie(cooking_animation, height=200)
    st.markdown("</div>", unsafe_allow_html=True)

    # Create tabs
    tabs = st.tabs(["🎨 Recipe Generator", "📊 Nutrition Analysis", "📅 Meal Planning"])

    # Recipe Generator Tab
    with tabs[0]:
        st.markdown("### Generate Your Perfect Recipe")

        input_col1, input_col2 = st.columns([3, 1])
        with input_col1:
            input_method = st.radio(
                "Choose your recipe generation method:",
                ["Upload Image", "Enter Ingredients"],
                horizontal=True,
                format_func=lambda x: "📸 " + x if "Upload" in x else "🥗 " + x,
            )

        if input_method == "Upload Image":
            render_image_upload_section()
        else:
            render_ingredient_input_section()

    # Nutrition Analysis Tab
    with tabs[1]:
        render_nutrition_analysis()

    # Meal Planning Tab
    with tabs[2]:
        render_meal_planning()


def render_image_upload_section():
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload a food image",
        type=["jpg", "jpeg", "png"],
        help="For best results, use a well-lit, clear image of the food",
    )

    if uploaded_file:
        with st.spinner("🔍 Analyzing your delicious image..."):
            title, ingredients, recipe, image_path = predict_from_image(uploaded_file)

            if title is None or ingredients is None or recipe is None:
                st.error("Unable to analyze the image. Please try another one!")
            else:
                handle_recipe_generation(title, ingredients, recipe, image_path)

    st.markdown("</div>", unsafe_allow_html=True)

from utils.text_generator import chef_top, chef_beam, load_text_generator


def render_ingredient_input_section():
    st.markdown('<div class="ingredient-input-section">', unsafe_allow_html=True)
    chef_col1, chef_col2 = st.columns([2, 1])

    with chef_col1:
        st.markdown(meta.HEADER_INFO, unsafe_allow_html=True)
        chef = st.selectbox(
            "👨‍🍳 Select Your Personal Chef",
            ["Chef Scheherazade", "Chef Giovanni"],
            help="Each chef brings their unique culinary expertise",
        )

    with chef_col2:
        st.markdown(meta.CHEF_INFO, unsafe_allow_html=True)

    st.markdown("---")

    prompts = list(EXAMPLES.keys()) + ["Custom"]
    prompt = st.selectbox("🔍 Choose a Recipe Template or Create Your Own", prompts)

    items = st.text_area(
        "🥗 List Your Ingredients",
        value=EXAMPLES[prompt] if prompt != "Custom" else "",
        help="Separate ingredients with commas (e.g., chicken, rice, tomatoes)",
        height=100,
    )

    if st.button("🪄 Generate My Recipe", type="primary", use_container_width=True):
        with st.spinner("👨‍🍳 Creating your culinary masterpiece..."):
            generator = load_text_generator()
            generation_params = chef_top if chef == "Chef Scheherazade" else chef_beam

            # Convert list to comma-separated string
            clean_items = pure_comma_separation(items, return_list=False)
            if not clean_items:
                st.error("Please enter valid ingredients!")
                return

            recipe = generator.generate(clean_items, generation_params)

            if recipe:
                nutrition = calculate_nutrition(recipe["ingredients"])
                # Create two columns
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("### Your Recipe is Being Written...")
                    formatted_recipe = format_recipe_for_streaming(recipe)
                    recipe_container = stream_text(formatted_recipe)
                
                with col2:
                    # Show nutrition info
                    st.markdown("### Nutrition Facts")
                    for nutrient, value in nutrition.items():
                        st.metric(nutrient.capitalize(), f"{value}g")
                    
                    # Show save button after streaming is complete
                    if st.button("📥 Save Recipe", key="save_recipe"):
                        # Add your save functionality here
                        st.success("Recipe saved successfully!")
            else:
                st.error("Failed to generate recipe. Please try again.")


def render_nutrition_analysis():
    st.markdown("### 📊 Nutrition Analysis")
    selected_ingredients = st.multiselect(
        "Select ingredients to analyze:",
        ["Chicken", "Rice", "Vegetables", "Fish", "Beef", "Pasta"],
    )

    if selected_ingredients:
        nutrition = calculate_nutrition(selected_ingredients)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
            for nutrient, value in nutrition.items():
                st.metric(nutrient.capitalize(), f"{value}g")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
            fig = px.pie(
                values=list(nutrition.values()),
                names=list(nutrition.keys()),
                title="Nutritional Breakdown",
                hole=0.3,
            )
            st.plotly_chart(fig)
            st.markdown("</div>", unsafe_allow_html=True)


def render_meal_planning():
    st.markdown("### 📅 Weekly Meal Planner")
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    meals = ["Breakfast", "Lunch", "Dinner"]

    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        selected_day = st.selectbox("Select day:", days)
    with col2:
        selected_meal = st.selectbox("Select meal:", meals)

    if st.button("🔮 Generate meal suggestion", use_container_width=True):
        with st.spinner("Planning your meal..."):
            generator = load_text_generator()
            recipe = generator.generate("healthy " + selected_meal.lower(), {})
            if recipe:
                nutrition = calculate_nutrition(recipe["ingredients"])
                display_recipe_card(
                    recipe["title"],
                    recipe["ingredients"],
                    recipe["directions"],
                    nutrition,
                )


def handle_recipe_generation(title, ingredients, recipe, image_path):
    if not ingredients:
        st.warning("No ingredients detected. Generating a basic recipe...")
        ingredients = ["Main ingredient"]

    if not recipe:
        st.warning("No recipe steps detected. Generating basic steps...")
        recipe = ["Prepare ingredients", "Cook according to preference"]

    nutrition = calculate_nutrition(ingredients)

    if image_path:
        st.image(image_path, use_container_width=True)

    display_recipe_card(title, ingredients, recipe, nutrition, image_path)

    recipe_text = f"""
    {title}

    Ingredients:
    {chr(10).join(['- ' + ing for ing in ingredients])}

    Instructions:
    {chr(10).join([f'{i+1}. {step}' for i, step in enumerate(recipe)])}
    """
    safe_title = "".join(x for x in title if x.isalnum() or x in [" ", "-", "_"])
    filename = f"{safe_title.lower().replace(' ', '_')}_recipe.txt"

    st.download_button(
        label="📥 Download Recipe",
        data=recipe_text,
        file_name=filename,
        mime="text/plain",
    )


if __name__ == "__main__":
    # Check login state
    if not st.session_state.get("LOGGED_IN", False):
        st.switch_page("streamlit_app.py")

    # Initialize login UI
    from pages.widgets import __login__

    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
    )

    # Show navigation
    login_ui.nav_sidebar()

    # Render content
    render_home_content()
