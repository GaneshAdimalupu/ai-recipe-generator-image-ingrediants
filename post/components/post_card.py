import streamlit as st
from datetime import datetime
import base64
from PIL import Image
import io
from post.models.db_schema import posts_collection, likes_collection
from .comment_section import render_comment_section

def format_time(timestamp):
    """Format post timestamp for display"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return "Just now"
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 7:
        return timestamp.strftime('%B %d, %Y')
    elif diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "Just now"

def render_post_card(post, username, view_type="feed"):
    """
    Render a single post card with all interactions
    
    Parameters:
    - post: The post data to render
    - username: Current user's username
    - view_type: Type of view (feed, trending, saved, my_posts) to ensure unique keys
    """
    with st.container():
        # Post header
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
        
        # Post title
        st.markdown(f"### {post['title']}")
        
        # Post image
        if post.get('image'):
            try:
                image = Image.open(io.BytesIO(base64.b64decode(post['image'])))
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {str(e)}")
        
        # Post content
        st.markdown(post['content'])
        
        # Tags
        if post.get('tags'):
            st.markdown(
                '<div class="tag-container">' +
                ''.join([f'<span class="tag">#{tag}</span>' for tag in post['tags']]) +
                '</div>',
                unsafe_allow_html=True
            )
        
        # Recipe details expander
        with st.expander("View Full Recipe 📝"):
            if post.get('ingredients'):
                st.markdown("#### 📋 Ingredients")
                st.markdown(post['ingredients'])
            if post.get('instructions'):
                st.markdown("#### 👩‍🍳 Instructions")
                st.markdown(post['instructions'])
        
        # Generate unique keys for each interaction button
        post_id_str = str(post['_id'])
        like_key = f"like_{view_type}_{post_id_str}"
        comment_key = f"comment_{view_type}_{post_id_str}"
        share_key = f"share_{view_type}_{post_id_str}"
        save_key = f"save_{view_type}_{post_id_str}"
        
        # Interaction buttons
        col1, col2, col3, col4 = st.columns(4)
        
        # Like button
        with col1:
            has_liked = likes_collection.find_one({
                "post_id": post["_id"],
                "user": username
            }) is not None
            
            like_icon = "❤️" if has_liked else "🤍"
            if st.button(f"{like_icon} {post.get('likes', 0)}", key=like_key):
                if not has_liked:
                    # Add like
                    likes_collection.insert_one({
                        "post_id": post["_id"],
                        "user": username,
                        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    # Update post likes count
                    posts_collection.update_one(
                        {"_id": post["_id"]},
                        {"$inc": {"likes": 1}}
                    )
                    st.rerun()
        
        # Comment button
        with col2:
            if st.button(f"💬 {post.get('comments_count', 0)}", key=comment_key):
                st.session_state[f"show_comments_{view_type}_{post['_id']}"] = \
                    not st.session_state.get(f"show_comments_{view_type}_{post['_id']}", False)
        
        # Share button
        with col3:
            if st.button("🔗 Share", key=share_key):
                st.info("Share functionality coming soon!")
        
        # Save button
        with col4:
            if st.button("🔖 Save", key=save_key):
                st.info("Save functionality coming soon!")
        
        # Comments section
        if st.session_state.get(f"show_comments_{view_type}_{post['_id']}", False):
            render_comment_section(post["_id"], username, view_type)
        
        # Add spacing between posts
        st.markdown(
            "<hr style='margin: 30px 0; border: none; border-top: 1px solid #eee;'>",
            unsafe_allow_html=True
        )