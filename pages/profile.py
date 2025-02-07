import streamlit as st
from datetime import datetime
import base64
from PIL import Image
import io
from pages.posts import get_current_username
from post.models.db_schema import (
    posts_collection,
    likes_collection,
    bookmarks_collection,
    followers_collection
)

def get_profile_stats(username):
    """Get user's profile statistics"""
    # Get post count
    posts_count = posts_collection.count_documents({"user": username})
    
    # Get followers count
    followers_count = followers_collection.count_documents({"following": username})
    
    # Get following count
    following_count = followers_collection.count_documents({"follower": username})
    
    return posts_count, followers_count, following_count

def upload_profile_picture():
    """Handle profile picture upload"""
    uploaded_file = st.file_uploader("Change Profile Picture", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        try:
            # Read the file into bytes
            bytes_data = uploaded_file.getvalue()
            
            # Convert to base64
            base64_image = base64.b64encode(bytes_data).decode()
            
            # Update user's profile picture in database
            # Note: You'll need to add a users collection and update the user document
            return base64_image
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
    return None

def render_profile_page(username):
    """Render the user profile page"""
    # Apply custom CSS
    st.markdown("""
    <style>
        /* Profile Section */
        .profile-section {
            padding: 20px;
            margin-bottom: 30px;
        }
        
        /* Stats Section */
        .stats-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }
        
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        
        /* Posts Grid */
        .posts-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        
        .grid-post {
            aspect-ratio: 1;
            object-fit: cover;
            width: 100%;
            transition: transform 0.2s;
        }
        
        .grid-post:hover {
            transform: scale(1.02);
        }
        
        /* Bio Section */
        .bio-section {
            margin: 20px 0;
            padding: 10px;
        }
        
        /* Edit Profile Button */
        .edit-profile-btn {
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Get user stats
    posts_count, followers_count, following_count = get_profile_stats(username)
    
    # Profile Header Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile Picture
        st.image(
            "https://api.dicebear.com/6.x/avataaars/svg?seed=" + username,
            width=150
        )
        if st.button("Edit Profile Picture"):
            profile_pic = upload_profile_picture()
            if profile_pic:
                st.success("Profile picture updated!")
                st.rerun()
    
    with col2:
        # Username and Edit Profile Button
        st.markdown(f"### @{username}")
        st.button("Edit Profile", key="edit_profile")
        
        # Stats Row
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        with stats_col1:
            st.markdown(f"**{posts_count}** posts")
        with stats_col2:
            st.markdown(f"**{followers_count}** followers")
        with stats_col3:
            st.markdown(f"**{following_count}** following")
        
        # Bio Section
        st.markdown("🧑‍🍳 Food enthusiast and recipe creator")
        st.markdown("📍 Making delicious meals and sharing them with the world")
    
    # Posts Grid Section
    st.markdown("### Posts")
    
    # Get user's posts
    posts = list(posts_collection.find({"user": username}).sort("time", -1))
    
    # Create grid layout
    if posts:
        # Split posts into rows of 3
        for i in range(0, len(posts), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(posts):
                    post = posts[i + j]
                    with col:
                        # Display post image or placeholder
                        if post.get('image'):
                            try:
                                image = Image.open(io.BytesIO(base64.b64decode(post['image'])))
                                st.image(image, use_container_width=True)
                            except Exception:
                                st.image("https://via.placeholder.com/300", use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/300", use_container_width=True)
                        
                        # Post stats
                        st.markdown(f"""
                            ❤️ {post.get('likes', 0)} &nbsp;&nbsp; 
                            💬 {post.get('comments_count', 0)}
                        """)
    else:
        st.info("No posts yet! Share your first recipe to get started.")

def main():
    """Main function to handle the profile page"""
    if not st.session_state.get("LOGGED_IN", False):
        st.switch_page("streamlit_app.py")
        return
        # Get current user with improved error handling
    username = get_current_username()

        # Initialize login UI
    from pages.widgets import __login__

    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
    )

    # Show navigation
    login_ui.nav_sidebar()

    if not username:
        st.error("Please log in to access the social feed.")
        st.error("If you're seeing this message after logging in, please try refreshing the page.")
        if st.button("Return to Login"):
            st.switch_page("streamlit_app.py")
        return
    
    try:
        render_profile_page(username)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try refreshing the page. If the error persists, contact support.")


if __name__ == "__main__":
    main()