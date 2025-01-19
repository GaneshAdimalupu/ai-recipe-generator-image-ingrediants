import streamlit as st
from datetime import datetime
from post.models.db_schema import comments_collection, posts_collection

def format_comment_time(timestamp):
    """Format comment timestamp for display"""
    now = datetime.now()
    comment_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    diff = now - comment_time
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "Just now"

def render_comment_section(post_id, username, view_type="feed"):
    """Render comments section for a post"""
    st.markdown('<div class="comment-section">', unsafe_allow_html=True)
    
    # Display existing comments
    comments = comments_collection.find({"post_id": post_id}).sort("time", -1)
    for comment in comments:
        st.markdown(f"""
            <div class="comment-item">
                <div class="comment-header">
                    <img src="https://api.dicebear.com/6.x/avataaars/svg?seed={comment['user']}"
                         class="comment-avatar">
                    <div class="comment-info">
                        <span class="comment-username">{comment['user']}</span>
                        <span class="comment-time">{format_comment_time(comment['time'])}</span>
                    </div>
                </div>
                <div class="comment-content">
                    {comment['content']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Add new comment form with unique key
    with st.form(f"comment_form_{view_type}_{post_id}", clear_on_submit=True):
        comment_text = st.text_area(
            "Add a comment",
            key=f"comment_input_{view_type}_{post_id}",
            placeholder="Share your thoughts..."
        )
        
        if st.form_submit_button("Post Comment"):
            if comment_text.strip():
                # Insert new comment
                comments_collection.insert_one({
                    "post_id": post_id,
                    "user": username,
                    "content": comment_text,
                    "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Update comment count
                posts_collection.update_one(
                    {"_id": post_id},
                    {"$inc": {"comments_count": 1}}
                )
                
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)