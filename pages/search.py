import streamlit as st
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from pages.widgets import __login__

# Initialize login UI
login_ui = __login__(
    auth_token="your_courier_auth_token",
    company_name="Be My Chef AI",
    width=200,
    height=200,
)

# Check if user is logged in and show navigation
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")
else:
    # Show navigation sidebar
    login_ui.nav_sidebar()



st.title("🔎 Hugging Face Chatbot with Search")

"""
This chatbot uses a Hugging Face model for natural language understanding and DuckDuckGo search for fetching web data. Replace with different models as required.
"""


# Load Hugging Face model and tokenizer
@st.cache_resource
def load_model_and_tokenizer():
    model_name = "google/flan-t5-base"  # Replace with any suitable model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model


tokenizer, model = load_model_and_tokenizer()

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can search the web. How can I help you?",
        }
    ]

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Process user input
if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Generate response with Hugging Face model
    input_text = f"Question: {prompt} Answer:"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(
        inputs.input_ids, max_length=150, num_beams=5, early_stopping=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Append and display assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    # DuckDuckGo search integration
    st.write("**Fetching additional context from the web...**")
    import requests

    query = prompt.replace(" ", "+")
    search_url = f"https://duckduckgo.com/html/?q={query}"
    try:
        search_response = requests.get(search_url)
        if search_response.status_code == 200:
            st.write("Search results fetched successfully.")
            # You can parse and show relevant search results here
        else:
            st.write("Failed to fetch search results.")
    except Exception as e:
        st.write(f"Error: {e}")
