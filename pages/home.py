import time
from click import prompt
from components.logo import add_logo_with_rotating_text
from home.nutrition_meal import analyze_ingredients_nutrition, render_meal_planning_main, render_nutrition_analysis_main
from home.styles import  load_custom_css
from home.utils import calculate_nutrition, display_recipe_card, load_lottie_url, predict_from_image
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
                ["Upload Image", "Enter Ingredients","Recipe Name"],
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
def estimate_nutrition_from_ingredients(ingredients, recipe_name):
    """Generate realistic nutrition estimates based on ingredients and recipe type"""
    import random
    
    # Default nutrition ranges based on recipe type
    nutrition_ranges = {
        "pasta": {"calories": (300, 600), "protein": (8, 20), "carbs": (40, 80), "fat": (8, 25), "fiber": (2, 6)},
        "salad": {"calories": (150, 350), "protein": (5, 15), "carbs": (10, 30), "fat": (7, 20), "fiber": (3, 8)},
        "soup": {"calories": (150, 300), "protein": (6, 15), "carbs": (15, 30), "fat": (5, 15), "fiber": (2, 6)},
        "dessert": {"calories": (200, 500), "protein": (2, 8), "carbs": (30, 70), "fat": (8, 25), "fiber": (1, 4)},
        "breakfast": {"calories": (250, 450), "protein": (10, 25), "carbs": (20, 45), "fat": (10, 20), "fiber": (2, 7)},
        "meat": {"calories": (300, 600), "protein": (25, 50), "carbs": (5, 20), "fat": (15, 35), "fiber": (1, 4)},
        "fish": {"calories": (200, 400), "protein": (20, 35), "carbs": (5, 15), "fat": (8, 20), "fiber": (1, 3)},
        "vegetarian": {"calories": (250, 450), "protein": (8, 20), "carbs": (30, 60), "fat": (10, 20), "fiber": (5, 12)},
        "vegan": {"calories": (250, 450), "protein": (8, 18), "carbs": (30, 60), "fat": (8, 18), "fiber": (6, 14)},
        "default": {"calories": (250, 450), "protein": (10, 25), "carbs": (20, 45), "fat": (8, 20), "fiber": (3, 8)}
    }
    
    # Determine recipe type from name and ingredients
    recipe_type = "default"
    recipe_name_lower = recipe_name.lower()
    
    ingredient_text = " ".join(ingredients).lower()
    
    # Check recipe name and ingredients for keywords
    if any(word in recipe_name_lower for word in ["pasta", "noodle", "spaghetti", "fettuccine", "macaroni"]) or \
       any(word in ingredient_text for word in ["pasta", "noodle", "spaghetti", "fettuccine", "macaroni"]):
        recipe_type = "pasta"
    elif any(word in recipe_name_lower for word in ["salad", "greens", "bowl"]) or \
         any(word in ingredient_text for word in ["lettuce", "spinach", "arugula", "salad"]):
        recipe_type = "salad"
    elif any(word in recipe_name_lower for word in ["soup", "stew", "chowder", "broth"]) or \
         any(word in ingredient_text for word in ["broth", "stock", "soup"]):
        recipe_type = "soup"
    elif any(word in recipe_name_lower for word in ["cake", "pie", "cookie", "dessert", "sweet", "chocolate"]) or \
         any(word in ingredient_text for word in ["sugar", "chocolate", "vanilla", "cream", "cookie"]):
        recipe_type = "dessert"
    elif any(word in recipe_name_lower for word in ["breakfast", "omelette", "pancake", "waffle", "eggs"]) or \
         any(word in ingredient_text for word in ["egg", "oats", "granola", "breakfast"]):
        recipe_type = "breakfast"
    elif any(word in recipe_name_lower for word in ["chicken", "beef", "pork", "steak", "turkey", "meat"]) or \
         any(word in ingredient_text for word in ["chicken", "beef", "pork", "steak", "turkey", "ground meat"]):
        recipe_type = "meat"
    elif any(word in recipe_name_lower for word in ["fish", "salmon", "tuna", "cod", "seafood", "shrimp"]) or \
         any(word in ingredient_text for word in ["fish", "salmon", "tuna", "cod", "seafood", "shrimp"]):
        recipe_type = "fish"
    elif any(word in recipe_name_lower for word in ["vegetarian", "veggie"]) or \
         (not any(meat in ingredient_text for meat in ["chicken", "beef", "pork", "fish", "meat", "salmon", "shrimp"])):
        recipe_type = "vegetarian"
    elif any(word in recipe_name_lower for word in ["vegan", "plant-based"]) or \
         not any(animal in ingredient_text for animal in ["meat", "chicken", "fish", "egg", "milk", "cheese", "cream", "butter", "yogurt"]):
        recipe_type = "vegan"
    
    # Get appropriate ranges for recipe type
    ranges = nutrition_ranges.get(recipe_type, nutrition_ranges["default"])
    
    # Calculate per-serving values based on ingredient count
    ingredient_factor = min(1.5, max(0.8, len(ingredients) / 10))  # Scale based on number of ingredients
    
    # Generate nutrition values
    return {
        "calories": str(int(random.uniform(ranges["calories"][0], ranges["calories"][1]) * ingredient_factor)),
        "protein": str(round(random.uniform(ranges["protein"][0], ranges["protein"][1]) * ingredient_factor, 1)),
        "carbs": str(round(random.uniform(ranges["carbs"][0], ranges["carbs"][1]) * ingredient_factor, 1)),
        "fat": str(round(random.uniform(ranges["fat"][0], ranges["fat"][1]) * ingredient_factor, 1)),
        "fiber": str(round(random.uniform(ranges["fiber"][0], ranges["fiber"][1]) * ingredient_factor, 1))
    }

def generate_sample_recipes(recipe_name, num_variations):
    """Generate sample recipes for testing purposes when API is unavailable"""
    recipes = []
    
    variations = [
        {
            "title": f"Creamy Garlic Parmesan {recipe_name} - Variation 1",
            "ingredients": [
                "8 oz pasta, dried",
                "4 tbsp butter",
                "3 cloves garlic, minced",
                "1 cup heavy cream",
                "1/2 cup grated Parmesan cheese",
                "1/4 cup chopped fresh parsley",
                "Salt and black pepper to taste"
            ],
            "instructions": [
                "Cook pasta according to package directions. Drain and set aside.",
                "While pasta cooks, melt butter in a large skillet over medium heat. Add garlic and cook until fragrant (about 1 minute).",
                "Pour in heavy cream and bring to a simmer. Reduce heat to low and cook for 5 minutes, stirring occasionally.",
                "Stir in Parmesan cheese until melted and sauce is smooth. Season with salt and pepper to taste.",
                "Add cooked pasta to the sauce and toss to coat.",
                "Garnish with fresh parsley and serve immediately."
            ],
            "prep_time": "5 minutes",
            "cook_time": "15 minutes",
            "servings": "2"
        },
        {
            "title": f"Spicy Peanut {recipe_name} - Variation 2",
            "ingredients": [
                "8 oz spaghetti, dried",
                "1/4 cup peanut butter",
                "2 tbsp soy sauce",
                "1 tbsp rice vinegar",
                "1 tbsp sesame oil",
                "1 tbsp honey",
                "1 tsp sriracha (or more, to taste)",
                "1/4 cup chopped green onions",
                "1/4 cup chopped peanuts (for garnish)"
            ],
            "instructions": [
                "Cook spaghetti according to package directions. Drain and set aside.",
                "While pasta cooks, whisk together peanut butter, soy sauce, rice vinegar, sesame oil, honey, and sriracha in a bowl until smooth.",
                "Add cooked spaghetti to the sauce and toss to coat.",
                "Garnish with green onions and chopped peanuts. Serve immediately."
            ],
            "prep_time": "5 minutes",
            "cook_time": "10 minutes",
            "servings": "2"
        },
        {
            "title": f"Mediterranean {recipe_name} with Lemon and Herbs - Variation 3",
            "ingredients": [
                "8 oz pasta, dried",
                "3 tbsp olive oil",
                "2 cloves garlic, minced",
                "1 lemon, zested and juiced",
                "1/3 cup kalamata olives, sliced",
                "1/4 cup chopped fresh herbs (parsley, basil, oregano)",
                "1/3 cup crumbled feta cheese",
                "1/4 cup sun-dried tomatoes, chopped",
                "Salt and pepper to taste"
            ],
            "instructions": [
                "Cook pasta according to package directions. Drain and reserve 1/4 cup pasta water.",
                "In a large bowl, combine olive oil, garlic, lemon zest, and lemon juice.",
                "Add hot cooked pasta and toss. Add reserved pasta water as needed to create a light sauce.",
                "Fold in olives, herbs, feta cheese, and sun-dried tomatoes.",
                "Season with salt and pepper to taste.",
                "Serve warm or at room temperature."
            ],
            "prep_time": "10 minutes",
            "cook_time": "12 minutes",
            "servings": "2"
        },
        {
            "title": f"One-Pot {recipe_name} with Vegetables - Variation 4",
            "ingredients": [
                "8 oz pasta",
                "2 cups vegetable broth",
                "1 can (14 oz) diced tomatoes",
                "1 medium zucchini, chopped",
                "1 bell pepper, chopped",
                "1 small onion, diced",
                "2 cloves garlic, minced",
                "1 tsp Italian seasoning",
                "2 tbsp olive oil",
                "1/3 cup grated Parmesan cheese",
                "Fresh basil for garnish"
            ],
            "instructions": [
                "In a large pot, heat olive oil over medium heat. Add onions and cook until translucent, about 3 minutes.",
                "Add garlic and cook for 30 seconds until fragrant.",
                "Add uncooked pasta, vegetable broth, diced tomatoes (with juice), zucchini, bell pepper, and Italian seasoning.",
                "Bring to a boil, then reduce heat to low. Cover and simmer for 10-12 minutes, stirring occasionally, until pasta is tender and most liquid is absorbed.",
                "Remove from heat and stir in Parmesan cheese.",
                "Let stand for 5 minutes to thicken, then garnish with fresh basil before serving."
            ],
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "servings": "4"
        }
    ]
    
    # Format the sample recipes into a structured multi-recipe response
    formatted_recipes = []
    for i in range(min(num_variations, len(variations))):
        variation = variations[i]
        recipe_text = f"# {variation['title']}\n\n"
        recipe_text += "## Ingredients:\n"
        for ingredient in variation["ingredients"]:
            recipe_text += f"- {ingredient}\n"
        recipe_text += "\n## Instructions:\n"
        for j, instruction in enumerate(variation["instructions"], 1):
            recipe_text += f"{j}. {instruction}\n"
        recipe_text += f"\n## Recipe Details:\n"
        recipe_text += f"- Prep Time: {variation['prep_time']}\n"
        recipe_text += f"- Cook Time: {variation['cook_time']}\n"
        recipe_text += f"- Servings: {variation['servings']}\n"
        formatted_recipes.append(recipe_text)
    
    return "\n\n".join(formatted_recipes)

def estimate_nutrition_from_ingredients(ingredients, recipe_name):
    """Generate realistic nutrition estimates based on ingredients and recipe type"""
    import random
    
    # Default nutrition ranges based on recipe type
    nutrition_ranges = {
        "pasta": {"calories": (300, 600), "protein": (8, 20), "carbs": (40, 80), "fat": (8, 25), "fiber": (2, 6)},
        "salad": {"calories": (150, 350), "protein": (5, 15), "carbs": (10, 30), "fat": (7, 20), "fiber": (3, 8)},
        "soup": {"calories": (150, 300), "protein": (6, 15), "carbs": (15, 30), "fat": (5, 15), "fiber": (2, 6)},
        "dessert": {"calories": (200, 500), "protein": (2, 8), "carbs": (30, 70), "fat": (8, 25), "fiber": (1, 4)},
        "breakfast": {"calories": (250, 450), "protein": (10, 25), "carbs": (20, 45), "fat": (10, 20), "fiber": (2, 7)},
        "meat": {"calories": (300, 600), "protein": (25, 50), "carbs": (5, 20), "fat": (15, 35), "fiber": (1, 4)},
        "fish": {"calories": (200, 400), "protein": (20, 35), "carbs": (5, 15), "fat": (8, 20), "fiber": (1, 3)},
        "vegetarian": {"calories": (250, 450), "protein": (8, 20), "carbs": (30, 60), "fat": (10, 20), "fiber": (5, 12)},
        "vegan": {"calories": (250, 450), "protein": (8, 18), "carbs": (30, 60), "fat": (8, 18), "fiber": (6, 14)},
        "default": {"calories": (250, 450), "protein": (10, 25), "carbs": (20, 45), "fat": (8, 20), "fiber": (3, 8)}
    }
    
    # Determine recipe type from name and ingredients
    recipe_type = "default"
    recipe_name_lower = recipe_name.lower()
    
    ingredient_text = " ".join(ingredients).lower()
    
    # Check recipe name and ingredients for keywords
    if any(word in recipe_name_lower for word in ["pasta", "noodle", "spaghetti", "fettuccine", "macaroni"]) or \
       any(word in ingredient_text for word in ["pasta", "noodle", "spaghetti", "fettuccine", "macaroni"]):
        recipe_type = "pasta"
    elif any(word in recipe_name_lower for word in ["salad", "greens", "bowl"]) or \
         any(word in ingredient_text for word in ["lettuce", "spinach", "arugula", "salad"]):
        recipe_type = "salad"
    elif any(word in recipe_name_lower for word in ["soup", "stew", "chowder", "broth"]) or \
         any(word in ingredient_text for word in ["broth", "stock", "soup"]):
        recipe_type = "soup"
    elif any(word in recipe_name_lower for word in ["cake", "pie", "cookie", "dessert", "sweet", "chocolate"]) or \
         any(word in ingredient_text for word in ["sugar", "chocolate", "vanilla", "cream", "cookie"]):
        recipe_type = "dessert"
    elif any(word in recipe_name_lower for word in ["breakfast", "omelette", "pancake", "waffle", "eggs"]) or \
         any(word in ingredient_text for word in ["egg", "oats", "granola", "breakfast"]):
        recipe_type = "breakfast"
    elif any(word in recipe_name_lower for word in ["chicken", "beef", "pork", "steak", "turkey", "meat"]) or \
         any(word in ingredient_text for word in ["chicken", "beef", "pork", "steak", "turkey", "ground meat"]):
        recipe_type = "meat"
    elif any(word in recipe_name_lower for word in ["fish", "salmon", "tuna", "cod", "seafood", "shrimp"]) or \
         any(word in ingredient_text for word in ["fish", "salmon", "tuna", "cod", "seafood", "shrimp"]):
        recipe_type = "fish"
    elif any(word in recipe_name_lower for word in ["vegetarian", "veggie"]) or \
         (not any(meat in ingredient_text for meat in ["chicken", "beef", "pork", "fish", "meat", "salmon", "shrimp"])):
        recipe_type = "vegetarian"
    elif any(word in recipe_name_lower for word in ["vegan", "plant-based"]) or \
         not any(animal in ingredient_text for animal in ["meat", "chicken", "fish", "egg", "milk", "cheese", "cream", "butter", "yogurt"]):
        recipe_type = "vegan"
    
    # Get appropriate ranges for recipe type
    ranges = nutrition_ranges.get(recipe_type, nutrition_ranges["default"])
    
    # Calculate per-serving values based on ingredient count
    ingredient_factor = min(1.5, max(0.8, len(ingredients) / 10))  # Scale based on number of ingredients
    
    # Generate nutrition values
    return {
        "calories": str(int(random.uniform(ranges["calories"][0], ranges["calories"][1]) * ingredient_factor)),
        "protein": str(round(random.uniform(ranges["protein"][0], ranges["protein"][1]) * ingredient_factor, 1)),
        "carbs": str(round(random.uniform(ranges["carbs"][0], ranges["carbs"][1]) * ingredient_factor, 1)),
        "fat": str(round(random.uniform(ranges["fat"][0], ranges["fat"][1]) * ingredient_factor, 1)),
        "fiber": str(round(random.uniform(ranges["fiber"][0], ranges["fiber"][1]) * ingredient_factor, 1))
    }

def generate_sample_recipes(recipe_name, num_variations):
    """Generate sample recipes for testing purposes when API is unavailable"""
    recipes = []
    
    variations = [
        {
            "title": f"Creamy Garlic Parmesan {recipe_name} - Variation 1",
            "ingredients": [
                "8 oz pasta, dried",
                "4 tbsp butter",
                "3 cloves garlic, minced",
                "1 cup heavy cream",
                "1/2 cup grated Parmesan cheese",
                "1/4 cup chopped fresh parsley",
                "Salt and black pepper to taste"
            ],
            "instructions": [
                "Cook pasta according to package directions. Drain and set aside.",
                "While pasta cooks, melt butter in a large skillet over medium heat. Add garlic and cook until fragrant (about 1 minute).",
                "Pour in heavy cream and bring to a simmer. Reduce heat to low and cook for 5 minutes, stirring occasionally.",
                "Stir in Parmesan cheese until melted and sauce is smooth. Season with salt and pepper to taste.",
                "Add cooked pasta to the sauce and toss to coat.",
                "Garnish with fresh parsley and serve immediately."
            ],
            "prep_time": "5 minutes",
            "cook_time": "15 minutes",
            "servings": "2"
        },
        {
            "title": f"Spicy Peanut {recipe_name} - Variation 2",
            "ingredients": [
                "8 oz spaghetti, dried",
                "1/4 cup peanut butter",
                "2 tbsp soy sauce",
                "1 tbsp rice vinegar",
                "1 tbsp sesame oil",
                "1 tbsp honey",
                "1 tsp sriracha (or more, to taste)",
                "1/4 cup chopped green onions",
                "1/4 cup chopped peanuts (for garnish)"
            ],
            "instructions": [
                "Cook spaghetti according to package directions. Drain and set aside.",
                "While pasta cooks, whisk together peanut butter, soy sauce, rice vinegar, sesame oil, honey, and sriracha in a bowl until smooth.",
                "Add cooked spaghetti to the sauce and toss to coat.",
                "Garnish with green onions and chopped peanuts. Serve immediately."
            ],
            "prep_time": "5 minutes",
            "cook_time": "10 minutes",
            "servings": "2"
        },
        {
            "title": f"Mediterranean {recipe_name} with Lemon and Herbs - Variation 3",
            "ingredients": [
                "8 oz pasta, dried",
                "3 tbsp olive oil",
                "2 cloves garlic, minced",
                "1 lemon, zested and juiced",
                "1/3 cup kalamata olives, sliced",
                "1/4 cup chopped fresh herbs (parsley, basil, oregano)",
                "1/3 cup crumbled feta cheese",
                "1/4 cup sun-dried tomatoes, chopped",
                "Salt and pepper to taste"
            ],
            "instructions": [
                "Cook pasta according to package directions. Drain and reserve 1/4 cup pasta water.",
                "In a large bowl, combine olive oil, garlic, lemon zest, and lemon juice.",
                "Add hot cooked pasta and toss. Add reserved pasta water as needed to create a light sauce.",
                "Fold in olives, herbs, feta cheese, and sun-dried tomatoes.",
                "Season with salt and pepper to taste.",
                "Serve warm or at room temperature."
            ],
            "prep_time": "10 minutes",
            "cook_time": "12 minutes",
            "servings": "2"
        },
        {
            "title": f"One-Pot {recipe_name} with Vegetables - Variation 4",
            "ingredients": [
                "8 oz pasta",
                "2 cups vegetable broth",
                "1 can (14 oz) diced tomatoes",
                "1 medium zucchini, chopped",
                "1 bell pepper, chopped",
                "1 small onion, diced",
                "2 cloves garlic, minced",
                "1 tsp Italian seasoning",
                "2 tbsp olive oil",
                "1/3 cup grated Parmesan cheese",
                "Fresh basil for garnish"
            ],
            "instructions": [
                "In a large pot, heat olive oil over medium heat. Add onions and cook until translucent, about 3 minutes.",
                "Add garlic and cook for 30 seconds until fragrant.",
                "Add uncooked pasta, vegetable broth, diced tomatoes (with juice), zucchini, bell pepper, and Italian seasoning.",
                "Bring to a boil, then reduce heat to low. Cover and simmer for 10-12 minutes, stirring occasionally, until pasta is tender and most liquid is absorbed.",
                "Remove from heat and stir in Parmesan cheese.",
                "Let stand for 5 minutes to thicken, then garnish with fresh basil before serving."
            ],
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "servings": "4"
        }
    ]
    
    # Format the sample recipes into a structured multi-recipe response
    formatted_recipes = []
    for i in range(min(num_variations, len(variations))):
        variation = variations[i]
        recipe_text = f"# {variation['title']}\n\n"
        recipe_text += "## Ingredients:\n"
        for ingredient in variation["ingredients"]:
            recipe_text += f"- {ingredient}\n"
        recipe_text += "\n## Instructions:\n"
        for j, instruction in enumerate(variation["instructions"], 1):
            recipe_text += f"{j}. {instruction}\n"
        recipe_text += f"\n## Recipe Details:\n"
        recipe_text += f"- Prep Time: {variation['prep_time']}\n"
        recipe_text += f"- Cook Time: {variation['cook_time']}\n"
        recipe_text += f"- Servings: {variation['servings']}\n"
        formatted_recipes.append(recipe_text)
    
    return "\n\n".join(formatted_recipes)

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
    
    # Number of recipe variations
    num_variations = st.slider(
        "Number of recipe variations to generate",
        min_value=1,
        max_value=4,
        value=3,
        step=1,
        help="Generate multiple variations of the recipe"
    )
    
    # Hide option for nutrition value estimation (will always use estimation)
    estimation_option = "Estimate nutrition values"
    
    if st.button("🪄 Generate Recipe", type="primary", use_container_width=True):
        if not recipe_name:
            st.error("Please enter a recipe name!")
            return
            
        with st.spinner(f"✨ Creating {num_variations} recipe variations..."):
            # Prepare the prompt for Gemini API
            prompt = f"""Create {num_variations} different variations of recipes for '{recipe_name}'.

I need a full disclaimer at the beginning of your response about nutrition information: "It's impossible for me to provide EXACT nutrition values without lab analysis of the finished dishes. Nutrition information varies significantly based on specific ingredient brands, portion sizes, and cooking methods. Therefore, I will provide estimated values based on generic data and common serving sizes, and I strongly recommend using a nutrition calculator with specific ingredient details for more accurate results."

For EACH recipe variation, structure your response with clear headers in this exact format:

# [Recipe Title - Variation #]

## Ingredients:
- [ingredient 1 with precise measurement]
- [ingredient 2 with precise measurement]
(etc.)

## Instructions:
1. [Step 1]
2. [Step 2]
(etc.)

## Nutrition Information:
- Calories: [estimated number]
- Protein: [estimated number]g
- Carbs: [estimated number]g
- Fat: [estimated number]g
- Fiber: [estimated number]g

## Recipe Details:
- Prep Time: [time in minutes]
- Cook Time: [time in minutes]
- Servings: [number]

Make sure each variation has different ingredients or techniques. Provide reasonable estimated nutrition values for each variation.
"""
            
            if dietary_options:
                prompt += f"\nEach recipe must be {', '.join(dietary_options)}."
                
            if cuisine_type != "Any":
                prompt += f"\nEach recipe should be prepared in {cuisine_type} cuisine style."
                
            prompt += f"\nAll recipes should be suitable for {difficulty} level home cooks."
            
            # Call the Gemini API to generate the recipe
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                # Get the Google API key from Streamlit secrets
                google_api_key = st.secrets["mongo"]["API_KEY"]
                
                # Initialize the Gemini model
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    google_api_key=google_api_key,
                    temperature=0.7,
                    max_output_tokens=8192  # Increase output length for multiple recipes
                )
                
                # Generate the recipes
                response = llm.invoke(prompt)
                full_response = response.content
                
                # For development/testing purposes, if API fails, use sample data
                if not full_response or "error" in full_response.lower():
                    # Sample test data for development purposes
                    full_response = generate_sample_recipes(recipe_name, num_variations)
                
                # Split the response into individual recipes
                import re
                
                # Split by top-level headers (Recipe titles)
                recipe_sections = re.split(r'^#\s+', full_response, flags=re.MULTILINE)
                # Remove any empty sections
                recipe_sections = [s for s in recipe_sections if s.strip()]
                
                # Create tabs for the different recipe variations
                # Check if there's a disclaimer at the beginning of the response
                disclaimer = ""
                if "impossible" in full_response.lower() and "nutrition" in full_response.lower() and "values" in full_response.lower():
                    disclaimer_match = re.search(r"(It's impossible.*?results\.)", full_response, re.DOTALL | re.IGNORECASE)
                    if disclaimer_match:
                        disclaimer = disclaimer_match.group(1)
                        # Remove the disclaimer from parsing
                        full_response = full_response.replace(disclaimer, "")
                
                # Re-split after removing disclaimer
                recipe_sections = re.split(r'^#\s+', full_response, flags=re.MULTILINE)
                recipe_sections = [s for s in recipe_sections if s.strip()]
                
                if recipe_sections:
                    tabs = st.tabs([f"Recipe {i+1}" for i in range(min(len(recipe_sections), num_variations))])
                    
                    # Process each recipe section
                    for i, (tab, recipe_text) in enumerate(zip(tabs, recipe_sections[:num_variations])):
                        with tab:
                            try:
                                # Add the header back for proper parsing
                                recipe_text = "# " + recipe_text
                                
                                # Extract title (looking for markdown headers)
                                title_match = re.search(r"#\s*(.*?)(?:\n|$)", recipe_text)
                                title = title_match.group(1).strip() if title_match else f"{recipe_name} Variation {i+1}"
                                
                                # Extract ingredients
                                ingredients_match = re.search(r"##\s*Ingredients:?.*?\n(.*?)(?:##|$)", 
                                                         recipe_text, re.DOTALL)
                                ingredients_text = ingredients_match.group(1) if ingredients_match else ""
                                ingredients = [line.strip() for line in re.findall(r"[-*•]\s*(.*?)(?:\n|$)", ingredients_text) 
                                           if line.strip()]
                                if not ingredients:
                                    ingredients = [line.strip() for line in ingredients_text.split('\n') 
                                               if line.strip() and not line.startswith('#')]
                                
                                # Extract instructions
                                instructions_match = re.search(r"##\s*Instructions:?.*?\n(.*?)(?:##|$)", 
                                                          recipe_text, re.DOTALL)
                                instructions_text = instructions_match.group(1) if instructions_match else ""
                                instructions = [step.strip() for step in re.findall(r"\d+\.\s*(.*?)(?:\n|$)", instructions_text) 
                                            if step.strip()]
                                if not instructions:
                                    instructions = [line.strip() for line in instructions_text.split('\n') 
                                                if line.strip() and not line.startswith('#')]
                                
                                # Extract or estimate nutrition information
                                if estimation_option == "Estimate nutrition values":
                                    # Generate realistic nutrition values based on ingredients
                                    nutrition = estimate_nutrition_from_ingredients(ingredients, title)
                                else:
                                    # Use placeholder values
                                    nutrition = {
                                        "calories": "0",
                                        "protein": "0",
                                        "carbs": "0",
                                        "fat": "0",
                                        "fiber": "0"
                                    }
                                
                                # Try to extract nutrition from the text if available
                                nutrition_match = re.search(r"##\s*Nutrition Information:?.*?\n(.*?)(?:##|$)", 
                                                       recipe_text, re.DOTALL)
                                if nutrition_match:
                                    nutrition_text = nutrition_match.group(1)
                                    
                                    # Extract each nutrition value only if estimation option is not selected
                                    if estimation_option != "Estimate nutrition values":
                                        calories_match = re.search(r"[cC]alories:?\s*(\d+(?:\.\d+)?)", nutrition_text)
                                        if calories_match:
                                            nutrition["calories"] = calories_match.group(1)
                                        
                                        protein_match = re.search(r"[pP]rotein:?\s*(\d+(?:\.\d+)?)\s*g", nutrition_text)
                                        if protein_match:
                                            nutrition["protein"] = protein_match.group(1)
                                        
                                        carbs_match = re.search(r"[cC]arbs:?\s*(\d+(?:\.\d+)?)\s*g", nutrition_text)
                                        if carbs_match:
                                            nutrition["carbs"] = carbs_match.group(1)
                                        
                                        fat_match = re.search(r"[fF]at:?\s*(\d+(?:\.\d+)?)\s*g", nutrition_text)
                                        if fat_match:
                                            nutrition["fat"] = fat_match.group(1)
                                        
                                        fiber_match = re.search(r"[fF]iber:?\s*(\d+(?:\.\d+)?)\s*g", nutrition_text)
                                        if fiber_match:
                                            nutrition["fiber"] = fiber_match.group(1)
                                
                                # Extract recipe details
                                recipe_details = {
                                    "prep_time": "N/A",
                                    "cook_time": "N/A",
                                    "servings": "N/A"
                                }
                                
                                details_match = re.search(r"##\s*Recipe Details:?.*?\n(.*?)(?:##|$)", 
                                                     recipe_text, re.DOTALL)
                                if details_match:
                                    details_text = details_match.group(1)
                                    
                                    prep_time_match = re.search(r"[pP]rep\s*[tT]ime:?\s*([^\n,]+)", details_text)
                                    if prep_time_match:
                                        recipe_details["prep_time"] = prep_time_match.group(1).strip()
                                    
                                    cook_time_match = re.search(r"[cC]ook\s*[tT]ime:?\s*([^\n,]+)", details_text)
                                    if cook_time_match:
                                        recipe_details["cook_time"] = cook_time_match.group(1).strip()
                                    
                                    servings_match = re.search(r"[sS]ervings:?\s*([^\n,]+)", details_text)
                                    if servings_match:
                                        recipe_details["servings"] = servings_match.group(1).strip()
                                
                                # Create recipe display with enhanced styling
                                st.markdown(f"""
                                <div class="recipe-card">
                                    <h1 class="recipe-title">{title}</h1>
                                    <div class="recipe-meta">
                                        <span class="recipe-meta-item">⏱️ Prep: {recipe_details['prep_time']}</span>
                                        <span class="recipe-meta-item">🍳 Cook: {recipe_details['cook_time']}</span>
                                        <span class="recipe-meta-item">👥 Serves: {recipe_details['servings']}</span>
                                        <span class="recipe-meta-item">📊 Difficulty: {difficulty}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Create two columns for ingredients and instructions
                                col1, col2 = st.columns([1, 1])
                                
                                with col1:
                                    st.markdown("### Ingredients")
                                    for ing in ingredients:
                                        st.markdown(f"""
                                        <div class="ingredient-item">
                                            <span class="ingredient-icon">🍽️</span>
                                            <span class="ingredient-text">{ing}</span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                # Add nutrition section with accurate values
                                st.markdown("### Nutrition Facts")
                                
                                # Add disclaimer about nutrition values
                                st.info("⚠️ Nutrition values are estimates based on standard ingredients. Actual values may vary depending on specific brands and preparation methods.")
                                
                                # Create layout for displaying nutrition values
                                st.markdown("<div class='nutrition-grid'>", unsafe_allow_html=True)
                                
                                # Calories
                                st.markdown(f"""
                                    <div class='nutrition-item'>
                                        <div class='nutrition-label'>Calories</div>
                                        <div class='nutrition-value'>{nutrition['calories']}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Other nutrients with their units
                                nutrient_data = [
                                        {"name": "Carbs", "value": nutrition['carbs'], "unit": "g"},
                                        {"name": "Protein", "value": nutrition['protein'], "unit": "g"},
                                        {"name": "Fat", "value": nutrition['fat'], "unit": "g"},
                                        {"name": "Fiber", "value": nutrition['fiber'], "unit": "g"}
                                    ]
                                    
                                for nutrient in nutrient_data:
                                        st.markdown(f"""
                                        <div class='nutrition-item'>
                                            <div class='nutrition-label'>{nutrient['name']}</div>
                                            <div class='nutrition-value'>{nutrient['value']}{nutrient['unit']}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown("### Instructions")
                                    for i, step in enumerate(instructions, 1):
                                        st.markdown(f"""
                                        <div class="instruction-step">
                                            <div class="step-number">{i}</div>
                                            <div class="step-text">{step}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                # Create download button with formatted recipe
                                recipe_download_text = f"""
# {title}

## Recipe Details
- Difficulty: {difficulty}
- Prep Time: {recipe_details['prep_time']}
- Cook Time: {recipe_details['cook_time']}
- Servings: {recipe_details['servings']}

## Ingredients
{chr(10).join(['- ' + ing for ing in ingredients])}

## Instructions
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(instructions)])}

## Nutrition Information
- Calories: {nutrition['calories']}
- Protein: {nutrition['protein']}g
- Carbs: {nutrition['carbs']}g
- Fat: {nutrition['fat']}g
- Fiber: {nutrition['fiber']}g
"""
                                
                                safe_title = "".join(x for x in title if x.isalnum() or x in [" ", "-", "_"])
                                filename = f"{safe_title.lower().replace(' ', '_')}_recipe.txt"

                                st.download_button(
                                    label="📥 Download Recipe",
                                    data=recipe_download_text,
                                    file_name=filename,
                                    mime="text/plain",
                                    key=f"download_recipe_{i}",
                                    use_container_width=True
                                )
                            
                            except Exception as e:
                                st.error(f"Error parsing recipe {i+1}: {str(e)}")
                                st.markdown(f"### Recipe {i+1}")
                                st.markdown(recipe_text)
                else:
                    st.error("Failed to generate recipe variations. Please try again.")
                
                # Add CSS styling for the recipe cards
                st.markdown("""
                <style>
                    .recipe-card {
                        background-color: white;
                        border-radius: 15px;
                        padding: 30px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                        margin-bottom: 30px;
                    }
                    .recipe-title {
                        color: #FF4B4B;
                        text-align: center;
                        margin-bottom: 15px;
                    }
                    .recipe-meta {
                        display: flex;
                        justify-content: center;
                        flex-wrap: wrap;
                        gap: 15px;
                        margin-bottom: 30px;
                    }
                    .recipe-meta-item {
                        background-color: rgba(255, 75, 75, 0.1);
                        padding: 8px 15px;
                        border-radius: 20px;
                        color: #333;
                    }
                    .ingredient-item {
                        display: flex;
                        align-items: center;
                        background-color: #f8f9fa;
                        padding: 10px 15px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        transition: transform 0.2s ease;
                    }
                    .ingredient-item:hover {
                        transform: translateX(5px);
                        background-color: #f1f3f5;
                    }
                    .ingredient-icon {
                        margin-right: 10px;
                        font-size: 1.1rem;
                    }
                    .instruction-step {
                        display: flex;
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 15px;
                        transition: all 0.3s ease;
                    }
                    .instruction-step:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                    }
                    .step-number {
                        background-color: #FF4B4B;
                        color: white;
                        width: 25px;
                        height: 25px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 15px;
                        flex-shrink: 0;
                    }
                    .step-text {
                        flex: 1;
                    }
                    
                    /* Nutrition grid styling */
                    .nutrition-grid {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 15px;
                        margin-top: 20px;
                    }
                    .nutrition-item {
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 10px 15px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .nutrition-label {
                        font-weight: 500;
                        color: #333;
                    }
                    .nutrition-value {
                        font-weight: 600;
                        color: #FF4B4B;
                    }
                    
                    /* Tab styling */
                    .stTabs [data-baseweb="tab-list"] {
                        gap: 8px;
                    }
                    .stTabs [data-baseweb="tab"] {
                        height: 50px;
                        white-space: pre-wrap;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        color: #333;
                        font-weight: 500;
                    }
                    .stTabs [data-baseweb="tab-highlight"] {
                        background-color: #FF4B4B;
                    }
                    .stTabs [data-baseweb="tab"][aria-selected="true"] {
                        background-color: rgba(255, 75, 75, 0.1);
                        color: #FF4B4B;
                        font-weight: 600;
                    }
                    
                    /* Info box styling */
                    .element-container:has(.stAlert) {
                        margin-bottom: 20px;
                    }
                </style>
                """, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error generating recipes: {str(e)}")
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
    """Render nutrition analysis tab"""
    # Call the enhanced implementation
    render_nutrition_analysis_main()

def render_meal_planning():
    """Render meal planning tab"""
    # Call the enhanced implementation
    render_meal_planning_main()


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