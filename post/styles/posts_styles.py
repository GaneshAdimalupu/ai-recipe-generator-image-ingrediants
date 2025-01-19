def get_styles():
    """Returns CSS styles for the social feed"""
    return """
    <style>
        /* Post Card */
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
        
        /* Post Header */
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
        
        /* Post Content */
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
        
        /* Tags */
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
            transition: background-color 0.2s ease;
        }
        
        .tag:hover {
            background-color: #e4e6e9;
        }
        
        /* Interaction Bar */
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
        
        /* Comments Section */
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
            transition: transform 0.2s ease;
        }
        
        .comment-item:hover {
            transform: translateX(5px);
        }
        
        .comment-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .comment-avatar {
            width: 32px;
            height: 32px;
            border-radius: 16px;
            margin-right: 10px;
        }
        
        .comment-info {
            display: flex;
            flex-direction: column;
        }
        
        .comment-username {
            font-weight: 600;
            font-size: 14px;
            color: #1a1a1a;
        }
        
        .comment-time {
            font-size: 12px;
            color: #666;
        }
        
        .comment-content {
            font-size: 14px;
            color: #333;
            margin-left: 42px;
        }
        
        /* Form Elements */
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s ease;
        }
        
        input[type="text"]:focus, textarea:focus {
            border-color: #ff4b4b;
            outline: none;
        }
        
        /* Buttons */
        .primary-button {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .primary-button:hover {
            background-color: #ff3333;
        }
        
        /* Dark Mode Support */
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
            
            input[type="text"], textarea {
                background-color: #333;
                color: #ffffff;
                border-color: #444;
            }
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .post-card {
            animation: slideIn 0.3s ease-out;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .post-card {
                margin: 10px 0;
                padding: 15px;
            }
            
            .interaction-bar {
                gap: 10px;
            }
            
            .tag-container {
                gap: 5px;
            }
            
            .comment-content {
                margin-left: 0;
            }
        }
    </style>
    """

def apply_styles():
    """Apply the styles to the current Streamlit page"""
    import streamlit as st
    st.markdown(get_styles(), unsafe_allow_html=True)