import streamlit as st

# Initialize login check
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")

from datetime import datetime, timedelta
from mongodb.db import get_database
from pages.widgets import __login__
import base64
from PIL import Image
import io
from math import log
import timeago

# Initialize MongoDB connections
db = get_database()
posts_collection = db["posts"]
comments_collection = db["comments"]
likes_collection = db["likes"]
votes_collection = db["votes"]
awards_collection = db["awards"]
saved_posts_collection = db["saved_posts"]

# Initialize session states
if 'show_comments' not in st.session_state:
    st.session_state.show_comments = None
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = "hot"
if 'time_filter' not in st.session_state:
    st.session_state.time_filter = "all"

def calculate_score(upvotes, downvotes):
    """Calculate Reddit-style score for sorting"""
    return upvotes - downvotes

def get_vote_status(post_id, username):
    """Get user's vote status for a post"""
    if not username:
        return 0
    vote = votes_collection.find_one({
        "post_id": post_id,
        "user": username
    })
    return vote["vote_type"] if vote else 0  # 1 for upvote, -1 for downvote, 0 for no vote

def handle_vote(post_id, username, vote_type):
    """Handle post voting"""
    if not username:
        return False
        
    existing_vote = votes_collection.find_one({
        "post_id": post_id,
        "user": username
    })
    
    if existing_vote:
        if existing_vote["vote_type"] == vote_type:
            # Remove vote if clicking same button
            votes_collection.delete_one({"_id": existing_vote["_id"]})
            update_vote_count(post_id)
            return False
        else:
            # Change vote
            votes_collection.update_one(
                {"_id": existing_vote["_id"]},
                {"$set": {"vote_type": vote_type}}
            )
    else:
        # New vote
        votes_collection.insert_one({
            "post_id": post_id,
            "user": username,
            "vote_type": vote_type,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    update_vote_count(post_id)
    return True

def update_vote_count(post_id):
    """Update post's vote counts"""
    upvotes = votes_collection.count_documents({"post_id": post_id, "vote_type": 1})
    downvotes = votes_collection.count_documents({"post_id": post_id, "vote_type": -1})
    score = calculate_score(upvotes, downvotes)
    
    posts_collection.update_one(
        {"_id": post_id},
        {
            "$set": {
                "upvotes": upvotes,
                "downvotes": downvotes,
                "score": score
            }
        }
    )

def is_post_saved(post_id, username):
    """Check if post is saved by user"""
    return saved_posts_collection.find_one({
        "post_id": post_id,
        "user": username
    }) is not None

def toggle_save_post(post_id, username):
    """Toggle save status of a post"""
    if is_post_saved(post_id, username):
        saved_posts_collection.delete_one({
            "post_id": post_id,
            "user": username
        })
        return False
    else:
        saved_posts_collection.insert_one({
            "post_id": post_id,
            "user": username,
            "saved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return True

def get_hot_score(upvotes, downvotes, created_time):
    """Calculate Reddit-style hot score"""
    score = upvotes - downvotes
    order = log(max(abs(score), 1), 10)
    sign = 1 if score > 0 else -1 if score < 0 else 0
    seconds = created_time.timestamp() - 1134028003
    return round(sign * order + seconds / 45000, 7)

def format_time(time_value):
    """Format time value consistently"""
    if isinstance(time_value, str):
        try:
            return datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.now()
    return time_value

def save_image(uploaded_file):
    """Save uploaded image as base64"""
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode()
    return None

def load_image(base64_string):
    """Load image from base64"""
    if base64_string:
        image_bytes = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(image_bytes))
    return None

def render_single_post(post, current_user):
    """Render a single Reddit-style post"""
    vote_status = get_vote_status(post["_id"], current_user)
    is_saved = is_post_saved(post["_id"], current_user) if current_user else False
    display_time = format_time(post['time'])
    
    # Post container
    st.markdown('<div class="reddit-post-card">', unsafe_allow_html=True)
    
    # Vote column and content column
    col1, col2 = st.columns([1, 11])
    
    with col1:
        # Vote buttons and count
        upvote = st.button("⬆️", key=f"up_{post['_id']}", 
                          help="Upvote", use_container_width=True,
                          disabled=not current_user)
        
        st.markdown(f"""
            <div class="vote-count {
                'upvoted' if vote_status == 1 else 
                'downvoted' if vote_status == -1 else ''
            }">
                {post.get('score', 0)}
            </div>
        """, unsafe_allow_html=True)
        
        downvote = st.button("⬇️", key=f"down_{post['_id']}", 
                            help="Downvote", use_container_width=True,
                            disabled=not current_user)
        
        if upvote or downvote:
            if not current_user:
                st.warning("Please log in to vote")
            else:
                handle_vote(post["_id"], current_user, 1 if upvote else -1)
                st.rerun()
    
    with col2:
        # Post header
        st.markdown(f"""
            <div class="post-header">
                <span class="post-subreddit">r/RecipeShare</span>
                <span>Posted by u/{post['user']}</span>
                <span>•</span>
                <span>{timeago.format(display_time, datetime.now())}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Post title and content
        st.markdown(f"### {post['title']}")
        
        # Image
        if post.get('image'):
            image = load_image(post['image'])
            if image:
                st.image(image, use_container_width=True)
        
        # Content
        st.markdown(post['content'])
        
        # Recipe details in expandable section
        if post.get('ingredients') or post.get('instructions'):
            with st.expander("📝 View Full Recipe"):
                if post.get('ingredients'):
                    st.markdown("#### Ingredients")
                    st.write(post['ingredients'])
                if post.get('instructions'):
                    st.markdown("#### Instructions")
                    st.write(post['instructions'])
        
        # Tags
        if post.get('tags'):
            st.markdown(' '.join([f'`#{tag}`' for tag in post['tags']]))
        
        # Action buttons
        col1, col2, col3, col4 = st.columns([2, 2, 2, 6])
        
        with col1:
            if st.button(f"💬 {post.get('comments_count', 0)} Comments", 
                        key=f"comment_{post['_id']}", use_container_width=True):
                st.session_state['show_comments'] = post['_id']
        
        with col2:
            saved_icon = "📥" if is_saved else "💾"
            if st.button(f"{saved_icon} Save", key=f"save_{post['_id']}", 
                        use_container_width=True):
                if not current_user:
                    st.warning("Please log in to save posts")
                else:
                    toggle_save_post(post["_id"], current_user)
                    st.rerun()
        
        with col3:
            if st.button("🔗 Share", key=f"share_{post['_id']}", 
                        use_container_width=True):
                st.toast("Link copied to clipboard!")
        
        # Comments section
        if st.session_state.get('show_comments') == post['_id']:
            st.markdown('<div class="comments-section">', unsafe_allow_html=True)
            
            # Comment form
            if current_user:
                with st.form(f"comment_form_{post['_id']}", clear_on_submit=True):
                    comment = st.text_area("Add a comment")
                    if st.form_submit_button("Post Comment"):
                        if comment.strip():
                            comments_collection.insert_one({
                                "post_id": post["_id"],
                                "user": current_user,
                                "content": comment,
                                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            posts_collection.update_one(
                                {"_id": post["_id"]},
                                {"$inc": {"comments_count": 1}}
                            )
                            st.rerun()
            else:
                st.warning("Please log in to comment")
            
            # Display comments
            comments = comments_collection.find({"post_id": post["_id"]}).sort("time", -1)
            for comment in comments:
                comment_time = format_time(comment['time'])
                st.markdown(f"""
                    <div class="comment">
                        <div class="comment-header">
                            <strong>{comment['user']}</strong>
                            <span>•</span>
                            <span>{timeago.format(comment_time, datetime.now())}</span>
                        </div>
                        <div class="comment-content">
                            {comment['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main(login_ui):
    """Main function to render the Reddit-style feed"""
    current_user = login_ui.get_username()

    # Page title and description
    st.title("🍳 Recipe Community")
    st.markdown("Share and discover amazing recipes from fellow chefs!")

    # Create post section
    with st.expander("📝 Create New Post", expanded=False):
        if not current_user:
            st.warning("Please log in to create a post")
        else:
            with st.form("post_form", clear_on_submit=True):
                post_title = st.text_input("Recipe Title", placeholder="What's cooking?")
                post_content = st.text_area("Recipe Description", placeholder="Tell us about your recipe!", height=100)
                uploaded_file = st.file_uploader("Add Food Photo", type=['jpg', 'jpeg', 'png'])
                
                col1, col2 = st.columns(2)
                with col1:
                    ingredients = st.text_area("Ingredients", placeholder="List your ingredients", height=150)
                with col2:
                    instructions = st.text_area("Instructions", placeholder="Share your cooking steps", height=150)
                
                tags = st.multiselect(
                    "Add Tags",
                    ["Vegetarian", "Vegan", "Gluten-Free", "Quick & Easy", "Dessert", 
                     "Main Course", "Breakfast", "Lunch", "Dinner", "Snack"]
                )
                
                submitted = st.form_submit_button("Share Recipe 🚀")
                
                if submitted:
                    if post_title.strip() and post_content.strip():
                        image_data = save_image(uploaded_file)
                        
                        new_post = {
                            "title": post_title,
                            "content": post_content,
                            "ingredients": ingredients,
                            "instructions": instructions,
                            "tags": tags,
                            "image": image_data,
                            "user": current_user,
                            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "score": 0,
                            "upvotes": 0,
                            "downvotes": 0,
                            "comments_count": 0
                        }
                        
                        posts_collection.insert_one(new_post)
                        st.success("Recipe shared successfully! 🎉")
                        st.rerun()
                    else:
                        st.error("Please add a title and description for your recipe.")

    # Sorting and filtering options
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_options = {
            "hot": "🔥 Hot",
            "new": "✨ New",
            "top": "⭐ Top",
            "controversial": "💭 Controversial"
        }
        selected_sort = st.select_slider(
            "Sort by",
            options=list(sort_options.keys()),
            format_func=lambda x: sort_options[x],
            value=st.session_state.sort_by
        )
        st.session_state.sort_by = selected_sort

    with col2:
        time_filters = {
            "hour": "Past Hour",
            "day": "Past 24H",
            "week": "Past Week",
            "month": "Past Month",
            "year": "Past Year",
            "all": "All Time"
        }
        selected_time = st.selectbox(
            "Time period",
            options=list(time_filters.keys()),
            format_func=lambda x: time_filters[x],
            index=list(time_filters.keys()).index(st.session_state.time_filter)
        )
        st.session_state.time_filter = selected_time

    # Get and sort posts
    all_posts = list(posts_collection.find())
    
    # Filter posts by time
    now = datetime.now()
    if selected_time != "all":
        time_deltas = {
            "hour": timedelta(hours=1),
            "day": timedelta(days=1),
            "week": timedelta(weeks=1),
            "month": timedelta(days=30),
            "year": timedelta(days=365)
        }
        cutoff_time = now - time_deltas[selected_time]
        all_posts = [post for post in all_posts if format_time(post['time']) > cutoff_time]
    
    # Sort posts based on selected sorting method
    if selected_sort == "hot":
        all_posts.sort(key=lambda x: get_hot_score(
            x.get('upvotes', 0), 
            x.get('downvotes', 0), 
            format_time(x['time'])
        ), reverse=True)
    elif selected_sort == "new":
        all_posts.sort(key=lambda x: format_time(x['time']), reverse=True)
    elif selected_sort == "top":
        all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
    elif selected_sort == "controversial":
        all_posts.sort(key=lambda x: abs(x.get('upvotes', 0) - x.get('downvotes', 0)), reverse=True)

    # Display posts
    if all_posts:
        for post in all_posts:
            render_single_post(post, current_user)
    else:
        st.info("No recipes yet! Be the first to share your culinary creation! 👨‍🍳")

if __name__ == "__main__":
    # Initialize login UI
    login_ui = __login__(
        auth_token="your_courier_auth_token",
        company_name="Be My Chef AI",
        width=200,
        height=200,
    )
    
    # Show navigation
    login_ui.nav_sidebar()
    
    # Apply Reddit-style CSS
    st.markdown("""
        <style>
        /* Import the Reddit-style CSS defined above */
                .reddit-post-card {
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 16px;
    display: flex;
}

.vote-column {
    background-color: #f8f9fa;
    padding: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 40px;
    border-radius: 4px 0 0 4px;
}

.vote-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
}

.vote-button:hover {
    background-color: #e9ecef;
    border-radius: 4px;
}

.vote-count {
    font-weight: bold;
    margin: 4px 0;
}

.post-content-column {
    flex-grow: 1;
    padding: 12px;
}

.post-header {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: #787c7e;
    margin-bottom: 8px;
}

.post-subreddit {
    color: #1a1a1b;
    font-weight: 700;
    margin-right: 8px;
}

.post-title {
    font-size: 18px;
    font-weight: 500;
    color: #1a1a1b;
    margin-bottom: 8px;
}

.post-actions {
    display: flex;
    gap: 16px;
    color: #787c7e;
    font-weight: 700;
    font-size: 12px;
    margin-top: 8px;
}

.action-button {
    display: flex;
    align-items: center;
    gap: 4px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
}

.action-button:hover {
    background-color: #f6f7f8;
}

.upvoted {
    color: #ff4500;
}

.downvoted {
    color: #7193ff;
}

.saved {
    color: #46d160;
}

.comments-section {
    margin-top: 16px;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 4px;
}

.comment {
    padding: 12px;
    margin-bottom: 12px;
    background-color: white;
    border-radius: 4px;
    border-left: 4px solid #ccc;
}

.comment-header {
    font-size: 12px;
    color: #787c7e;
    margin-bottom: 8px;
}

.comment-content {
    font-size: 14px;
    line-height: 1.5;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .reddit-post-card {
        background-color: #1a1a1b;
        border-color: #343536;
    }
    
    .vote-column {
        background-color: #272729;
    }
    
    .post-title {
        color: #d7dadc;
    }
    
    .post-actions {
        color: #818384;
    }
    
    .action-button:hover {
        background-color: #272729;
    }
    
    .comments-section {
        background-color: #272729;
    }
    
    .comment {
        background-color: #1a1a1b;
        border-left-color: #343536;
    }
}
        </style>
    """, unsafe_allow_html=True)
    
    # Render content
    main(login_ui)