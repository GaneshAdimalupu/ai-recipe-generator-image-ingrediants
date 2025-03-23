
import streamlit as st
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from pages.widgets import __login__
import requests
from bs4 import BeautifulSoup
import random

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

# Load model and tokenizer with error handling
@st.cache_resource
def load_model_and_tokenizer():
    try:
        model_name = "google/flan-t5-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

def search_recipes(query):
    """Search for recipes using a web search"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        search_url = f"https://duckduckgo.com/html/?q={query}+recipe"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.select('.result'):
                title = result.select_one('.result__title')
                snippet = result.select_one('.result__snippet')
                link = result.select_one('.result__url')
                
                if title and snippet:
                    clean_title = ' '.join(title.get_text().split())
                    clean_snippet = ' '.join(snippet.get_text().split())
                    
                    if any(word in clean_title.lower() or word in clean_snippet.lower() 
                          for word in query.lower().split()):
                        results.append({
                            'title': clean_title,
                            'snippet': clean_snippet,
                            'url': link.get('href') if link else None
                        })
            
            return results[:3]
        return []
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def generate_random_cooking_info():
    """Generate random cooking information for recipe display"""
    times = ["20", "30", "45", "60", "90"]
    difficulties = ["Easy", "Medium", "Hard"]
    servings = ["2-4", "4-6", "6-8"]
    
    return {
        "time": f"{random.choice(times)} mins",
        "difficulty": random.choice(difficulties),
        "servings": random.choice(servings)
    }

def process_user_query(query, model, tokenizer):
    """Process user query and generate response"""
    try:
        # Enhance the prompt
        prompt = f"""
        Generate a helpful response about this recipe/cooking query: {query}
        Include:
        - Brief introduction or explanation
        - Key ingredients or techniques if relevant
        - Cooking tips if applicable
        - Health or dietary information if relevant
        Keep the response natural and conversational.
        """
        
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs.input_ids,
            max_length=300,
            num_beams=5,
            temperature=0.7,
            top_p=0.9,
            no_repeat_ngram_size=3
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    except Exception as e:
        return f"I apologize, but I encountered an error processing your query: {str(e)}"

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Add custom CSS for styling
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}

.user-message {
    background-color: #e3f2fd;
    border-left: 5px solid #2196f3;
}

.assistant-message {
    background-color: #f5f5f5;
    border-left: 5px solid #ff4b4b;
}

.recipe-card {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.recipe-info {
    display: flex;
    gap: 15px;
    margin-top: 10px;
    font-size: 0.9em;
    color: #666;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .recipe-card {
        background-color: #2d2d2d;
    }
    .user-message {
        background-color: #1a3a4a;
    }
    .assistant-message {
        background-color: #2d2d2d;
    }
}
</style>
""", unsafe_allow_html=True)

# Main page layout
st.title("👩‍🍳 Recipe Chat Assistant")
st.markdown("""
Ask me anything about recipes, cooking techniques, or ingredients! I'll help you find 
recipes and provide cooking advice.
""")

# Quick action buttons
quick_actions = [
    "Indian Recipes",
    "Quick Meals",
    "Vegetarian",
    "Desserts",
    "Healthy Options"
]

cols = st.columns(len(quick_actions))
for i, action in enumerate(quick_actions):
    with cols[i]:
        if st.button(action):
            prompt = f"Show me some {action.lower()}"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# Load AI model
tokenizer, model = load_model_and_tokenizer()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"""
            <div class="{message['role']}-message">
                {message['content']}
            </div>
        """, unsafe_allow_html=True)
        
        if message["role"] == "assistant" and "recipes" in message:
            for recipe in message["recipes"]:
                cooking_info = generate_random_cooking_info()
                st.markdown(f"""
                    <div class="recipe-card">
                        <h3>{recipe['title']}</h3>
                        <p>{recipe['snippet']}</p>
                        <div class="recipe-info">
                            <span>⏲️ {cooking_info['time']}</span>
                            <span>📊 {cooking_info['difficulty']}</span>
                            <span>👥 Serves {cooking_info['servings']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask about a recipe or cooking technique..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Add to search history
    if prompt not in st.session_state.search_history:
        st.session_state.search_history.append(prompt)
        if len(st.session_state.search_history) > 10:
            st.session_state.search_history.pop(0)
    
    # Generate response
    if model and tokenizer:
        with st.spinner("Thinking..."):
            # Generate AI response
            response = process_user_query(prompt, model, tokenizer)
            
            # Search for recipes
            recipes = search_recipes(prompt)
            
            # Add to messages
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "recipes": recipes
            })
            
            # Display response
            with st.chat_message("assistant"):
                st.write(response)
                if recipes:
                    st.markdown("### 📚 Related Recipes:")
                    for recipe in recipes:
                        cooking_info = generate_random_cooking_info()
                        st.markdown(f"""
                            <div class="recipe-card">
                                <h3>{recipe['title']}</h3>
                                <p>{recipe['snippet']}</p>
                                <div class="recipe-info">
                                    <span>⏲️ {cooking_info['time']}</span>
                                    <span>📊 {cooking_info['difficulty']}</span>
                                    <span>👥 Serves {cooking_info['servings']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

# Sidebar with history
with st.sidebar:
    if st.session_state.search_history:
        st.markdown("### 📜 Recent Searches")
        for query in reversed(st.session_state.search_history[-5:]):
            if st.button(query, key=f"history_{query}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
