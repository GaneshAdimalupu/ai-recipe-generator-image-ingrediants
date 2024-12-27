import streamlit as st
from datetime import datetime
from mongodb.db import get_database
from pages.widgets import __login__

# Initialize login UI
login_ui = __login__(
    auth_token="your_courier_auth_token",
    company_name="Be My Chef AI",
    width=200,
    height=200,
)

# Check if user is logged in and show navigation
if not st.session_state.get("LOGGED_IN", False):
    st.switch_page("streamlit_app.py")
else:
    # Show navigation sidebar
    login_ui.nav_sidebar()



# Connect to MongoDB
db = get_database()
posts_collection = db["posts"]  # Collection for posts


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
