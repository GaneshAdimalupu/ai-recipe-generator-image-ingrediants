import time
import streamlit as st
from langchain_ollama import ChatOllama
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

st.title("🧠 DeepSeek Code Companion")
st.caption("🚀 Your AI Pair Programmer with Debugging Superpowers")


llm_engine = ChatOllama(
    model="llama2",
    base_url="http://localhost:11434",
    temperature=1
)


system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI coding assistant. Provide concise, correct solutions "
    "with strategic print statements for debugging. Always respond in English."
)

if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today? 💻"}]

chat_container = st.container()

with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_query = st.chat_input("Type your coding question here...")

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
    st.session_state.message_log.append({"role": "user", "content": user_query})
    with st.spinner("🧠 Processing..."):
        prompt_chain = build_prompt_chain()
        ai_response = generate_ai_response(prompt_chain)
    
    with st.chat_message("ai"):
        response_container = st.empty()
        streamed_text = ""
        for word in stream_data(ai_response):
            streamed_text += word
            response_container.markdown(streamed_text)
    
    st.session_state.message_log.append({"role": "ai", "content": ai_response})
    st.rerun()
