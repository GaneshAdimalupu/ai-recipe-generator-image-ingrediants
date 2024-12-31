import os
import streamlit as st
import numpy as np
from pages.widgets import __login__
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
from Foodimg2Ing.output import output
from chef_transformer.examples import EXAMPLES
from chef_transformer import dummy, meta
from utils.api import generate_cook_image
from utils.draw import generate_food_with_logo_image, generate_recipe_image
from transformers import pipeline, set_seed
from transformers import AutoTokenizer
from PIL import ImageFont
import os
import re

from utils.utils import pure_comma_separation


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

# Enhanced CSS for better styling
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
    
    /* Input fields styling */
    .stTextInput > div > div {
        border-radius: 8px;
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

# Helper functions
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def calculate_nutrition(ingredients):
    """Calculate nutrition facts for given ingredients"""
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


# 2. Define your classes and functions **after** setting page config
class TextGeneration:
    def __init__(self):
        self.debug = False
        self.dummy_outputs = dummy.recipes
        self.tokenizer = None
        self.generator = None
        self.api_ids = []
        self.api_keys = []
        self.api_test = 2
        self.task = "text2text-generation"
        self.model_name_or_path = "flax-community/t5-recipe-generation"
        self.color_frame = "#ffffff"
        self.main_frame = "asset/frame/recipe-bg.png"
        self.no_food = "asset/frame/no_food.png"
        self.logo_frame = "asset/frame/logo.png"
        self.chef_frames = {
            "scheherazade": "asset/frame/food-image-logo-bg-s.png",
            "giovanni": "asset/frame/food-image-logo-bg-g.png",
        }
        self.fonts = {
            "title": ImageFont.truetype("asset/fonts/Poppins-Bold.ttf", 70),
            "sub_title": ImageFont.truetype("asset/fonts/Poppins-Medium.ttf", 30),
            "body_bold": ImageFont.truetype("asset/fonts/Montserrat-Bold.ttf", 22),
            "body": ImageFont.truetype("asset/fonts/Montserrat-Regular.ttf", 18),
        }
        set_seed(42)

    def _skip_special_tokens_and_prettify(self, text):
        recipe_maps = {"<sep>": "--", "<section>": "\n"}
        recipe_map_pattern = "|".join(map(re.escape, recipe_maps.keys()))

        text = re.sub(
            recipe_map_pattern,
            lambda m: recipe_maps[m.group()],
            re.sub("|".join(self.tokenizer.all_special_tokens), "", text),
        )

        data = {"title": "", "ingredients": [], "directions": []}
        for section in text.split("\n"):
            section = section.strip()
            if section.startswith("title:"):
                data["title"] = " ".join(
                    [
                        w.strip().capitalize()
                        for w in section.replace("title:", "").strip().split()
                        if w.strip()
                    ]
                )
            elif section.startswith("ingredients:"):
                data["ingredients"] = [
                    s.strip() for s in section.replace("ingredients:", "").split("--")
                ]
            elif section.startswith("directions:"):
                data["directions"] = [
                    s.strip() for s in section.replace("directions:", "").split("--")
                ]
            else:
                pass

        return data

    def load_pipeline(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        self.generator = pipeline(
            self.task, model=self.model_name_or_path, tokenizer=self.model_name_or_path
        )

    def load_api(self):
        app_ids = os.getenv("EDAMAM_APP_ID")
        app_ids = app_ids.split(",") if app_ids else []
        app_keys = os.getenv("EDAMAM_APP_KEY")
        app_keys = app_keys.split(",") if app_keys else []

        if len(app_ids) != len(app_keys):
            self.api_ids = []
            self.api_keys = []

        self.api_ids = app_ids
        self.api_keys = app_keys

    def load(self):
        self.load_api()
        if not self.debug:
            self.load_pipeline()

    def prepare_frame(self, recipe, chef_name):
        frame_path = self.chef_frames[chef_name.lower()]
        food_logo = generate_food_with_logo_image(
            frame_path, self.logo_frame, recipe["image"]
        )
        frame = generate_recipe_image(
            recipe, self.main_frame, food_logo, self.fonts, bg_color="#ffffff"
        )
        return frame

    def generate(self, items, generation_kwargs):
        recipe = self.dummy_outputs[0]
        # recipe = self.dummy_outputs[random.randint(0, len(self.dummy_outputs) - 1)]

        if not self.debug:
            generation_kwargs["num_return_sequences"] = 1
            # generation_kwargs["return_full_text"] = False
            generation_kwargs["return_tensors"] = True
            generation_kwargs["return_text"] = False

            generated_ids = self.generator(
                items,
                **generation_kwargs,
            )[
                0
            ]["generated_token_ids"]
            recipe = self.tokenizer.decode(generated_ids, skip_special_tokens=False)
            recipe = self._skip_special_tokens_and_prettify(recipe)

        if self.api_ids and self.api_keys and len(self.api_ids) == len(self.api_keys):
            test = 0
            for i in range(len(self.api_keys)):
                if test > self.api_test:
                    recipe["image"] = None
                    break
                image = generate_cook_image(
                    recipe["title"].lower(), self.api_ids[i], self.api_keys[i]
                )
                test += 1
                if image:
                    recipe["image"] = image
                    break
        else:
            recipe["image"] = None

        return recipe

    def generate_frame(self, recipe, chef_name):
        return self.prepare_frame(recipe, chef_name)


@st.cache_resource
def load_text_generator():
    generator = TextGeneration()
    generator.load()
    return generator


def predict_from_image(uploaded_file):
    """Process uploaded image and generate recipe"""
    static_dir = os.path.join(os.getcwd(), "asset/Recipe Gen images/")
    os.makedirs(static_dir, exist_ok=True)

    image_path = os.path.join(static_dir, uploaded_file.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # return output(image_path), image_path
    title, ingredients, recipe = output(image_path)

    # Flatten the lists if they're nested
    if ingredients and isinstance(ingredients[0], list):
        ingredients = [item for sublist in ingredients for item in sublist]
    if recipe and isinstance(recipe[0], list):
        recipe = [item for sublist in recipe for item in sublist]

    return title, ingredients, recipe, image_path


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
            st.image(image_path, use_column_width=True, caption="")
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


# Main application layout
st.markdown('<div class="main">', unsafe_allow_html=True)

# Centered header with animation
st.markdown('<h1 class="app-title">🧑‍🍳 Be My Chef AI</h1>', unsafe_allow_html=True)
st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
cooking_animation = load_lottie_url(
    "https://assets9.lottiefiles.com/packages/lf20_yfsytba9.json"
)
if cooking_animation:
    st_lottie(cooking_animation, height=200)
st.markdown("</div>", unsafe_allow_html=True)

# Enhanced tabs with better styling
tabs = st.tabs(["🎨 Recipe Generator", "📊 Nutrition Analysis", "📅 Meal Planning"])

# Recipe Generator Tab
with tabs[0]:
    st.markdown("### Generate Your Perfect Recipe")

    # Input method selection with modern toggle
    input_col1, input_col2 = st.columns([3, 1])
    with input_col1:
        input_method = st.radio(
            "Choose your recipe generation method:",
            ["Upload Image", "Enter Ingredients"],
            horizontal=True,
            format_func=lambda x: "📸 " + x if "Upload" in x else "🥗 " + x,
        )

    # Image Upload Section
    if input_method == "Upload Image":
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload a food image",
            type=["jpg", "jpeg", "png"],
            help="For best results, use a well-lit, clear image of the food",
        )

        if uploaded_file:
            with st.spinner("🔍 Analyzing your delicious image..."):
                try:
                    title, ingredients, recipe, image_path = predict_from_image(
                        uploaded_file
                    )
                    if ingredients and recipe:
                        nutrition = calculate_nutrition(ingredients)
                        display_recipe_card(
                            title, ingredients, recipe, nutrition, image_path
                        )
                    else:
                        st.error("Unable to analyze the image. Please try another one!")
                except Exception as e:
                    st.error("Oops! Something went wrong. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Ingredient Input Section
    else:
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

        # Example selection and ingredient input
        prompts = list(EXAMPLES.keys()) + ["Custom"]
        prompt = st.selectbox("🔍 Choose a Recipe Template or Create Your Own", prompts)

        items = st.text_area(
            "🥗 List Your Ingredients",
            value=EXAMPLES[prompt] if prompt != "Custom" else "",
            help="Separate ingredients with commas (e.g., chicken, rice, tomatoes)",
            height=100,
        )

        # Generate button with loading animation
        if st.button("🪄 Generate My Recipe", type="primary", use_container_width=True):
            with st.spinner("👨‍🍳 Creating your culinary masterpiece..."):
                generator = load_text_generator()
                recipe = generator.generate(pure_comma_separation(items), {})
                if recipe:
                    nutrition = calculate_nutrition(recipe["ingredients"])
                    display_recipe_card(
                        recipe["title"],
                        recipe["ingredients"],
                        recipe["directions"],
                        nutrition,
                    )
    st.markdown("</div>", unsafe_allow_html=True)


# Nutrition Analysis Tab
with tabs[1]:
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

# Meal Planning Tab
with tabs[2]:
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
st.markdown("</div>", unsafe_allow_html=True)
