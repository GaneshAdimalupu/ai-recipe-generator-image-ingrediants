from mongodb.db import get_database

# Initialize database connection
db = get_database()

# Collections
posts_collection = db["posts"]
comments_collection = db["comments"]
likes_collection = db["likes"]
bookmarks_collection = db["bookmarks"]

# Create indexes
def setup_indexes():
    """Set up MongoDB indexes for better query performance"""
    # Posts indexes
    posts_collection.create_index([("time", -1)])
    posts_collection.create_index([("likes", -1)])
    posts_collection.create_index([("comments_count", -1)])
    posts_collection.create_index([("tags", 1)])
    posts_collection.create_index([("user", 1)])
    
    # Comments indexes
    comments_collection.create_index([("post_id", 1)])
    comments_collection.create_index([("time", -1)])
    comments_collection.create_index([("user", 1)])
    
    # Likes indexes (ensure unique likes per user per post)
    likes_collection.create_index(
        [("post_id", 1), ("user", 1)],
        unique=True
    )
    
    # Bookmarks indexes (ensure unique bookmarks per user per post)
    bookmarks_collection.create_index(
        [("post_id", 1), ("user", 1)],
        unique=True
    )

# Schema definitions (for reference)
post_schema = {
    "title": str,
    "content": str,
    "ingredients": str,
    "instructions": str,
    "tags": list,
    "image": str,  # base64 encoded
    "user": str,
    "time": str,  # ISO format
    "likes": int,
    "comments_count": int
}

comment_schema = {
    "post_id": "ObjectId",
    "user": str,
    "content": str,
    "time": str  # ISO format
}

like_schema = {
    "post_id": "ObjectId",
    "user": str,
    "time": str  # ISO format
}

bookmark_schema = {
    "post_id": "ObjectId",
    "user": str,
    "time": str,  # ISO format
    "notes": str,  # Optional user notes about the saved recipe
    "collections": list  # User-defined collection labels
}

# Database utilities
def get_trending_posts(limit=10):
    """Get trending posts based on recent likes and comments"""
    pipeline = [
        {
            "$addFields": {
                "score": {
                    "$add": [
                        "$likes",
                        {"$multiply": ["$comments_count", 2]}  # Comments weighted more
                    ]
                }
            }
        },
        {"$sort": {"score": -1, "time": -1}},
        {"$limit": limit}
    ]
    return list(posts_collection.aggregate(pipeline))

def get_user_feed(username, limit=20):
    """Get personalized feed for user based on their interactions"""
    # Get posts from users they've interacted with
    interacted_users = set()
    
    # Users whose posts they've liked
    likes = likes_collection.find({"user": username})
    for like in likes:
        post = posts_collection.find_one({"_id": like["post_id"]})
        if post:
            interacted_users.add(post["user"])
    
    # Users whose posts they've commented on
    comments = comments_collection.find({"user": username})
    for comment in comments:
        post = posts_collection.find_one({"_id": comment["post_id"]})
        if post:
            interacted_users.add(post["user"])
    
    # Combine posts from interacted users with trending posts
    feed_posts = list(posts_collection.find({
        "$or": [
            {"user": {"$in": list(interacted_users)}},
            {"likes": {"$gt": 10}}  # Include popular posts
        ]
    }).sort([
        ("time", -1)
    ]).limit(limit))
    
    return feed_posts

def search_posts(query, tags=None):
    """Search posts by text content and tags"""
    search_conditions = []
    
    if query:
        text_condition = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"ingredients": {"$regex": query, "$options": "i"}},
                {"instructions": {"$regex": query, "$options": "i"}}
            ]
        }
        search_conditions.append(text_condition)
    
    if tags:
        tag_condition = {"tags": {"$in": tags}}
        search_conditions.append(tag_condition)
    
    if search_conditions:
        query = {"$and": search_conditions} if len(search_conditions) > 1 else search_conditions[0]
    else:
        query = {}
    
    return list(posts_collection.find(query).sort("time", -1))

# Call this function when initializing your application
setup_indexes()