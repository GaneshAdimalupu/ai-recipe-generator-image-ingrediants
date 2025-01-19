import streamlit as st
from datetime import datetime
from mongodb.db import get_database
import base64
from PIL import Image
import io
import time

# Initialize MongoDB connections
db = get_database()
posts_collection = db["posts"]
comments_collection = db["comments"]
likes_collection = db["likes"]
bookmarks_collection = db["bookmarks"]

# Enhanced CSS for modern social media styling
st.markdown("""
<style>
    /* Post card styling */
    .post-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .post-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .user-info {
        display: flex;
        flex-direction: column;
        margin-left: 15px;
    }
    
    .username {
        font-weight: 600;
        color: #1a1a1a;
        font-size: 16px;
    }
    
    .post-meta {
        color: #666;
        font-size: 14px;
        margin-top: 2px;
    }
    
    .post-content {
        font-size: 16px;
        line-height: 1.6;
        color: #333;
        margin: 15px 0;
    }
    
    .post-image {
        width: 100%;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    .interaction-bar {
        display: flex;
        gap: 20px;
        padding: 10px 0;
        border-top: 1px solid #eee;
        border-bottom: 1px solid #eee;
        margin: 15px 0;
    }
    
    .interaction-button {
        display: flex;
        align-items: center;
        gap: 5px;
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        transition: color 0.2s ease;
        font-size: 14px;
    }
    
    .interaction-button:hover {
        color: #ff4b4b;
    }
    
    .comment-section {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
    }
    
    .comment-item {
        background-color: white;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
    
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
    }
    
    .tag {
        background-color: #f0f2f5;
        color: #666;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
    }
    
    /* Filter bar styling */
    .filter-bar {
        display: flex;
        gap: 10px;
        padding: 15px;
        background-color: white;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .post-card {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        .username {
            color: #ffffff;
        }
        .post-content {
            color: #e0e0e0;
        }
        .comment-section {
            background-color: #2d2d2d;
        }
        .comment-item {
            background-color: #333;
        }
        .tag {
            background-color: #333;
            color: #e0e0e0;
        }
        .filter-bar {
            background-color: #1e1e1e;
        }
    }
</style>
""", unsafe_allow_html=True)

def format_time(time_value):
    """Format time value for display"""
    if isinstance(time_value, str):
        try:
            time_value = datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return "Just now"
    
    now = datetime.now()
    diff = now - time_value
    
    if diff.days > 7:
        return time_value.strftime('%B %d, %Y')
    elif diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "Just now"

def handle_image_upload(uploaded_file):
    """Process uploaded image"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode()
        return base64_image
    return None

def create_new_post():
    """Enhanced post creation form"""
    st.markdown("### 📝 Share Your Recipe")
    
    with st.form("new_post_form", clear_on_submit=True):
        # Title input
        title = st.text_input("Recipe Title", placeholder="Give your recipe a catchy name!")
        
        # Rich text content
        content = st.text_area(
            "Recipe Details",
            placeholder="Share your recipe, cooking tips, or food story...",
            height=150
        )
        
        # Image upload with preview
        uploaded_file = st.file_uploader("Add Photos", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
        
        # Ingredients and Instructions
        col1, col2 = st.columns(2)
        with col1:
            ingredients = st.text_area(
                "Ingredients",
                placeholder="List your ingredients here...",
                height=150
            )
        with col2:
            instructions = st.text_area(
                "Cooking Instructions",
                placeholder="Share your cooking steps...",
                height=150
            )
        
        # Tags with suggestions
        suggested_tags = [
            "Breakfast", "Lunch", "Dinner", "Dessert",
            "Vegetarian", "Vegan", "Gluten-Free", "Quick & Easy",
            "Healthy", "Comfort Food", "Party", "Budget-Friendly"
        ]
        tags = st.multiselect("Add Tags", suggested_tags)
        
        # Submit button
        submitted = st.form_submit_button("Share Recipe 🚀")
        
        if submitted:
            if title.strip() and content.strip():
                image_data = handle_image_upload(uploaded_file)
                
                # Create post document
                new_post = {
                    "title": title,
                    "content": content,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "tags": tags,
                    "image": image_data,
                    "user": st.session_state.get("username", "Anonymous"),
                    "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "likes": 0,
                    "comments_count": 0
                }
                
                # Insert into database
                posts_collection.insert_one(new_post)
                st.success("Recipe shared successfully! 🎉")
                
                # Show sharing options
                st.markdown("### Share your recipe!")
                share_col1, share_col2, share_col3 = st.columns(3)
                with share_col1:
                    st.button("📱 Share to Instagram")
                with share_col2:
                    st.button("📘 Share to Facebook")
                with share_col3:
                    st.button("🔗 Copy Link")
            else:
                st.error("Please add a title and description for your recipe.")

def display_feed():
    """Enhanced feed display"""
    # Filter options
    st.markdown("### 🍳 Recipe Feed")
    
    # Advanced filtering
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Most Popular", "Most Commented", "Trending"]
        )
    with col2:
        diet_filter = st.multiselect(
            "Dietary Preferences",
            ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"]
        )
    with col3:
        time_filter = st.selectbox(
            "Time",
            ["All Time", "Today", "This Week", "This Month"]
        )

    # Get posts with sorting and filtering
    query = {}
    if diet_filter:
        query["tags"] = {"$in": diet_filter}
        
    if time_filter != "All Time":
        if time_filter == "Today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "This Week":
            start_date = datetime.now() - timedelta(days=7)
        else:  # This Month
            start_date = datetime.now() - timedelta(days=30)
        query["time"] = {"$gte": start_date.strftime('%Y-%m-%d %H:%M:%S')}

    # Apply sorting
    sort_params = [("time", -1)]  # Default to most recent
    if sort_by == "Most Popular":
        sort_params = [("likes", -1)]
    elif sort_by == "Most Commented":
        sort_params = [("comments_count", -1)]
    elif sort_by == "Trending":
        # Complex sort for trending (combine recent + popularity)
        sort_params = [("likes", -1), ("time", -1)]

    posts = list(posts_collection.find(query).sort(sort_params))

    # Display posts
    for post in posts:
        with st.container():
            st.markdown(f"""
                <div class="post-card">
                    <div class="post-header">
                        <img src="https://api.dicebear.com/6.x/avataaars/svg?seed={post['user']}"
                             style="width: 50px; height: 50px; border-radius: 50%;">
                        <div class="user-info">
                            <div class="username">{post['user']}</div>
                            <div class="post-meta">{format_time(post['time'])}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Post title and content
            st.markdown(f"### {post['title']}")
            
            # Image display
            if post.get('image'):
                try:
                    image = Image.open(io.BytesIO(base64.b64decode(post['image'])))
                    st.image(image, use_container_width=True)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
            
            st.markdown(post['content'])
            
            # Tags
            if post.get('tags'):
                st.markdown(
                    '<div class="tag-container">' +
                    ''.join([f'<span class="tag">#{tag}</span>' for tag in post['tags']]) +
                    '</div>',
                    unsafe_allow_html=True
                )
            
            # Recipe details in expander
            with st.expander("View Full Recipe 📝"):
                if post.get('ingredients'):
                    st.markdown("#### 📋 Ingredients")
                    st.markdown(post['ingredients'])
                if post.get('instructions'):
                    st.markdown("#### 👩‍🍳 Instructions")
                    st.markdown(post['instructions'])
            
            # Interaction buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(f"❤️ {post.get('likes', 0)}", key=f"like_{post['_id']}"):
                    posts_collection.update_one(
                        {"_id": post["_id"]},
                        {"$inc": {"likes": 1}}
                    )
                    st.experimental_rerun()
                    
            with col2:
                if st.button(f"💬 {post.get('comments_count', 0)}", key=f"comment_{post['_id']}"):
                    st.session_state[f"show_comments_{post['_id']}"] = \
                        not st.session_state.get(f"show_comments_{post['_id']}", False)
                    
            with col3:
                st.button("🔗 Share", key=f"share_{post['_id']}")
                
            with col4:
                st.button("🔖 Save", key=f"save_{post['_id']}")
            
            # Comments section
            if st.session_state.get(f"show_comments_{post['_id']}", False):
                st.markdown('<div class="comment-section">', unsafe_allow_html=True)
                
                # Display existing comments
                comments = comments_collection.find({"post_id": post["_id"]}).sort("time", -1)
                for comment in comments:
                    st.markdown(f"""
                        <div class="comment-item">
                            <strong>{comment['user']}</strong> • {format_time(comment['time'])}
                            <br>{comment['content']}
                        </div>
                    """, unsafe_allow_html=True)
                
                # Add new comment
                with st.form(f"comment_form_{post['_id']}", clear_on_submit=True):
                    comment_text = st.text_area("Add a comment", key=f"comment_input_{post['_id']}")
                    if st.form_submit_button("Post Comment"):
                        if comment_text.strip():
                            comments_collection.insert_one({
                                "post_id": post["_id"],
                                "user": st.session_state.get("username", "Anonymous"),
                                "content": comment_text,
                                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            # Update comment count
                            posts_collection.update_one(
                                {"_id": post["_id"]},
                                {"$inc": {"comments_count": 1}}
                            )
                            st.experimental_rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Add spacing between posts
            st.markdown("<hr style='margin: 30px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

def render_sidebar_filters():
    """Enhanced sidebar filters"""
    st.sidebar.markdown("### 🔍 Explore")
    
    # Search
    st.sidebar.text_input("Search recipes...", placeholder="Type to search...")
    
    # Popular tags cloud
    st.sidebar.markdown("### 🏷️ Popular Tags")
    tags = ["#Breakfast", "#Dinner", "#Vegetarian", "#QuickMeal", "#Healthy", "#Dessert"]
    cols = st.sidebar.columns(2)
    for i, tag in enumerate(tags):
        with cols[i % 2]:
            st.button(tag, use_container_width=True)
    
    # Trending topics
    st.sidebar.markdown("### 🔥 Trending")
    trending = [
        "Summer Salads",
        "One-Pot Meals",
        "30-Min Recipes",
        "Healthy Snacks"
    ]
    for topic in trending:
        st.sidebar.button(f"📈 {topic}", use_container_width=True)
    
    # Activity feed
    st.sidebar.markdown("### 📱 Recent Activity")
    activities = [
        ("ChefJohn liked your post", "2m ago"),
        ("New comment on your recipe", "5m ago"),
        ("Your post is trending!", "15m ago")
    ]
    for activity, time in activities:
        st.sidebar.markdown(f"""
            <div style='
                background-color: grey;
                padding: 10px;
                border-radius: 8px;
                margin: 5px 0;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            '>
                <div>{activity}</div>
                <div style='color: #666; font-size: 12px;'>{time}</div>
            </div>
        """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'feed_page' not in st.session_state:
        st.session_state.feed_page = 1
    if 'posts_per_page' not in st.session_state:
        st.session_state.posts_per_page = 5
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'feed'

def render_floating_action_button():
    """Add floating action button for new post"""
    st.markdown("""
        <div style='
            position: fixed;
            right: 20px;
            bottom: 20px;
            background-color: #FF4B4B;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: pointer;
            z-index: 1000;
        '>
            ✏️
        </div>
    """, unsafe_allow_html=True)

def main():
    """Main function to render the social feed"""
    initialize_session_state()
    
    # Page title and description
    st.title("🍳 Recipe Social Feed")
    st.markdown("Share and discover amazing recipes from our community!")
    
    # Tabs for different views
    tabs = ["📱 Feed", "🔥 Trending", "🔖 Saved", "👤 My Posts"]
    selected_tab = st.radio("View", tabs, horizontal=True)
    
    # Render sidebar filters
    render_sidebar_filters()
    
    # Main content area
    if selected_tab == "📱 Feed":
        # Create new post section
        create_new_post()
        
        # Display feed
        display_feed()
        
        # Add floating action button
        render_floating_action_button()
        
    elif selected_tab == "🔥 Trending":
        st.markdown("### 🔥 Trending Recipes")
        # Add trending content here
        
    elif selected_tab == "🔖 Saved":
        st.markdown("### 🔖 Saved Recipes")
        # Add saved recipes content here
        
    else:  # My Posts
        st.markdown("### 👤 My Posts")
        # Add user's posts content here

if __name__ == "__main__":
    main()