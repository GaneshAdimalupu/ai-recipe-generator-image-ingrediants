from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import re
import json

def initialize_gemini_model(api_key):
    """Initialize and return a Gemini model instance"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=api_key,
        temperature=0.7
    )

def generate_recipe_from_name(model, recipe_name, dietary_options=None, cuisine_type=None, difficulty="Intermediate"):
    """Generate a recipe based on the given name using the Gemini API"""
    # Build the system prompt
    system_prompt = """You are a professional chef with expertise in creating detailed, accurate recipes. 
    When asked to create a recipe, provide a well-structured response with:
    1. A clear title starting with '#'
    2. An ingredients section with quantities, each item on a new line with bullet points
    3. Step-by-step instructions, numbered sequentially
    4. Complete nutritional information
    5. Cooking time, prep time, and serving size

    Format your response in clean Markdown with clear section headers."""
    
    # Build the human prompt
    prompt = f"Create a detailed recipe for '{recipe_name}'"
    
    if dietary_options:
        prompt += f" that is {', '.join(dietary_options)}"
        
    if cuisine_type and cuisine_type != "Any":
        prompt += f" in {cuisine_type} cuisine style"
        
    prompt += f". The recipe should be {difficulty} level difficulty."
    prompt += " Include a title, ingredients list with measurements, step-by-step instructions, cooking time, preparation time, and comprehensive nutritional information (calories, protein, carbs, fats, etc.)."
    
    # Generate the recipe
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    response = model.invoke(messages)
    return response.content

def parse_recipe_content(recipe_text, recipe_name=None):
    """Parse the generated recipe text into structured components"""
    try:
        # Extract title (Look for the first heading)
        title_match = re.search(r"#\s*(.*?)(?:\n|$)", recipe_text)
        title = title_match.group(1).strip() if title_match else recipe_name or "Recipe"
        
        # Extract ingredients section (between "Ingredients:" and the next section)
        ingredients_pattern = r"(?:##?\s*Ingredients|\*\*Ingredients\*\*|Ingredients:)(.*?)(?:##?\s*|Instructions:|Directions:|Steps:|$)"
        ingredients_section = re.search(ingredients_pattern, recipe_text, re.DOTALL | re.IGNORECASE)
        ingredients_text = ingredients_section.group(1).strip() if ingredients_section else ""
        
        # Extract individual ingredients (Look for bullet points or list items)
        ingredients = []
        for line in ingredients_text.split("\n"):
            clean_line = line.strip()
            if clean_line and (clean_line.startswith("-") or clean_line.startswith("*") or clean_line.startswith("•")):
                # Remove bullet point and clean up
                ingredient = re.sub(r"^[-*•]\s*", "", clean_line).strip()
                if ingredient:
                    ingredients.append(ingredient)
        
        # If no bullet points found, just use non-empty lines
        if not ingredients:
            ingredients = [line.strip() for line in ingredients_text.split("\n") if line.strip()]
        
        # Extract directions/instructions section
        directions_pattern = r"(?:##?\s*(?:Instructions|Directions|Steps)|\*\*(?:Instructions|Directions|Steps)\*\*|(?:Instructions|Directions|Steps):)(.*?)(?:##?\s*|Nutrition:|$)"
        directions_section = re.search(directions_pattern, recipe_text, re.DOTALL | re.IGNORECASE)
        directions_text = directions_section.group(1).strip() if directions_section else ""
        
        # Extract individual steps
        directions = []
        step_pattern = r"(?:\d+\.\s*|\d+\)\s*)(.*?)(?:\n|$)"
        steps = re.findall(step_pattern, directions_text)
        
        if steps:
            directions = [step.strip() for step in steps if step.strip()]
        else:
            # If no numbered steps found, use non-empty lines
            directions = [line.strip() for line in directions_text.split("\n") if line.strip()]
        
        # Extract nutrition information
        nutrition_pattern = r"(?:##?\s*Nutrition|\*\*Nutrition\*\*|Nutrition:)(.*?)(?:##?\s*|$)"
        nutrition_section = re.search(nutrition_pattern, recipe_text, re.DOTALL | re.IGNORECASE)
        nutrition_text = nutrition_section.group(1).strip() if nutrition_section else ""
        
        # Extract cooking and prep time
        time_info = {}
        time_patterns = {
            "prep_time": r"(?:Prep[aration]* Time:?|Prep:?)\s*([^\n]+)",
            "cook_time": r"(?:Cook(?:ing)? Time:?|Cook:?)\s*([^\n]+)",
            "total_time": r"(?:Total Time:?)\s*([^\n]+)",
            "servings": r"(?:Servings?:?|Yields?:?)\s*([^\n]+)"
        }
        
        for key, pattern in time_patterns.items():
            match = re.search(pattern, recipe_text, re.IGNORECASE)
            if match:
                time_info[key] = match.group(1).strip()
        
        # Structure the result
        result = {
            "title": title,
            "ingredients": ingredients,
            "directions": directions,
            "nutrition_text": nutrition_text,
            "time_info": time_info,
            "raw_text": recipe_text  # Include raw text for fallback
        }
        
        return result
    
    except Exception as e:
        # Return a basic structure with the raw text on parsing failure
        return {
            "title": recipe_name or "Recipe",
            "ingredients": [],
            "directions": [],
            "nutrition_text": "",
            "time_info": {},
            "raw_text": recipe_text,
            "parse_error": str(e)
        }