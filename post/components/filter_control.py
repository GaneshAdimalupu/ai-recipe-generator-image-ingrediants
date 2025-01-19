import streamlit as st
from datetime import datetime, timedelta

def render_filter_controls():
    """Render filter and sort controls for the feed"""
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
    
    # Build query based on filters
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
    
    # Determine sort parameters
    if sort_by == "Most Popular":
        sort_params = [("likes", -1)]
    elif sort_by == "Most Commented":
        sort_params = [("comments_count", -1)]
    elif sort_by == "Trending":
        # Combine recent + popularity for trending
        sort_params = [("likes", -1), ("time", -1)]
    else:  # Most Recent
        sort_params = [("time", -1)]
    
    return query, sort_params

def render_sidebar_filters():
    """Render sidebar filters and navigation"""
    st.sidebar.markdown("### 🔍 Explore")
    
    # Search box
    search_query = st.sidebar.text_input(
        "Search recipes...",
        placeholder="Search by title, ingredients, or tags"
    )
    
    # Popular tags
    st.sidebar.markdown("### 🏷️ Popular Tags")
    tag_cols = st.sidebar.columns(2)
    tags = ["#Breakfast", "#Dinner", "#Vegetarian", "#QuickMeal", "#Healthy", "#Dessert"]
    
    selected_tags = []
    for i, tag in enumerate(tags):
        with tag_cols[i % 2]:
            if st.button(tag, use_container_width=True):
                selected_tags.append(tag.replace("#", ""))
    
    # Trending topics
    st.sidebar.markdown("### 🔥 Trending Now")
    trending_topics = [
        "Summer Grilling",
        "Quick Weeknight Dinners",
        "Healthy Meal Prep",
        "Seasonal Recipes"
    ]
    
    selected_topic = None
    for topic in trending_topics:
        if st.sidebar.button(f"📈 {topic}", use_container_width=True):
            selected_topic = topic
    
    return {
        "search_query": search_query,
        "selected_tags": selected_tags,
        "selected_topic": selected_topic
    }