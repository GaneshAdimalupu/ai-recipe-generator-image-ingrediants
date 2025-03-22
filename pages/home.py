import time
from click import prompt
from components.logo import add_logo_with_rotating_text
from home.styles import  load_custom_css
from home.utils import calculate_nutrition, display_recipe_card, img_to_base64, load_lottie_url, predict_from_image
import streamlit as st
from utils.text_generator import load_text_generator
from utils.gemini_recipe_helper import initialize_gemini_model, generate_recipe_from_name, parse_recipe_content

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
                ["Upload Image", "Enter Ingredients", "Recipe Name"],
                horizontal=True,
                format_func=lambda x: "📸 " + x if "Upload" in x else "🥗 " + x if "Ingredients" in x else "📝 " + x,
            )

        if input_method == "Upload Image":
            render_image_upload_section()
        elif input_method == "Enter Ingredients":
            render_ingredient_input_section()
        else:
            render_recipe_name_section()

    # Nutrition Analysis Tab
    with tabs[1]:
        render_nutrition_analysis()

    # Meal Planning Tab
    with tabs[2]:
        render_meal_planning()

def render_recipe_name_section():
    """Render the section for generating recipes by name using Gemini API"""
    st.markdown('<div class="recipe-name-section">', unsafe_allow_html=True)
    
    # Recipe name input
    recipe_name = st.text_input(
        "🍽️ Enter the name of the recipe you want to create",
        placeholder="e.g., Chocolate Lava Cake, Butter Chicken, Vegan Lasagna",
        help="Be specific about the recipe you want to generate"
    )
    
    # Dietary preferences or restrictions
    dietary_options = st.multiselect(
        "Any dietary preferences or restrictions?",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb", "Keto", "Paleo"]
    )
    
    # Cuisine type (optional)
    cuisine_type = st.selectbox(
        "Cuisine type (optional)",
        ["Any", "Italian", "Mexican", "Indian", "Chinese", "Japanese", "American", "Mediterranean", "Thai", "French"]
    )
    
    # Difficulty level
    difficulty = st.select_slider(
        "Difficulty level",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate"
    )
    
    if st.button("🪄 Generate Recipe", type="primary", use_container_width=True):
        if not recipe_name:
            st.error("Please enter a recipe name!")
            return
            
        with st.spinner("✨ Creating your recipe masterpiece..."):
            # Prepare the prompt for Gemini API
            prompt = f"Create a detailed recipe for '{recipe_name}'"
            
            if dietary_options:
                prompt += f" that is {', '.join(dietary_options)}"
                
            if cuisine_type != "Any":
                prompt += f" in {cuisine_type} cuisine style"
                
            prompt += f". The recipe should be {difficulty} level difficulty."
            prompt += " Include a title, ingredients list with measurements, step-by-step instructions, cooking time, preparation time, and comprehensive nutritional information (calories, protein, carbs, fats, etc.)."
            
            # Call the Gemini API to generate the recipe
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.output_parsers import StrOutputParser
                
                # Get the Google API key from Streamlit secrets
                google_api_key = st.secrets["mongo"]["API_KEY"]
                
                # Initialize the Gemini model
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    google_api_key=google_api_key,
                    temperature=0.7
                )
                
                # Generate the recipe
                response = llm.invoke(prompt)
                recipe_text = response.content
                
                # Parse the generated recipe text
                # This is a simplified parser - you might need to adjust based on Gemini's output format
                try:
                    # Extract title, ingredients, and instructions
                    title_match = re.search(r"#+\s*(.*?)\n", recipe_text)
                    title = title_match.group(1) if title_match else recipe_name
                    
                    # Extract ingredients section
                    ingredients_section = re.search(r"(?:Ingredients|INGREDIENTS):(.*?)(?:Instructions|INSTRUCTIONS|Directions|DIRECTIONS|Steps|STEPS)", recipe_text, re.DOTALL)
                    ingredients_text = ingredients_section.group(1) if ingredients_section else ""
                    ingredients = [ing.strip() for ing in re.findall(r"[-•*]\s*(.*?)(?:\n|$)", ingredients_text) if ing.strip()]
                    
                    if not ingredients:  # Try another pattern if the first doesn't work
                        ingredients = [ing.strip() for ing in ingredients_text.split('\n') if ing.strip()]
                    
                    # Extract directions section
                    directions_section = re.search(r"(?:Instructions|INSTRUCTIONS|Directions|DIRECTIONS|Steps|STEPS):(.*?)(?:Nutrition|NUTRITION|Notes|NOTES|$)", recipe_text, re.DOTALL)
                    directions_text = directions_section.group(1) if directions_section else ""
                    directions = [step.strip() for step in re.findall(r"\d+\.\s*(.*?)(?:\n|$)", directions_text) if step.strip()]
                    
                    if not directions:  # Try another pattern if the first doesn't work
                        directions = [step.strip() for step in directions_text.split('\n') if step.strip() and not step.strip().startswith('#')]
                    
                    # Extract nutrition information
                    nutrition_section = re.search(r"(?:Nutrition|NUTRITION|Nutritional Information):(.*?)(?:$)", recipe_text, re.DOTALL)
                    nutrition_text = nutrition_section.group(1) if nutrition_section else ""
                    
                    # Calculate nutrition with either parsed values or from ingredients
                    try:
                        nutrition = calculate_nutrition(ingredients)
                    except:
                        # Default nutrition if calculation fails
                        nutrition = {
                            "calories": "N/A", 
                            "protein": "N/A", 
                            "carbs": "N/A", 
                            "fat": "N/A"
                        }
                    
                    # Create two columns
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### Your Recipe is Ready!")
                        st.markdown(f"## {title}")
                        
                        st.markdown("### Ingredients")
                        for ing in ingredients:
                            st.markdown(f"- {ing}")
                        
                        st.markdown("### Instructions")
                        for i, step in enumerate(directions, 1):
                            st.markdown(f"{i}. {step}")
                    
                    with col2:
                        # Show nutrition info
                        st.markdown("### Nutrition Facts")
                        for nutrient, value in nutrition.items():
                            st.metric(nutrient.capitalize(), f"{value}g" if isinstance(value, (int, float)) else value)
                        
                        # Add additional recipe metadata
                        st.markdown("### Recipe Details")
                        cuisine_display = cuisine_type if cuisine_type != "Any" else "Various"
                        st.markdown(f"**Cuisine:** {cuisine_display}")
                        st.markdown(f"**Difficulty:** {difficulty}")
                        if dietary_options:
                            st.markdown(f"**Dietary:** {', '.join(dietary_options)}")
                        
                        # Show save button
                        if st.button("📥 Save Recipe", key="save_recipe_name"):
                            st.success("Recipe saved successfully!")
                        
                        # Download button
                        recipe_download_text = f"""
                        {title}

                        Ingredients:
                        {chr(10).join(['- ' + ing for ing in ingredients])}

                        Instructions:
                        {chr(10).join([f'{i+1}. {step}' for i, step in enumerate(directions)])}
                        
                        Nutritional Information:
                        {nutrition_text}
                        """
                        
                        safe_title = "".join(x for x in title if x.isalnum() or x in [" ", "-", "_"])
                        filename = f"{safe_title.lower().replace(' ', '_')}_recipe.txt"

                        st.download_button(
                            label="📥 Download Recipe",
                            data=recipe_download_text,
                            file_name=filename,
                            mime="text/plain",
                        )
                
                except Exception as e:
                    # If parsing fails, show the raw recipe text
                    st.markdown("### Your Generated Recipe")
                    st.markdown(recipe_text)
                    st.error(f"Note: Couldn't parse the recipe structure automatically. Showing raw output.")
            
            except Exception as e:
                st.error(f"Error generating recipe: {str(e)}")
                st.error("Please check your API key or try again later.")
    
    st.markdown("</div>", unsafe_allow_html=True)

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
