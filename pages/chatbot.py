import streamlit as st
from transformers import pipeline
from datetime import datetime

from navigation import make_sidebar

make_sidebar()

# Initialize the GPT model (you can replace with another model like T5, GPT-2, etc.)
# Force the model to load on CPU
generator = pipeline("text-generation", model="gpt2", device=-1)


# Title of the app
st.title("Recipe Generator 🍳")

# Introduction text
st.markdown(
    """
    Welcome to the Recipe Generator! 🍲
    - You can ask for recipes based on ingredients or specify the type of recipe you'd like.
    - Just type your request below and let the AI generate the recipe for you!
    - You can continue interacting with the app, asking for different recipes or changing your ingredients.
"""
)


# Function to generate recipe based on the user input
def generate_recipe(query):
    # Generate text based on the input query (you can tweak the prompt for better results)
    prompt = f"Create a recipe based on the following: {query}"
    result = generator(prompt, max_length=150, num_return_sequences=1)
    return result[0]["generated_text"]


# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# User input for recipe request
user_input = st.text_input("Enter your recipe request or ingredients:")

# Process the user input and update the conversation
if user_input:
    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add user query to the conversation history with timestamp
    st.session_state.conversation.append(
        {"role": "User", "message": user_input, "timestamp": current_time}
    )

    # Generate recipe based on user input
    recipe = generate_recipe(user_input)

    # Add generated recipe to conversation history with timestamp
    st.session_state.conversation.append(
        {"role": "AI", "message": recipe, "timestamp": current_time}
    )

# Display the conversation (history of user queries and AI responses)
for conversation in st.session_state.conversation:
    st.markdown(
        f"**{conversation['role']} ({conversation['timestamp']}):** {conversation['message']}"
    )
    st.markdown(
        "---"
    )  # Add a line after each message to differentiate the conversation

# Option to clear the session state
if st.button("Clear Conversation"):
    st.session_state.conversation = []
    st.rerun()
