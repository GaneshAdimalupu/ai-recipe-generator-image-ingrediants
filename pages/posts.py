import streamlit as st
from datetime import datetime
from post.components.post_card import render_post_card
from post.components.filter_control import render_filter_controls, render_sidebar_filters
from post.models.db_schema import (
    get_trending_posts,
    search_posts,
    posts_collection,
    bookmarks_collection
)
from post.styles.posts_styles import apply_post_styles
import base64

def initialize_session_state():
    """Initialize all required session state variables"""
    if 'show_new_post_form' not in st.session_state:
        st.session_state.show_new_post_form = False
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "All Posts"
    if 'feed_page' not in st.session_state:
        st.session_state.feed_page = 1
    if 'posts_per_page' not in st.session_state:
        st.session_state.posts_per_page = 5

def get_all_posts(limit=20, skip=0, query=None, sort_params=None):
    """Get all posts with pagination and optional filtering"""
    if query is None:
        query = {}
    if sort_params is None:
        sort_params = [("time", -1)]
    
    return list(posts_collection.find(query)
               .sort(sort_params)
               .skip(skip)
               .limit(limit))

def handle_image_upload(uploaded_file):
    """Process uploaded image and convert to base64"""
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode()
            return base64_image
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None
    return None

def render_new_post_form(username):
    """Render the form for creating a new post"""
    st.markdown("### 📝 Share Your Recipe")
    
    with st.form("new_post_form", clear_on_submit=True):
        title = st.text_input("Recipe Title", placeholder="Give your recipe a catchy name!")
        content = st.text_area("Recipe Details", placeholder="Share your recipe, cooking tips, or food story...", height=150)
        
        uploaded_file = st.file_uploader("Add Photos", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            ingredients = st.text_area("Ingredients", placeholder="List your ingredients here...", height=150)
        with col2:
            instructions = st.text_area("Cooking Instructions", placeholder="Share your cooking steps...", height=150)
        
        col3, col4 = st.columns(2)
        with col3:
            cooking_time = st.number_input("Cooking Time (minutes)", min_value=1)
            servings = st.number_input("Servings", min_value=1)
        with col4:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            cuisine = st.selectbox("Cuisine Type", ["Italian", "Mexican", "Indian", "Chinese", "American", "Mediterranean", "Japanese", "Thai", "French", "Other"])
        
        suggested_tags = ["Breakfast", "Lunch", "Dinner", "Dessert", "Vegetarian", "Vegan", "Gluten-Free", "Quick & Easy", "Healthy", "Comfort Food", "Party", "Budget-Friendly"]
        tags = st.multiselect("Add Tags", suggested_tags)
        
        submitted = st.form_submit_button("Share Recipe 🚀")
        if submitted and title.strip() and content.strip():
            image_data = handle_image_upload(uploaded_file) if uploaded_file else None
            
            new_post = {
                "title": title,
                "content": content,
                "ingredients": ingredients,
                "instructions": instructions,
                "cooking_time": cooking_time,
                "servings": servings,
                "difficulty": difficulty,
                "cuisine": cuisine,
                "tags": tags,
                "image": image_data,
                "user": username,
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "likes": 0,
                "comments_count": 0
            }
            
            posts_collection.insert_one(new_post)
            st.success("Recipe shared successfully! 🎉")
            return True
        elif submitted:
            st.error("Please add a title and description for your recipe.")
        return False

def render_feed(username):
    """Render the main social feed with all posts"""
    # Apply styles
    apply_post_styles()
    
    # Page title and description
    st.title("🍳 Recipe Social Feed")
    st.markdown("Share and discover amazing recipes from our community!")
    
    # Tabs for different views
    tab_names = ["📱 All Posts", "🔥 Trending", "🔖 Saved", "👤 My Posts"]
    tabs = st.tabs(tab_names)
    
    # Get filter settings from sidebar
    sidebar_filters = render_sidebar_filters()
    search_query = sidebar_filters["search_query"]
    selected_tags = sidebar_filters["selected_tags"]
    
    # All Posts tab
    with tabs[0]:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown("### 🌟 All Community Recipes")
        with col2:
            if st.button("➕ New Post", use_container_width=True):
                st.session_state.show_new_post_form = True
        
        if st.session_state.get("show_new_post_form", False):
            if render_new_post_form(username):
                st.session_state.show_new_post_form = False
                st.rerun()
        
        # Get filter and sort parameters
        query, sort_params = render_filter_controls()
        
        # Calculate pagination
        skip = (st.session_state.feed_page - 1) * st.session_state.posts_per_page
        
        # Get and display posts
        if search_query:
            posts = search_posts(search_query, selected_tags)
        else:
            posts = get_all_posts(
                limit=st.session_state.posts_per_page,
                skip=skip,
                query=query,
                sort_params=sort_params
            )
        
        if posts:
            for post in posts:
                render_post_card(post, username, view_type="feed")
            
            # Pagination
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.session_state.feed_page > 1:
                    if st.button("← Previous"):
                        st.session_state.feed_page -= 1
                        st.rerun()
            with col3:
                if len(posts) == st.session_state.posts_per_page:
                    if st.button("Next →"):
                        st.session_state.feed_page += 1
                        st.rerun()
        else:
            st.info("No posts found. Be the first to share a recipe! 👨‍🍳")
    
    # Trending tab
    with tabs[1]:
        st.markdown("### 🔥 Trending Recipes")
        trending_posts = get_trending_posts()
        if trending_posts:
            for post in trending_posts:
                render_post_card(post, username, view_type="trending")
        else:
            st.info("No trending posts yet!")
    
    # Saved recipes tab
    with tabs[2]:
        st.markdown("### 🔖 Saved Recipes")
        saved_posts = list(bookmarks_collection.find({"user": username}))
        if saved_posts:
            for bookmark in saved_posts:
                post = posts_collection.find_one({"_id": bookmark["post_id"]})
                if post:
                    render_post_card(post, username, view_type="saved")
        else:
            st.info("No saved recipes yet. Click the bookmark icon on recipes to save them!")
    
    # My posts tab
    with tabs[3]:
        st.markdown("### 👤 My Posts")
        my_posts = list(posts_collection.find({"user": username}).sort("time", -1))
        if my_posts:
            for post in my_posts:
                render_post_card(post, username, view_type="my_posts")
        else:
            st.info("You haven't shared any recipes yet. Click 'Create New Post' to get started!")

def get_current_username():
    """Get username from the login widget cookies"""
    if 'username' in st.session_state:
        return st.session_state.username
    # Check cookies as fallback
    from pages.widgets import __login__
    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
    )
    return login_ui.get_username()


def main():
    """Main function to handle the social feed"""
    # Initialize session state
    initialize_session_state()
    
    # Check if user is logged in
    if not st.session_state.get("LOGGED_IN", False):
        st.switch_page("streamlit_app.py")
        return
    
        # Get current user with improved error handling
    username = get_current_username()


    
    if not username:
        st.error("Please log in to access the social feed.")
        st.error("If you're seeing this message after logging in, please try refreshing the page.")
        if st.button("Return to Login"):
            st.switch_page("streamlit_app.py")
        return
    
    try:
        # Render the main feed
        render_feed(username)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try refreshing the page. If the error persists, contact support.")

if __name__ == "__main__":
    main()
