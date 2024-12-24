import streamlit as st
from datetime import datetime
from mongodb.db import get_database

# Connect to MongoDB
db = get_database()
posts_collection = db["posts"]  # Collection for posts

from navigation import make_sidebar
make_sidebar()

# Ensure only logged-in users can access this page
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

# Title of the page
st.title("Posts Page 📝")


# Form to submit a new post
with st.form("post_form"):
    post_content = st.text_area("Write your post:")
    submitted = st.form_submit_button("Submit Post")

    if submitted:
        if post_content.strip():
            new_post = {
                "content": post_content,
                "user": "test_user",  # Replace with the actual username
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
            }
            posts_collection.insert_one(new_post)  # Insert into MongoDB
            st.success("Post submitted!")
        else:
            st.error("Post content cannot be empty.")

# Display existing posts
st.write("## 📰 Recent Posts")
all_posts = list(
    posts_collection.find().sort("time", -1)
)  # Get posts from MongoDB, sorted by time
if all_posts:
    for post in all_posts:
        st.write(f"### {post['user']} said:")
        st.write(post["content"])
        st.write(f"🕒 Posted on: {post['time']}")
        st.write("---")
else:
    st.info("No posts yet. Be the first to post!")
