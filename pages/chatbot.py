import time
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

from pages.widgets import __login__

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

# Get current user
current_user = login_ui.get_username()

# Show navigation sidebar
login_ui.nav_sidebar()

def stream_data(text, delay: float = 0.02):
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)

st.title("🧠 Chef AI Companion")
st.caption("🚀 Your can ask me anything related to cooking and I will help you out with the recipe")

# Get the Google API key from Streamlit secrets
# Your .streamlit/secrets.toml has API_KEY directly under [mongo]
try:
    google_api_key = st.secrets["mongo"]["API_KEY"]
except KeyError:
    st.error("Google API key not found in .streamlit/secrets.toml")
    st.info("Please check your API key in the secrets file")
    st.stop()

# Initialize the Gemini model
llm_engine = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=google_api_key,
    temperature=0.7,
    streaming=True,
    convert_system_message_to_human=True  # Gemini handles system prompts differently
)

system_prompt = SystemMessagePromptTemplate.from_template(
    "You are Be My Chef AI, an expert cooking assistant. You help users with recipes, cooking techniques, "
    "ingredient substitutions, and any food-related questions. Be friendly, enthusiastic, and provide "
    "detailed, step-by-step instructions when sharing recipes. Always respond in English. "
    "When providing recipes, include comprehensive nutritional information for each recipe (calories, protein, "
    "carbohydrates, fats, fiber, etc.). When users ask for recipe suggestions, always provide at least 6-8 diverse "
    "recipe options, not limiting to just 5. For each recipe, include prep time, cooking time, serving size, "
    "difficulty level, and any dietary labels (vegetarian, gluten-free, etc.)."
    "\n\nFor single-word queries (like an ingredient name), organize your response into 5 categories: "
    "Quick & Easy, Healthy, Gourmet, Comfort Food, and International. Clearly label each category with '## [Category Name]' "
    "and provide at least one detailed recipe for each category related to the query word."
)

if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm Be My Chef. What recipe would you like me to make? 💻"}]

chat_container = st.container()

with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_query = st.chat_input("Ask me about any recipe or cooking question...")

def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | llm_engine | StrOutputParser()
    return processing_pipeline.invoke({})

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    return ChatPromptTemplate.from_messages(prompt_sequence)

if user_query:
    # Special handling for one-word queries (likely an ingredient or cuisine)
    if len(user_query.strip().split()) == 1:
        input_word = user_query.strip()
        enhanced_query = f"Generate at least 6 diverse recipes using {input_word} as a main ingredient or theme. Group them into 5 categories: Quick & Easy, Healthy, Gourmet, Comfort Food, and International. For each recipe, include a title, brief description, ingredients, instructions, and nutritional information."
        st.session_state.message_log.append({"role": "user", "content": enhanced_query})
    else:
        st.session_state.message_log.append({"role": "user", "content": user_query})
    
    with st.spinner("🧠 Cooking up a response..."):
        prompt_chain = build_prompt_chain()
        try:
            ai_response = generate_ai_response(prompt_chain)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            ai_response = "I'm having trouble connecting to my cooking brain. Please check your API key or try again later."
    
    with st.chat_message("ai"):
        # If the input was a single word, we'll create category containers
        if len(user_query.strip().split()) == 1:
            st.write(f"Here are recipe suggestions featuring {user_query}:")
            
            # Create tabs for different recipe categories
            tabs = st.tabs(["Quick & Easy", "Healthy", "Gourmet", "Comfort Food", "International"])
            
            # We'll still show the complete response in the chat flow to avoid losing content
            response_container = st.empty()
            streamed_text = ""
            for word in stream_data(ai_response):
                streamed_text += word
                response_container.markdown(streamed_text)
        else:
            # Standard response for multi-word queries
            response_container = st.empty()
            streamed_text = ""
            for word in stream_data(ai_response):
                streamed_text += word
                response_container.markdown(streamed_text)
    
    st.session_state.message_log.append({"role": "ai", "content": ai_response})
    st.rerun()