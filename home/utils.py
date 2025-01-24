import base64
import numpy as np
import requests
import plotly.express as px
import streamlit as st
from pathlib import Path
import os


def img_to_base64(img_path):
    """Convert image file to base64 string"""
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def load_lottie_url(url: str):
    """Load and return Lottie animation from URL"""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def calculate_nutrition(ingredients):
    """Calculate mock nutrition facts for given ingredients"""
    return {
        "calories": np.random.randint(200, 800),
        "protein": np.random.randint(10, 30),
        "carbs": np.random.randint(20, 60),
        "fat": np.random.randint(10, 40),
        "fiber": np.random.randint(2, 8),
    }


def check_dietary_restrictions(ingredients, restrictions):
    """Check ingredients against dietary restrictions"""
    restricted_ingredients = []
    for ingredient in ingredients:
        for restriction in restrictions:
            if restriction.lower() in ingredient.lower():
                restricted_ingredients.append(f"{ingredient} (contains {restriction})")
    return restricted_ingredients


def predict_from_image(uploaded_file):
    """Process uploaded image and generate recipe"""
    try:
        static_dir = os.path.join(os.getcwd(), "asset/Recipe Gen images/")
        os.makedirs(static_dir, exist_ok=True)

        image_path = os.path.join(static_dir, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            from Foodimg2Ing.output import output

            title, ingredients, recipe = output(image_path)

            # Handle title
            if isinstance(title, list):
                title = " ".join(title) if title else "Custom Recipe"
            elif not title:
                title = "Custom Recipe"

            # Clean and validate recipe steps
            if recipe:
                # Remove any error messages or invalid steps
                recipe = [
                    step
                    for step in recipe
                    if not any(
                        error_text in step.lower()
                        for error_text in ["reason:", "no", "eos", "found"]
                    )
                ]
                # Remove empty or single-character steps
                recipe = [step for step in recipe if len(step.strip()) > 1]

            # Ensure ingredients and recipe are lists
            ingredients = (
                ingredients if ingredients and isinstance(ingredients, list) else []
            )
            recipe = recipe if recipe else []

            return title, ingredients, recipe, image_path

        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None, None, None, None

    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None, None, None, None


def display_recipe_card(title, ingredients, instructions, nutrition, image_path=None):
    """Display recipe information in an enhanced, aesthetic card format"""
    # Main recipe card container
    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)

    # Title section with elegant styling
    st.markdown(f'<h1 class="recipe-title">🍳 {title}</h1>', unsafe_allow_html=True)

    # Image and content layout
    cols = st.columns([1, 1])

    with cols[0]:
        if image_path:
            st.image(image_path, use_container_width=True, caption="")
            st.markdown("<br>", unsafe_allow_html=True)

        # Nutrition section with modern design
        st.markdown('<div class="nutrition-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Nutrition Facts")

        # Create three columns for nutrition metrics
        metric_cols = st.columns(3)
        for idx, (nutrient, value) in enumerate(nutrition.items()):
            with metric_cols[idx % 3]:
                st.metric(nutrient.capitalize(), f"{value}g")

        # Interactive nutrition chart
        fig = px.pie(
            values=list(nutrition.values()),
            names=list(nutrition.keys()),
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        # Ingredients section with enhanced styling
        st.markdown('<div class="recipe-section">', unsafe_allow_html=True)
        st.markdown("#### 🥗 Ingredients")
        for ingredient in ingredients:
            st.markdown(
                f'<div class="ingredient-item">• {ingredient}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Instructions section with step-by-step styling
        st.markdown('<div class="recipe-section">', unsafe_allow_html=True)
        st.markdown("#### 👩‍🍳 Instructions")
        for i, step in enumerate(instructions, 1):
            st.markdown(
                f'<div class="instruction-step">Step {i}: {step}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
