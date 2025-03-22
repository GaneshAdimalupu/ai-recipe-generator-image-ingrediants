import streamlit as st
import time
import re
import json
import random
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Try to import database modules, but provide fallbacks if they fail
try:
    from mongodb.db import get_database
    # Add collections
    db = get_database()
    meal_plans_collection = db["meal_plans"]
    nutrition_logs_collection = db["nutrition_logs"]
    DB_AVAILABLE = True
except Exception as e:
    st.warning(f"Database connection unavailable. Using local storage as fallback.")
    DB_AVAILABLE = False

# Create data directory for local storage
DATA_DIR = Path("data")
MEAL_PLANS_DIR = DATA_DIR / "meal_plans"
NUTRITION_LOGS_DIR = DATA_DIR / "nutrition_logs"
MEAL_PLANS_DIR.mkdir(parents=True, exist_ok=True)
NUTRITION_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Helper functions for local storage as fallback
def save_local_data(directory, filename, data):
    """Save data to local JSON file"""
    file_path = directory / f"{filename}.json"
    directory.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f)
    
    return True

def load_local_data(directory, filename):
    """Load data from local JSON file"""
    file_path = directory / f"{filename}.json"
    
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return {}

def list_local_data_files(directory):
    """List all JSON files in the directory"""
    directory.mkdir(parents=True, exist_ok=True)
    return [f.stem for f in directory.glob("*.json")]

# Meal planning and nutrition functions
def save_meal_plan(username, meal_plan):
    """Save meal plan to database or local storage"""
    # Add metadata
    meal_plan["username"] = username
    meal_plan["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meal_plan["id"] = f"mp_{int(time.time())}"
    
    if DB_AVAILABLE:
        try:
            result = meal_plans_collection.insert_one(meal_plan)
            return True, meal_plan["id"]
        except Exception as e:
            st.error(f"Database error: {str(e)}")
    
    # Fallback to local storage
    filename = f"{username}_{meal_plan['id']}"
    success = save_local_data(MEAL_PLANS_DIR, filename, meal_plan)
    return success, meal_plan["id"]

def get_user_meal_plans(username):
    """Get all meal plans for a user"""
    if DB_AVAILABLE:
        try:
            plans = list(meal_plans_collection.find({"username": username}).sort("created_at", -1))
            return plans
        except Exception:
            pass
    
    # Fallback to local storage
    plans = []
    filenames = list_local_data_files(MEAL_PLANS_DIR)
    for filename in filenames:
        if filename.startswith(f"{username}_"):
            plan = load_local_data(MEAL_PLANS_DIR, filename)
            if plan:
                plans.append(plan)
    
    # Sort by created_at (newest first)
    plans.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return plans

def get_meal_plan(plan_id, username=None):
    """Get a specific meal plan"""
    if DB_AVAILABLE:
        try:
            query = {"id": plan_id}
            if username:
                query["username"] = username
            plan = meal_plans_collection.find_one(query)
            return plan
        except Exception:
            pass
    
    # Fallback to local storage
    if username:
        filename = f"{username}_{plan_id}"
        return load_local_data(MEAL_PLANS_DIR, filename)
    
    # Search all files for the plan ID without knowing the username
    filenames = list_local_data_files(MEAL_PLANS_DIR)
    for filename in filenames:
        if plan_id in filename:
            return load_local_data(MEAL_PLANS_DIR, filename)
    
    return None

def save_nutrition_log(username, nutrition_data):
    """Save nutrition log to database or local storage"""
    # Add metadata
    nutrition_data["username"] = username
    nutrition_data["logged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nutrition_data["id"] = f"nl_{int(time.time())}"
    
    if DB_AVAILABLE:
        try:
            result = nutrition_logs_collection.insert_one(nutrition_data)
            return True, nutrition_data["id"]
        except Exception as e:
            st.error(f"Database error: {str(e)}")
    
    # Fallback to local storage
    filename = f"{username}_{nutrition_data['id']}"
    success = save_local_data(NUTRITION_LOGS_DIR, filename, nutrition_data)
    return success, nutrition_data["id"]

def get_user_nutrition_logs(username, days=30):
    """Get nutrition logs for a user within the specified number of days"""
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    if DB_AVAILABLE:
        try:
            logs = list(nutrition_logs_collection.find({
                "username": username,
                "logged_at": {"$gte": cutoff_date}
            }).sort("logged_at", -1))
            return logs
        except Exception:
            pass
    
    # Fallback to local storage
    logs = []
    filenames = list_local_data_files(NUTRITION_LOGS_DIR)
    
    for filename in filenames:
        if filename.startswith(f"{username}_"):
            log = load_local_data(NUTRITION_LOGS_DIR, filename)
            if log and log.get("logged_at", "").split()[0] >= cutoff_date:
                logs.append(log)
    
    # Sort by logged_at (newest first)
    logs.sort(key=lambda x: x.get("logged_at", ""), reverse=True)
    return logs

# Gemini API Integration
def get_gemini_api_key():
    """Get Gemini API key from Streamlit secrets or environment"""
    try:
        return st.secrets["mongo"]["API_KEY"]
    except:
        return None

def generate_with_gemini(prompt, model="gemini-1.5-pro"):
    """Generate content using Gemini API"""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = get_gemini_api_key()
        if not api_key:
            raise ValueError("No API key found for Gemini")
        
        # Initialize the Gemini model
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Generate content
        response = llm.invoke(prompt)
        return response.content, None
        
    except Exception as e:
        return None, f"Error with Gemini API: {str(e)}"

def analyze_ingredients_nutrition(ingredients, dietary_preferences=None):
    """Analyze ingredients and return comprehensive nutrition data using Gemini API"""
    try:
        # Build prompt
        ingredient_list = ", ".join(ingredients) if isinstance(ingredients, list) else ingredients
        prompt = f"""
        Analyze the following ingredients: {ingredient_list}

        Please provide a detailed nutritional analysis with the following information:
        1. Total calories
        2. Macronutrients breakdown (protein, carbohydrates, fats)
        3. Micronutrients (vitamins and minerals)
        4. Any allergens or common dietary concerns
        
        Format the response as structured JSON with the following fields:
        - calories (number)
        - protein_g (number)
        - carbs_g (number)
        - fat_g (number)
        - fiber_g (number)
        - sugar_g (number)
        - allergens (array of strings)
        - vitamins (array of objects with name and amount)
        - minerals (array of objects with name and amount)
        - health_notes (string with any relevant health information)
        """
        
        if dietary_preferences:
            pref_list = ", ".join(dietary_preferences)
            prompt += f"\n\nAlso note these dietary preferences or restrictions: {pref_list}"
        
        response, error = generate_with_gemini(prompt)
        
        if error:
            return None, error
        
        # Extract JSON from response
        try:
            # First try to find a JSON block in the markdown
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for anything that looks like a JSON object
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # Use the whole response as a fallback
                    json_str = response
            
            # Clean up common formatting issues
            json_str = re.sub(r'(\w+):', r'"\1":', json_str)  # Convert keys to quoted strings
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            
            nutrition_data = json.loads(json_str)
            return nutrition_data, None
            
        except Exception as json_error:
            # Fallback to generating structured data with another prompt
            fallback_prompt = f"""
            The previous response couldn't be parsed as JSON. Please analyze these ingredients again:
            {ingredient_list}
            
            Return ONLY a valid JSON object with these exact fields and numeric values:
            {{
              "calories": 0,
              "protein_g": 0,
              "carbs_g": 0,
              "fat_g": 0,
              "fiber_g": 0,
              "sugar_g": 0,
              "allergens": [],
              "vitamins": [],
              "minerals": [],
              "health_notes": ""
            }}
            """
            
            fallback_response, fallback_error = generate_with_gemini(fallback_prompt)
            
            if fallback_error:
                # Generate mock data as a last resort
                return generate_mock_nutrition_data(ingredients), f"Error parsing response, using estimated values. Original error: {str(json_error)}"
            
            try:
                # Extract JSON from fallback response
                json_match = re.search(r"\{.*\}", fallback_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0)), None
                else:
                    return generate_mock_nutrition_data(ingredients), "Unable to parse response, using estimated values"
            except:
                return generate_mock_nutrition_data(ingredients), "Unable to parse response, using estimated values"
                
    except Exception as e:
        # Generate mock data if the API call fails
        return generate_mock_nutrition_data(ingredients), f"Error: {str(e)}"

def generate_mock_nutrition_data(ingredients):
    """Generate mock nutrition data when API fails"""
    ingredient_count = len(ingredients) if isinstance(ingredients, list) else len(ingredients.split(','))
    
    return {
        "calories": int(100 + 50 * ingredient_count * random.uniform(0.8, 1.2)),
        "protein_g": int(5 + 3 * ingredient_count * random.uniform(0.8, 1.2)),
        "carbs_g": int(10 + 5 * ingredient_count * random.uniform(0.8, 1.2)),
        "fat_g": int(5 + 2 * ingredient_count * random.uniform(0.8, 1.2)),
        "fiber_g": round(2 + 1.5 * ingredient_count * random.uniform(0.8, 1.2), 1),
        "sugar_g": round(2 + 1.5 * ingredient_count * random.uniform(0.8, 1.2), 1),
        "allergens": ["Note: Allergen detection requires API analysis"],
        "vitamins": [
            {"name": "Vitamin A", "amount": "estimated"},
            {"name": "Vitamin C", "amount": "estimated"},
        ],
        "minerals": [
            {"name": "Calcium", "amount": "estimated"},
            {"name": "Iron", "amount": "estimated"},
        ],
        "health_notes": "These are estimated values as the detailed analysis couldn't be completed."
    }

def generate_meal_plan(preferences, days=7, dietary_restrictions=None):
    """Generate a complete meal plan using Gemini API"""
    try:
        # Build prompt
        goals = ", ".join(preferences.get("goals", ["balanced"]))
        
        prompt = f"""
        Create a detailed meal plan for {days} days with the following parameters:
        - Health/fitness goals: {goals}
        - Calories target: {preferences.get('calories', '2000')} calories per day
        """
        
        if dietary_restrictions:
            restrictions = ", ".join(dietary_restrictions)
            prompt += f"- Dietary restrictions: {restrictions}\n"
        
        if preferences.get("cuisine_preferences"):
            cuisines = ", ".join(preferences.get("cuisine_preferences"))
            prompt += f"- Preferred cuisines: {cuisines}\n"
            
        if preferences.get("meal_preferences"):
            meal_prefs = ", ".join(preferences.get("meal_preferences"))
            prompt += f"- Meal preferences: {meal_prefs}\n"
        
        prompt += """
        For each day, include:
        - Breakfast
        - Lunch
        - Dinner
        - Snacks
        - Total calorie count
        - Macronutrient breakdown (protein, carbs, fat)
        
        Format the response as JSON with the following structure:
        {
          "plan_name": "Name for this meal plan",
          "days": [
            {
              "day": 1,
              "meals": [
                {
                  "type": "breakfast",
                  "name": "Meal name",
                  "ingredients": ["ingredient1", "ingredient2"],
                  "preparation": "Brief preparation instructions",
                  "calories": 000,
                  "protein": 00,
                  "carbs": 00,
                  "fat": 00
                },
                // repeat for lunch, dinner, snacks
              ],
              "daily_totals": {
                "calories": 0000,
                "protein": 000,
                "carbs": 000,
                "fat": 000
              }
            },
            // repeat for each day
          ]
        }
        """
        
        response, error = generate_with_gemini(prompt)
        
        if error:
            return None, error
        
        # Extract JSON from response
        try:
            # First look for a code block
            json_match = re.search(r"```(?:json)?\n(.*?)\n```", response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for anything that might be a JSON object
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return None, "Could not extract meal plan from response"
            
            # Parse the JSON
            meal_plan = json.loads(json_str)
            
            # Add metadata
            meal_plan["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            meal_plan["preferences"] = preferences
            meal_plan["days_count"] = days
            
            return meal_plan, None
            
        except Exception as json_error:
            return None, f"Error parsing meal plan: {str(json_error)}"
            
    except Exception as e:
        return None, f"Error generating meal plan: {str(e)}"

# UI Components for Nutrition Analysis
def render_nutrition_analysis():
    st.markdown("## 📊 Comprehensive Nutrition Analysis")
    
    # Get current username
    username = get_current_username() if "get_current_username" in globals() else st.session_state.get("username", "guest")
    
    analysis_tab, history_tab = st.tabs(["Analyze Ingredients", "Nutrition History"])
    
    with analysis_tab:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            input_method = st.radio(
                "Input method:",
                ["Text Input"],
                horizontal=True
            )
            
            if input_method == "Text Input":
                ingredients = st.text_area(
                    "Enter ingredients (one per line or comma-separated):",
                    height=150,
                    help="Enter ingredients with approximate quantities if possible"
                )
            
        with col2:
            st.markdown("### Dietary Filters")
            dietary_preferences = st.multiselect(
                "Dietary considerations:",
                [
                    "Vegetarian", "Vegan", "Gluten-Free", 
                    "Dairy-Free", "Keto", "Paleo", 
                    "Low-Carb", "Low-Fat", "Low-Sodium"
                ]
            )
            
            meal_type = st.selectbox(
                "Meal type:",
                ["Any", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"]
            )
        
        analyze_btn = st.button("📊 Analyze Nutrition", type="primary", use_container_width=True)
        
        if analyze_btn:
            if not ingredients:
                st.error("Please enter ingredients or upload a recipe file.")
                return
            
            # Process ingredients
            if isinstance(ingredients, str):
                if '\n' in ingredients:
                    ingredients_list = [i.strip() for i in ingredients.split('\n') if i.strip()]
                else:
                    ingredients_list = [i.strip() for i in ingredients.split(',') if i.strip()]
            else:
                ingredients_list = ingredients
            
            with st.spinner("Analyzing nutritional content..."):
                # Call Gemini API to analyze ingredients
                nutrition_data, error = analyze_ingredients_nutrition(ingredients_list, dietary_preferences)
                
                if error:
                    st.warning(f"Using estimated nutrition values. {error}")
                
                if nutrition_data:
                    st.success("Analysis complete!")
                    
                    # Store the analysis result
                    meal_info = {"type": meal_type} if meal_type != "Any" else {}
                    save_data = {
                        "ingredients": ingredients_list,
                        "nutrition": nutrition_data,
                        "dietary_preferences": dietary_preferences,
                        "meal_info": meal_info
                    }
                    
                    save_success, log_id = save_nutrition_log(username, save_data)
                    if save_success:
                        st.success("Nutrition log saved successfully!")
                    
                    # Display nutrition information
                    cols = st.columns([2, 1])
                    
                    with cols[0]:
                        # Summary card
                        st.markdown("### Nutrition Summary")
                        summary_cols = st.columns(3)
                        
                        with summary_cols[0]:
                            st.metric("Calories", f"{nutrition_data.get('calories', 0)} kcal")
                        with summary_cols[1]:
                            st.metric("Protein", f"{nutrition_data.get('protein_g', 0)}g")
                        with summary_cols[2]:
                            st.metric("Carbs", f"{nutrition_data.get('carbs_g', 0)}g")
                        
                        # More detailed breakdown
                        st.markdown("### Detailed Breakdown")
                        
                        # Create macronutrient chart
                        macro_data = {
                            "Nutrient": ["Protein", "Carbs", "Fat"],
                            "Grams": [
                                nutrition_data.get("protein_g", 0),
                                nutrition_data.get("carbs_g", 0),
                                nutrition_data.get("fat_g", 0)
                            ]
                        }
                        
                        fig = px.bar(
                            macro_data, 
                            x="Nutrient", 
                            y="Grams",
                            color="Nutrient",
                            color_discrete_map={
                                "Protein": "#FF4B4B", 
                                "Carbs": "#1E88E5", 
                                "Fat": "#FFC107"
                            },
                            title="Macronutrient Composition"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calorie breakdown pie chart
                        protein_cals = nutrition_data.get("protein_g", 0) * 4
                        carbs_cals = nutrition_data.get("carbs_g", 0) * 4
                        fat_cals = nutrition_data.get("fat_g", 0) * 9
                        
                        fig2 = px.pie(
                            values=[protein_cals, carbs_cals, fat_cals],
                            names=["Protein", "Carbs", "Fat"],
                            title="Calorie Sources",
                            color_discrete_map={
                                "Protein": "#FF4B4B", 
                                "Carbs": "#1E88E5", 
                                "Fat": "#FFC107"
                            },
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                        
                    with cols[1]:
                        # Health notes and allergens
                        st.markdown("### Health Notes")
                        st.info(nutrition_data.get("health_notes", "No specific health notes."))
                        
                        # Allergens
                        st.markdown("### Allergens")
                        allergens = nutrition_data.get("allergens", [])
                        if allergens:
                            for allergen in allergens:
                                st.warning(f"⚠️ {allergen}")
                        else:
                            st.success("✅ No common allergens detected")
                        
                        # Additional nutrition metrics
                        st.markdown("### Additional Metrics")
                        st.metric("Fiber", f"{nutrition_data.get('fiber_g', 0)}g")
                        st.metric("Sugar", f"{nutrition_data.get('sugar_g', 0)}g")
                        
                        # Vitamins and minerals
                        if nutrition_data.get("vitamins") or nutrition_data.get("minerals"):
                            st.markdown("### Micronutrients")
                            
                            if nutrition_data.get("vitamins"):
                                st.markdown("#### Vitamins")
                                for vitamin in nutrition_data.get("vitamins", []):
                                    if isinstance(vitamin, dict):
                                        st.text(f"• {vitamin.get('name', 'Unknown')}: {vitamin.get('amount', 'N/A')}")
                                    else:
                                        st.text(f"• {vitamin}")
                            
                            if nutrition_data.get("minerals"):
                                st.markdown("#### Minerals")
                                for mineral in nutrition_data.get("minerals", []):
                                    if isinstance(mineral, dict):
                                        st.text(f"• {mineral.get('name', 'Unknown')}: {mineral.get('amount', 'N/A')}")
                                    else:
                                        st.text(f"• {mineral}")
                    
                    # Recipe suggestion (if applicable)
                    if len(ingredients_list) > 2:
                        st.markdown("### 👨‍🍳 Recipe Suggestion")
                        suggest_recipe_btn = st.button("Get Recipe Ideas with These Ingredients")
                        
                        if suggest_recipe_btn:
                            with st.spinner("Generating recipe ideas..."):
                                # Redirect to recipe generation
                                st.session_state.recipe_suggestion_ingredients = ingredients_list
                                st.session_state.redirect_to_recipes = True
                                st.rerun()
    
    with history_tab:
        st.markdown("### Your Nutrition History")
        history_days = st.slider("Show history for the last X days:", 7, 90, 30)
        
        nutrition_logs = get_user_nutrition_logs(username, days=history_days)
        
        if not nutrition_logs:
            st.info("No nutrition logs found. Start analyzing ingredients to build your history!")
        else:
            # Create a summary of nutrition over time
            dates = []
            calories = []
            proteins = []
            carbs = []
            fats = []
            
            for log in nutrition_logs:
                try:
                    log_date = datetime.strptime(log.get("logged_at", ""), "%Y-%m-%d %H:%M:%S").strftime("%m/%d")
                    nutrition = log.get("nutrition", {})
                    
                    dates.append(log_date)
                    calories.append(nutrition.get("calories", 0))
                    proteins.append(nutrition.get("protein_g", 0))
                    carbs.append(nutrition.get("carbs_g", 0))
                    fats.append(nutrition.get("fat_g", 0))
                except:
                    continue
            
            if dates:
                # Trend chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=dates, y=calories,
                    mode='lines+markers',
                    name='Calories',
                    line=dict(color='#FF4B4B', width=2)
                ))
                
                fig.update_layout(
                    title="Calorie Trends",
                    xaxis_title="Date",
                    yaxis_title="Calories",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Macronutrient trends
                fig2 = go.Figure()
                
                fig2.add_trace(go.Scatter(
                    x=dates, y=proteins,
                    mode='lines+markers',
                    name='Protein',
                    line=dict(color='#FF4B4B', width=2)
                ))
                
                fig2.add_trace(go.Scatter(
                    x=dates, y=carbs,
                    mode='lines+markers',
                    name='Carbs',
                    line=dict(color='#1E88E5', width=2)
                ))
                
                fig2.add_trace(go.Scatter(
                    x=dates, y=fats,
                    mode='lines+markers',
                    name='Fat',
                    line=dict(color='#FFC107', width=2)
                ))
                
                fig2.update_layout(
                    title="Macronutrient Trends",
                    xaxis_title="Date",
                    yaxis_title="Grams",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Recent logs
            st.markdown("### Recent Nutrition Logs")
            for i, log in enumerate(nutrition_logs[:5]):
                with st.expander(f"Log from {log.get('logged_at', 'Unknown date')}"):
                    # Display the log details
                    st.markdown("#### Ingredients Analyzed:")
                    ingredients = log.get("ingredients", [])
                    if isinstance(ingredients, list):
                        for ing in ingredients:
                            st.text(f"• {ing}")
                    else:
                        st.text(ingredients)
                    
                    st.markdown("#### Nutrition Summary:")
                    nutrition = log.get("nutrition", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Calories", f"{nutrition.get('calories', 0)} kcal")
                    with col2:
                        st.metric("Protein", f"{nutrition.get('protein_g', 0)}g")
                    with col3:
                        st.metric("Carbs", f"{nutrition.get('carbs_g', 0)}g")

# UI Components for Meal Planning
def render_meal_planning():
    st.markdown("## 📅 Intelligent Meal Planning")
    
    # Get current username
    username = get_current_username() if "get_current_username" in globals() else st.session_state.get("username", "guest")
    
    plan_tab, saved_tab = st.tabs(["Create Plan", "Saved Plans"])
    
    with plan_tab:
        st.markdown("### Create Your Personalized Meal Plan")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Meal Plan Preferences")
            
            plan_name = st.text_input("Plan name (optional):", 
                                     placeholder="e.g., Summer Fitness Plan, Family Meal Plan")
            
            days = st.slider("Number of days:", 1, 14, 7)
            
            goals = st.multiselect(
                "Health/fitness goals:",
                [
                    "Weight Loss", "Muscle Gain", "Maintenance", 
                    "Heart Health", "Energy Boost", "Balanced Diet"
                ],
                default=["Balanced Diet"]
            )
            
            calories = st.slider("Target daily calories:", 1200, 3500, 2000, 100)
        
        with col2:
            st.markdown("#### Dietary Preferences")
            
            dietary_restrictions = st.multiselect(
                "Dietary restrictions:",
                [
                    "Vegetarian", "Vegan", "Gluten-Free", 
                    "Dairy-Free", "Keto", "Paleo", 
                    "Low-Carb", "Low-Fat", "Low-Sodium"
                ]
            )
            
            cuisine_preferences = st.multiselect(
                "Preferred cuisines:",
                [
                    "Italian", "Mexican", "Indian", "Chinese", 
                    "Japanese", "Mediterranean", "Thai", "American",
                    "Middle Eastern", "French", "Korean"
                ]
            )
            
            meal_preferences = st.multiselect(
                "Meal preferences:",
                [
                    "Quick & Easy", "Batch-Cooking", "Kid-Friendly",
                    "High Protein", "Budget-Friendly", "One-Pot Meals"
                ]
            )
        
        generate_plan_btn = st.button("🍽️ Generate Meal Plan", type="primary", use_container_width=True)
        
        if generate_plan_btn:
            with st.spinner("Creating your personalized meal plan..."):
                # Prepare preferences object
                preferences = {
                    "name": plan_name or f"{username}'s Meal Plan",
                    "goals": goals,
                    "calories": calories,
                    "cuisine_preferences": cuisine_preferences,
                    "meal_preferences": meal_preferences
                }
                
                # Generate meal plan with Gemini
                meal_plan, error = generate_meal_plan(preferences, days, dietary_restrictions)
                
                if error:
                    st.error(f"Error generating meal plan: {error}")
                elif meal_plan:
                    # Save the meal plan
                    save_success, plan_id = save_meal_plan(username, meal_plan)
                    
                    if save_success:
                        st.success(f"Meal plan '{meal_plan.get('plan_name', 'New Plan')}' created successfully!")
                    
                    # Display the meal plan
                    st.markdown(f"## {meal_plan.get('plan_name', 'Your Personalized Meal Plan')}")
                    
                    # Create a weekly calendar view
                    if days > 1:
                        # Initialize tabs for each day
                        day_tabs = st.tabs([f"Day {day['day']}" for day in meal_plan.get('days', [])])
                        
                        # Populate each day tab
                        for i, day_data in enumerate(meal_plan.get('days', [])):
                            with day_tabs[i]:
                                # Day overview at the top
                                st.markdown(f"### Day {day_data['day']} Overview")
                                
                                # Nutritional summary for the day
                                totals = day_data.get('daily_totals', {})
                                
                                summary_cols = st.columns(4)
                                with summary_cols[0]:
                                    st.metric("Total Calories", f"{totals.get('calories', 0)} kcal")
                                with summary_cols[1]:
                                    st.metric("Protein", f"{totals.get('protein', 0)}g")
                                with summary_cols[2]:
                                    st.metric("Carbs", f"{totals.get('carbs', 0)}g")
                                with summary_cols[3]:
                                    st.metric("Fat", f"{totals.get('fat', 0)}g")
                                
                                # Meal cards for each meal of the day
                                meals = day_data.get('meals', [])
                                
                                for meal in meals:
                                    with st.expander(f"{meal.get('type', 'Meal').title()}: {meal.get('name', 'Unnamed Meal')}"):
                                        # Meal details
                                        st.markdown(f"**{meal.get('name', 'Meal')}**")
                                        
                                        # Ingredients and preparation
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.markdown("#### Ingredients")
                                            ingredients = meal.get('ingredients', [])
                                            if isinstance(ingredients, list):
                                                for ing in ingredients:
                                                    st.markdown(f"- {ing}")
                                            else:
                                                st.markdown(ingredients)
                                        
                                        with col2:
                                            st.markdown("#### Preparation")
                                            st.markdown(meal.get('preparation', 'No preparation instructions available.'))
                                        
                                        # Nutrition info
                                        st.markdown("#### Nutrition")
                                        
                                        nutrition_cols = st.columns(4)
                                        with nutrition_cols[0]:
                                            st.metric("Calories", f"{meal.get('calories', 0)} kcal")
                                        with nutrition_cols[1]:
                                            st.metric("Protein", f"{meal.get('protein', 0)}g")
                                        with nutrition_cols[2]:
                                            st.metric("Carbs", f"{meal.get('carbs', 0)}g")
                                        with nutrition_cols[3]:
                                            st.metric("Fat", f"{meal.get('fat', 0)}g")
                    else:
                        # Single day view (more detailed)
                        day_data = meal_plan.get('days', [{}])[0]
                        
                        # Day overview at the top
                        st.markdown("### Daily Overview")
                        
                        # Nutritional summary for the day
                        totals = day_data.get('daily_totals', {})
                        
                        summary_cols = st.columns(4)
                        with summary_cols[0]:
                            st.metric("Total Calories", f"{totals.get('calories', 0)} kcal")
                        with summary_cols[1]:
                            st.metric("Protein", f"{totals.get('protein', 0)}g")
                        with summary_cols[2]:
                            st.metric("Carbs", f"{totals.get('carbs', 0)}g")
                        with summary_cols[3]:
                            st.metric("Fat", f"{totals.get('fat', 0)}g")
                        
                        # Visual breakdown
                        macro_data = {
                            "Nutrient": ["Protein", "Carbs", "Fat"],
                            "Grams": [
                                totals.get("protein", 0),
                                totals.get("carbs", 0),
                                totals.get("fat", 0)
                            ]
                        }
                        
                        fig = px.bar(
                            macro_data, 
                            x="Nutrient", 
                            y="Grams",
                            color="Nutrient",
                            color_discrete_map={
                                "Protein": "#FF4B4B", 
                                "Carbs": "#1E88E5", 
                                "Fat": "#FFC107"
                            },
                            title="Macronutrient Composition"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Meal cards for each meal of the day
                        st.markdown("### Meals")
                        
                        for meal in day_data.get('meals', []):
                            with st.expander(f"{meal.get('type', 'Meal').title()}: {meal.get('name', 'Unnamed Meal')}"):
                                # Meal details
                                st.markdown(f"**{meal.get('name', 'Meal')}**")
                                
                                # Ingredients and preparation
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("#### Ingredients")
                                    ingredients = meal.get('ingredients', [])
                                    if isinstance(ingredients, list):
                                        for ing in ingredients:
                                            st.markdown(f"- {ing}")
                                    else:
                                        st.markdown(ingredients)
                                
                                with col2:
                                    st.markdown("#### Preparation")
                                    st.markdown(meal.get('preparation', 'No preparation instructions available.'))
                                
                                # Nutrition info
                                st.markdown("#### Nutrition")
                                
                                nutrition_cols = st.columns(4)
                                with nutrition_cols[0]:
                                    st.metric("Calories", f"{meal.get('calories', 0)} kcal")
                                with nutrition_cols[1]:
                                    st.metric("Protein", f"{meal.get('protein', 0)}g")
                                with nutrition_cols[2]:
                                    st.metric("Carbs", f"{meal.get('carbs', 0)}g")
                                with nutrition_cols[3]:
                                    st.metric("Fat", f"{meal.get('fat', 0)}g")
                    
                    # Shopping list generation
                    st.markdown("### 🛒 Shopping List")
                    
                    # Extract all ingredients from all meals
                    all_ingredients = []
                    for day in meal_plan.get('days', []):
                        for meal in day.get('meals', []):
                            ingredients = meal.get('ingredients', [])
                            if isinstance(ingredients, list):
                                all_ingredients.extend(ingredients)
                            else:
                                all_ingredients.append(ingredients)
                    
                    # Remove duplicates and sort
                    unique_ingredients = sorted(set(all_ingredients))
                    
                    # Organize by categories (simplified version)
                    categories = {
                        "Produce": [],
                        "Meat & Seafood": [],
                        "Dairy & Eggs": [],
                        "Grains & Pasta": [],
                        "Canned & Packaged": [],
                        "Spices & Seasonings": [],
                        "Other": []
                    }
                    
                    # Simple categorization based on keywords
                    for ingredient in unique_ingredients:
                        ingredient_lower = ingredient.lower()
                        if any(word in ingredient_lower for word in ["vegetable", "fruit", "lettuce", "spinach", "onion", "tomato", "carrot", "pepper", "potato"]):
                            categories["Produce"].append(ingredient)
                        elif any(word in ingredient_lower for word in ["chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp", "meat"]):
                            categories["Meat & Seafood"].append(ingredient)
                        elif any(word in ingredient_lower for word in ["milk", "cheese", "yogurt", "cream", "butter", "egg"]):
                            categories["Dairy & Eggs"].append(ingredient)
                        elif any(word in ingredient_lower for word in ["rice", "pasta", "bread", "flour", "oat", "quinoa", "cereal"]):
                            categories["Grains & Pasta"].append(ingredient)
                        elif any(word in ingredient_lower for word in ["can", "jar", "sauce", "soup", "bean", "lentil", "packaged"]):
                            categories["Canned & Packaged"].append(ingredient)
                        elif any(word in ingredient_lower for word in ["spice", "herb", "salt", "pepper", "oregano", "basil", "cumin"]):
                            categories["Spices & Seasonings"].append(ingredient)
                        else:
                            categories["Other"].append(ingredient)
                    
                    # Display organized shopping list
                    shopping_cols = st.columns(3)
                    col_index = 0
                    
                    for category, items in categories.items():
                        if items:
                            with shopping_cols[col_index % 3]:
                                st.markdown(f"#### {category}")
                                for item in items:
                                    st.checkbox(item, key=f"item_{item}")
                            col_index += 1
                    
                    # Shopping list export options
                    if st.button("📥 Export Shopping List"):
                        # Create a text version of the shopping list
                        shopping_list_text = "SHOPPING LIST\n\n"
                        for category, items in categories.items():
                            if items:
                                shopping_list_text += f"{category}:\n"
                                for item in items:
                                    shopping_list_text += f"[ ] {item}\n"
                                shopping_list_text += "\n"
                        
                        # Create download button
                        st.download_button(
                            label="Download Shopping List",
                            data=shopping_list_text,
                            file_name="shopping_list.txt",
                            mime="text/plain"
                        )
    
    with saved_tab:
        st.markdown("### Your Saved Meal Plans")
        
        # Get user's saved meal plans
        meal_plans = get_user_meal_plans(username)
        
        if not meal_plans:
            st.info("You don't have any saved meal plans yet. Create your first plan!")
        else:
            for i, plan in enumerate(meal_plans):
                with st.expander(f"{plan.get('plan_name', 'Meal Plan')} - Created on {plan.get('created_at', 'Unknown date')}"):
                    # Plan details
                    st.markdown(f"### {plan.get('plan_name', 'Meal Plan')}")
                    
                    # Plan metadata
                    preferences = plan.get('preferences', {})
                    
                    meta_cols = st.columns(3)
                    with meta_cols[0]:
                        st.markdown(f"**Days:** {plan.get('days_count', len(plan.get('days', [])))}")
                    with meta_cols[1]:
                        st.markdown(f"**Target Calories:** {preferences.get('calories', 'Not specified')} kcal")
                    with meta_cols[2]:
                        st.markdown(f"**Goals:** {', '.join(preferences.get('goals', ['Not specified']))}")
                    
                    # View full plan button
                    if st.button(f"View Full Plan", key=f"view_plan_{i}"):
                        # Store plan ID in session state and redirect to detailed view
                        st.session_state.selected_meal_plan_id = plan.get('id')
                        st.rerun()
                    
                    # Clone plan button (to create a similar plan with adjustments)
                    if st.button(f"Clone & Modify Plan", key=f"clone_plan_{i}"):
                        # Pre-fill the plan creation form with this plan's parameters
                        st.session_state.clone_plan_preferences = preferences
                        st.session_state.selected_tab = "Create Plan"
                        st.rerun()

# Helper function to get current username
def get_current_username():
    """Get current username from session state"""
    # Try from session state directly
    if "username" in st.session_state:
        return st.session_state.username
    
    # Try to get from login UI
    try:
        from pages.widgets import __login__
        login_ui = __login__(
            auth_token="your_courier_auth_token",
            company_name="Be My Chef AI",
            width=200,
            height=200,
        )
        return login_ui.get_username()
    except:
        # Fallback to default user
        return "guest"

# Main integration function to replace in home.py
def render_nutrition_analysis_main():
    """Wrapper function for nutrition analysis to integrate with home.py"""
    render_nutrition_analysis()

def render_meal_planning_main():
    """Wrapper function for meal planning to integrate with home.py"""
    render_meal_planning()

# If this script is run directly, show a standalone interface
if __name__ == "__main__":
    st.set_page_config(
        page_title="Nutrition & Meal Planning",
        page_icon="🍽️",
        layout="wide"
    )
    
    tabs = st.tabs(["📊 Nutrition Analysis", "📅 Meal Planning"])
    
    with tabs[0]:
        render_nutrition_analysis()
    
    with tabs[1]:
        render_meal_planning()