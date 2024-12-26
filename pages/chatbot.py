import streamlit as st
from transformers import pipeline
from datetime import datetime
from pymongo import MongoClient
from mongodb.db import get_database
from navigation import make_sidebar

make_sidebar()

# Connect to MongoDB
db = get_database()
conversation = db["conversation"]

# Initialize GPT model
generator = pipeline("text-generation", model="gpt2", device=-1)

# App Title
st.title("Recipe Generator 🍳")

# Introduction
st.markdown(
    """
    Welcome to the Recipe Generator! 🍲
    - Enter ingredients or a recipe idea, and let the AI create a recipe for you!
"""
)


# Function to generate recipe
def generate_recipe(query):
    prompt = f"Create a recipe based on the following: {query}"
    result = generator(prompt, max_length=150, num_return_sequences=1)
    return result[0]["generated_text"]


# Session State Initialization
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# User Input
user_input = st.text_input("Enter your recipe request or ingredients:")

if user_input:
    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Save conversation locally and in MongoDB
    st.session_state.conversation.append(
        {"role": "User", "message": user_input, "timestamp": current_time}
    )
    conversation.insert_one(
        {
            "user": "Anonymous",  # Replace with actual user data if applicable
            "content": user_input,
            "time": current_time,
        }
    )

    # Generate and store AI response
    try:
        recipe = generate_recipe(user_input)
        st.session_state.conversation.append(
            {"role": "AI", "message": recipe, "timestamp": current_time}
        )
    except Exception as e:
        recipe = f"Error generating recipe: {e}"
        st.session_state.conversation.append(
            {"role": "AI", "message": recipe, "timestamp": current_time}
        )

# Display Conversation
for convo in st.session_state.conversation:
    st.markdown(f"**{convo['role']} ({convo['timestamp']}):** {convo['message']}")
    st.markdown("---")

if st.button("Clear Conversation"):
    st.session_state.conversation = []
    st.experimental_rerun()

# Display Recent Posts from MongoDB
st.write("## 📰 Recent Posts")
all_conversation = list(conversation.find().sort("time", -1))
if all_conversation:
    for conv in all_conversation:
        st.write(f"### Anonymous said:")
        st.write(conv["content"])
        st.write(f"🕒 Asked on: {conv['time']}")
        st.write("---")
else:
    st.info("No posts yet. Be the first to post!")
