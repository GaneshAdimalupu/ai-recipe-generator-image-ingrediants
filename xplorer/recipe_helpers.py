import pandas as pd
from datetime import datetime
from mongodb.db import get_database
import streamlit as st

# Initialize MongoDB connection
db = get_database()
saved_recipes = db["saved_recipes"]

def load_recipe_data():
    """Load and clean recipe data"""
    try:
        recipes_df = pd.read_csv('data/indian_recipes.csv')
        
        # Clean data fields
        default_values = {
            'cuisine': 'Not Specified',
            'course': 'Not Specified',
            'diet': 'Not Specified',
            'prep_time': 'Not Specified',
            'description': 'No description available',
            'ingredients': 'Not specified',
            'instructions': 'Not specified'
        }
        
        for col, default in default_values.items():
            recipes_df[col] = recipes_df[col].fillna(default)
        
        return recipes_df
    except Exception as e:
        print(f"Error loading recipe data: {str(e)}")
        return None

def parse_ingredients(ingredients_str):
    """Parse ingredients into structured format"""
    if pd.isna(ingredients_str):
        return []
    
    ingredients = [ing.strip() for ing in ingredients_str.split('\n') if ing.strip()]
    parsed = []
    
    for ing in ingredients:
        ing = ing.replace('\t', '').strip()
        
        if ',' in ing:
            quantity, name = ing.split(',', 1)
            quantity = quantity.strip()
            name = name.strip()
        else:
            quantity = ""
            name = ing.strip()
        
        if quantity or name:
            parsed.append({
                'quantity': quantity,
                'name': name
            })
    
    return parsed

def parse_instructions(instructions_str):
    """Parse instructions into clear steps"""
    if pd.isna(instructions_str):
        return []
    return [step.strip() for step in instructions_str.split('.') if step.strip()]

def is_recipe_saved(recipe_name, user):
    """Check if recipe is saved by user"""
    if not user:
        return False
    return bool(saved_recipes.find_one({
        "user": user,
        "recipe_name": recipe_name
    }))

def toggle_recipe_save(recipe_name, recipe_data, user):
    """Toggle recipe save state"""
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

def filter_recipes(recipes_df, selected_view, current_user):
    """Handle recipe filtering based on view and user"""
    if selected_view == "All Recipes":
        return recipes_df
    else:  # Saved Recipes
        if not current_user:
            return pd.DataFrame()
            
        saved_recipes_list = list(saved_recipes.find({"user": current_user}))
        if not saved_recipes_list:
            return pd.DataFrame()
            
        return pd.DataFrame([recipe['recipe_data'] for recipe in saved_recipes_list])

def search_recipes(df, search_query):
    """Search recipes by name, ingredients, or cuisine"""
    if search_query:
        search_terms = search_query.lower().split()
        mask = pd.Series(True, index=df.index)
        for term in search_terms:
            term_mask = (
                df['name'].str.lower().str.contains(term, na=False) |
                df['ingredients'].str.lower().str.contains(term, na=False) |
                df['cuisine'].str.lower().str.contains(term, na=False)
            )
            mask &= term_mask
        return df[mask]
    return df