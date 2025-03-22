
def get_styles():
    """Returns Instagram-like CSS styles for the social feed"""
    return """
    <style>
        /* Global Styles */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #262626;
            background-color: #fafafa;
        }
        
        /* Custom Sidebar */
        .sidebar .sidebar-content {
            background-image: linear-gradient(180deg, #FF4B4B20 0%, #FF9A9A10 100%);
            border-right: 1px solid #e6e6e6;
        }
        
        .sidebar-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #FF4B4B, #FF9A9A);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            padding: 10px 0;
        }
        
        /* Instagram-like Post Card */
        .post-card {
            background-color: white;
            border-radius: 8px;
            margin-bottom: 24px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.2s ease;
            overflow: hidden;
        }
        
        .post-card:hover {
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Post Header - Instagram Style */
        .post-header {
            display: flex;
            align-items: center;
            padding: 14px 16px;
            border-bottom: 1px solid #efefef;
        }
        
        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 12px;
            border: 1px solid #efefef;
        }
        
        .user-info {
            flex: 1;
        }
        
        .username {
            font-weight: 600;
            font-size: 14px;
            color: #262626;
            text-decoration: none;
        }
        
        .post-meta {
            font-size: 12px;
            color: #8e8e8e;
        }
        
        .post-options {
            font-size: 16px;
            color: #262626;
        }
        
        /* Post Image */
        .post-image-container {
            position: relative;
            width: 100%;
        }
        
        .post-image {
            width: 100%;
            display: block;
        }
        
        /* Post Actions Bar */
        .post-actions {
            display: flex;
            padding: 8px 16px;
            border-top: 1px solid #efefef;
        }
        
        .action-button {
            background: none;
            border: none;
            cursor: pointer;
            padding: 8px;
            margin-right: 16px;
            font-size: 22px;
            transition: color 0.2s;
        }
        
        .action-button:hover {
            color: #FF4B4B;
        }
        
        .like-button.active {
            color: #FF4B4B;
        }
        
        /* Post Content */
        .post-content {
            padding: 12px 16px;
        }
        
        .post-title {
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 16px;
        }
        
        .post-text {
            font-size: 14px;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        /* Tags */
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 8px 0;
        }
        
        .tag {
            background-color: #fafafa;
            color: #00376b;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            transition: background-color 0.2s;
        }
        
        .tag:hover {
            background-color: #efefef;
        }
        
        /* Comments Section */
        .comments-section {
            padding: 12px 16px;
            border-top: 1px solid #efefef;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .view-all-comments {
            color: #8e8e8e;
            font-size: 14px;
            margin-bottom: 8px;
            cursor: pointer;
        }
        
        .comment-item {
            margin-bottom: 8px;
            display: flex;
        }
        
        .comment-avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            margin-right: 12px;
        }
        
        .comment-content {
            flex: 1;
        }
        
        .comment-username {
            font-weight: 600;
            font-size: 13px;
            margin-right: 6px;
        }
        
        .comment-text {
            font-size: 13px;
        }
        
        .comment-time {
            font-size: 12px;
            color: #8e8e8e;
            margin-top: 4px;
        }
        
        .comment-like {
            font-size: 12px;
            color: #8e8e8e;
            margin-left: 8px;
            cursor: pointer;
        }
        
        /* Add Comment Form */
        .add-comment-form {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            border-top: 1px solid #efefef;
        }
        
        .comment-input {
            flex: 1;
            border: none;
            padding: 8px 0;
            font-size: 14px;
            outline: none;
        }
        
        .post-comment-button {
            background: none;
            color: #0095f6;
            border: none;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
        }
        
        .post-comment-button:disabled {
            color: #b3dbff;
            cursor: default;
        }
        
        /* Stories Bar */
        .stories-bar {
            display: flex;
            overflow-x: auto;
            padding: 16px;
            margin-bottom: 24px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        
        .story-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-right: 16px;
            cursor: pointer;
        }
        
        .story-avatar-container {
            width: 62px;
            height: 62px;
            border-radius: 50%;
            background: linear-gradient(45deg, #fd5949, #d6249f, #285AEB);
            padding: 2px;
            margin-bottom: 6px;
        }
        
        .story-avatar {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid white;
            object-fit: cover;
        }
        
        .story-username {
            font-size: 12px;
            color: #262626;
            max-width: 64px;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
            text-align: center;
        }
        
        /* Instagram-like Explore Grid */
        .explore-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 4px;
            margin-bottom: 24px;
        }
        
        .explore-item {
            position: relative;
            aspect-ratio: 1;
            overflow: hidden;
            cursor: pointer;
        }
        
        .explore-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }
        
        .explore-item:hover .explore-image {
            transform: scale(1.05);
        }
        
        .explore-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.3);
            opacity: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: opacity 0.3s;
        }
        
        .explore-item:hover .explore-overlay {
            opacity: 1;
        }
        
        .explore-stats {
            display: flex;
            color: white;
            font-weight: 600;
        }
        
        .explore-stat {
            display: flex;
            align-items: center;
            margin: 0 8px;
        }
        
        .explore-stat-icon {
            margin-right: 4px;
        }
        
        /* Enhanced Sidebar Navigation */
        .sidebar-nav {
            margin-top: 20px;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            transition: background-color 0.2s;
            cursor: pointer;
        }
        
        .nav-item:hover {
            background-color: rgba(255, 75, 75, 0.1);
        }
        
        .nav-item.active {
            background-color: rgba(255, 75, 75, 0.2);
            font-weight: 600;
        }
        
        .nav-icon {
            font-size: 20px;
            margin-right: 12px;
            width: 24px;
            text-align: center;
        }
        
        .nav-text {
            font-size: 14px;
        }
        
        /* Profile Section in Sidebar */
        .sidebar-profile {
            display: flex;
            align-items: center;
            padding: 16px;
            border-top: 1px solid #efefef;
            margin-top: 24px;
        }
        
        .sidebar-avatar {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            margin-right: 12px;
        }
        
        .sidebar-user-info {
            flex: 1;
        }
        
        .sidebar-username {
            font-weight: 600;
            font-size: 14px;
        }
        
        .sidebar-name {
            font-size: 12px;
            color: #8e8e8e;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .explore-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #121212;
                color: #fafafa;
            }
            
            .post-card, .stories-bar {
                background-color: #1e1e1e;
                border: 1px solid #2e2e2e;
            }
            
            .post-header, .post-actions, .comments-section, .add-comment-form {
                border-color: #2e2e2e;
            }
            
            .username, .post-title {
                color: #fafafa;
            }
            
            .post-meta, .comment-time, .view-all-comments {
                color: #a8a8a8;
            }
            
            .tag {
                background-color: #2e2e2e;
                color: #b3dbff;
            }
            
            .comment-input {
                background-color: transparent;
                color: #fafafa;
            }
            
            .sidebar .sidebar-content {
                background-image: linear-gradient(180deg, #1e1e1e 0%, #2e2e2e 100%);
                border-right: 1px solid #2e2e2e;
            }
        }
    </style>
    """

def apply_post_styles():
    """Apply the Instagram-like styles to the current Streamlit page"""
    import streamlit as st
    st.markdown(get_styles(), unsafe_allow_html=True)