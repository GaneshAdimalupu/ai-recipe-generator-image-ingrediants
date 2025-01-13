import streamlit as st

# Initialize login check
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")

from datetime import datetime
from mongodb.db import get_database
from pages.widgets import __login__
import base64
from PIL import Image
import io





# Initialize login UI with proper authentication token
login_ui = __login__(
    auth_token="your_courier_auth_token",
    company_name="Be My Chef AI",
    width=200,
    height=200,
)

# Show navigation sidebar
login_ui.nav_sidebar()

# Add this function at the top with other helper functions
def has_user_liked_post(post_id, username):
    """Check if a user has already liked a post"""
    like = likes_collection.find_one({
        "post_id": post_id,
        "user": username
    })
    return bool(like)

# Helper Functions
def format_time(time_value):
    """Format time value consistently whether it's string or datetime"""
    if isinstance(time_value, str):
        try:
            # Parse string to datetime if it's a string
            return datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.now()  # Fallback if parsing fails
    return time_value  # Return as is if it's already datetime

# Enhanced CSS for social media style
st.markdown("""
<style>
    /* Post card styling */
    .post-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }
    
    .username {
        font-weight: 600;
        color: #262626;
    }
    
    .post-time {
        color: #8e8e8e;
        font-size: 12px;
    }
    
    .post-content {
        margin: 15px 0;
        font-size: 16px;
        line-height: 1.5;
    }
    
    .post-image {
        width: 100%;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .interaction-bar {
        display: flex;
        gap: 20px;
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #dbdbdb;
    }
    
    .interaction-button {
        display: flex;
        align-items: center;
        gap: 5px;
        color: #262626;
        cursor: pointer;
    }
    
    /* Create post form styling */
    .create-post-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .post-card, .create-post-card {
            background-color: #262626;
            color: #ffffff;
        }
        .username {
            color: #ffffff;
        }
        .post-time {
            color: #a8a8a8;
        }
        .interaction-button {
            color: #ffffff;
        }
    }
</style>
""", unsafe_allow_html=True)


# Connect to MongoDB
db = get_database()
posts_collection = db["posts"]
comments_collection = db["comments"]
likes_collection = db["likes"]

def save_image(uploaded_file):
    """Convert uploaded image to base64 for storage"""
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        
        # Convert to base64
        base64_image = base64.b64encode(bytes_data).decode()
        return base64_image
    return None

def load_image(base64_string):
    """Convert base64 string back to image for display"""
    if base64_string:
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        return image
    return None

# Title with subtle styling
st.markdown("# 📝 Recipe Social Feed")
st.markdown("Share your culinary creations with the community!")

# Create new post section
st.markdown("### Create New Post")
current_user = login_ui.get_username()
if not current_user:
    st.warning("Please log in to create a post")
else:
    with st.form("post_form", clear_on_submit=True):
        st.markdown('<div class="create-post-card">', unsafe_allow_html=True)
        
        post_title = st.text_input("Recipe Title", placeholder="Give your recipe a catchy name!")
        post_content = st.text_area("Recipe Details", placeholder="Share your recipe, cooking tips, or food story...", height=150)
        uploaded_file = st.file_uploader("Add a photo of your dish", type=['jpg', 'jpeg', 'png'])
        ingredients = st.text_area("Ingredients (optional)", placeholder="List your ingredients here...")
        instructions = st.text_area("Cooking Instructions (optional)", placeholder="Share your cooking steps...")
        
        tags = st.multiselect(
            "Add Tags",
            ["Vegetarian", "Vegan", "Gluten-Free", "Quick & Easy", "Dessert", "Main Course", "Breakfast", "Lunch", "Dinner"]
        )
        
        submitted = st.form_submit_button("Share Recipe 🚀")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if post_content.strip() and post_title.strip():
                image_data = save_image(uploaded_file)
                
                new_post = {
                    "title": post_title,
                    "content": post_content,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "tags": tags,
                    "image": image_data,
                    "user": current_user,  # Use the actual username
                    "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "likes": 0,
                    "comments_count": 0
                }
                
                posts_collection.insert_one(new_post)
                st.success("Recipe posted successfully! 🎉")
            else:
                st.error("Please add a title and description for your recipe.")

# Display existing posts
st.markdown("## 📱 Recipe Feed")

# Add filters
col1, col2 = st.columns([2, 1])
with col1:
    sort_by = st.selectbox(
        "Sort by",
        ["Most Recent", "Most Liked", "Most Commented"]
    )
with col2:
    filter_tag = st.multiselect("Filter by tags", ["Vegetarian", "Vegan", "Gluten-Free", "Quick & Easy"])

# Get posts from MongoDB with sorting
if sort_by == "Most Recent":
    all_posts = list(posts_collection.find().sort("time", -1))
elif sort_by == "Most Liked":
    all_posts = list(posts_collection.find().sort("likes", -1))
else:
    all_posts = list(posts_collection.find().sort("comments_count", -1))

# Filter by tags if selected
if filter_tag:
    all_posts = [post for post in all_posts if any(tag in post.get("tags", []) for tag in filter_tag)]

if all_posts:
    for post in all_posts:
        st.markdown('<div class="post-card">', unsafe_allow_html=True)

        # Format the time properly
        display_time = format_time(post['time']).strftime('%Y-%m-%d %H:%M')
        
        # In the post display section, update the username display:
        current_user = login_ui.get_username()
        is_author = post['user'] == current_user
        author_badge = "✍️ Author" if is_author else ""

        st.markdown(f"""
            <div class="post-header">
                <img src="https://api.dicebear.com/6.x/avataaars/svg?seed={post['user']}" class="user-avatar">
                <div>
                    <div class="username">👩‍🍳 {post['user']} {author_badge}</div>
                    <div class="post-time">🕒 {display_time}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Post title
        st.markdown(f"### {post['title']}")
        
        # Display image if exists
        if post.get('image'):
            image = load_image(post['image'])
            if image:
                st.image(image, use_container_width=True)
        
        # Post content
        st.markdown(f"<div class='post-content'>{post['content']}</div>", unsafe_allow_html=True)
        
        # Recipe details
        if post.get('ingredients'):
            with st.expander("📝 View Recipe Details"):
                st.markdown("#### Ingredients")
                st.write(post['ingredients'])
                if post.get('instructions'):
                    st.markdown("#### Instructions")
                    st.write(post['instructions'])
        
        # Tags
        if post.get('tags'):
            st.markdown(' '.join([f'`#{tag}`' for tag in post['tags']]))
        
        # Interaction buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            current_user = login_ui.get_username()
            has_liked = has_user_liked_post(post["_id"], current_user) if current_user else False
            like_button_text = "❤️" if has_liked else "🤍"
            
            if st.button(f"{like_button_text} {post.get('likes', 0)}", key=f"like_{str(post['_id'])}"):
                if not current_user:
                    st.warning("Please log in to like posts")
                elif not has_liked:
                    # Add like to likes collection
                    likes_collection.insert_one({
                        "post_id": post["_id"],
                        "user": current_user,
                        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    # Update post likes count
                    posts_collection.update_one(
                        {"_id": post["_id"]},
                        {"$inc": {"likes": 1}}
                    )
                    st.rerun()
        
        with col2:
            if st.button(f"💬 {post.get('comments_count', 0)}", key=f"comment_{post['_id']}"):
                st.session_state['show_comments'] = post['_id']
        
        # Comments section
        if st.session_state.get('show_comments') == post['_id']:
            with st.expander("Comments", expanded=True):
                # Add new comment
                with st.form(f"comment_form_{post['_id']}", clear_on_submit=True):
                    comment = st.text_area("Add a comment", key=f"comment_input_{post['_id']}")
                    if st.form_submit_button("Post Comment"):
                        current_user = login_ui.get_username()
                        if not current_user:
                            st.warning("Please log in to comment")
                        elif comment.strip():
                            comments_collection.insert_one({
                                "post_id": post["_id"],
                                "user": current_user,  # Use the actual username
                                "content": comment,
                                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            posts_collection.update_one(
                                {"_id": post["_id"]},
                                {"$inc": {"comments_count": 1}}
                            )
                            st.rerun()
                
                # Update the comment display part
                comments = comments_collection.find({"post_id": post["_id"]}).sort("time", -1)
                for comment in comments:
                    comment_time = format_time(comment['time']).strftime('%Y-%m-%d %H:%M')
                    st.markdown(f"""
                        <div style='padding: 10px; border-left: 2px solid #e0e0e0; margin: 5px 0;'>
                            <strong>{comment['user']}</strong> • {comment_time}<br>
                            {comment['content']}
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No recipes posted yet. Be the first to share your culinary creation! 👨‍🍳")