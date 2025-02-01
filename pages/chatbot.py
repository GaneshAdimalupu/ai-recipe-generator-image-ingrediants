import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
from datetime import datetime
from mongodb.db import get_database

def render_chatbot_content():
    st.title("🍳 Chef AI Assistant")
    st.markdown("""
    <style>
    .user-message { padding: 12px; border-radius: 15px; background: #f0f2f6; margin: 8px 0; }
    .ai-message { padding: 12px; border-radius: 15px; background: #e6f4ff; margin: 8px 0; }
    .timestamp { font-size: 0.8em; color: #666; }
    </style>
    """, unsafe_allow_html=True)

    # Load recipe-specific model
    @st.cache_resource
    def load_model():
        tokenizer = AutoTokenizer.from_pretrained("VishalMysore/cookgptlama")
        model = AutoModelForCausalLM.from_pretrained("VishalMysore/cookgptlama")
        return tokenizer, model

    tokenizer, model = load_model()
    db = get_database()
    conversation_col = db["chatbot_conversation"]

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat input with clear prompt
    user_input = st.chat_input("Ask me about recipes (e.g., 'Chicken curry recipe'):")

    if user_input:
        # Store user message
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": current_time
        })

        # Generate response
        with st.spinner("🧑🍳 Preparing your recipe..."):
            try:
                prompt = f"Q: Provide detailed step-by-step instructions for {user_input}\nA:"
                inputs = tokenizer(prompt, return_tensors="pt")
                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=500,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.split("A:")[-1].strip()
                
                # Format response with markdown
                formatted_response = "\n".join([f"- {line.strip()}" 
                                              for line in response.split("\n") if line.strip()])
                
                # Store in session and DB
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": formatted_response,
                    "time": current_time
                })
                
                conversation_col.insert_many([
                    {"user": st.session_state.get("username", "Anonymous"),
                     "content": user_input, 
                     "time": current_time,
                     "type": "user_query"},
                    {"user": "ChefAI",
                     "content": formatted_response,
                     "time": current_time,
                     "type": "ai_response"}
                ])

            except Exception as e:
                error_response = f"⚠️ Sorry, I'm having trouble in the kitchen. Please try again later. Error: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": error_response,
                    "time": current_time
                })

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>👤 You</strong><br>
                {message["content"]}
                <div class="timestamp">{message["time"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-message">
                <strong>🤖 Chef AI</strong><br>
                {message["content"].replace('-', '•')}
                <div class="timestamp">{message["time"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # Clear button with confirmation
    if st.button("🧹 Clear Conversation"):
        st.session_state.chat_history = []
        st.experimental_rerun()


if __name__ == "__main__":
    if not st.session_state.get("LOGGED_IN", False):
        st.switch_page("streamlit_app.py")

    from pages.widgets import __login__

    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
    )
    login_ui.nav_sidebar()

    render_chatbot_content()