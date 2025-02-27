def load_css():

    return"""
        <style>
        /* Global Reset */
        * {margin: 0; padding: 0; box-sizing: border-box;}
        
        /* Navigation */
        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid #eee;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-link {
            text-transform: uppercase;
            color: #333;
            text-decoration: none;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }
        
        /* Main Header */
        .tagline {
            text-align: center;
            padding: 1rem;
            font-style: italic;
            color: #666;
            border-bottom: 1px solid #eee;
        }
        
        /* Recipe Grid */
        .recipe-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .recipe-card {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s ease;
        }
        
        .recipe-card:hover {
            transform: translateY(-5px);
        }
        
        .recipe-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
        }
        
        .category-tag {
            position: absolute;
            bottom: 1rem;
            left: 1rem;
            background: #ffd43b;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        /* Category Icons */
        .category-icons {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .category-item {
            text-align: center;
        }
        
        .category-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-bottom: 0.5rem;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
        }
        
        .category-name {
            font-size: 0.7rem;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        /* Search Bar */
        .search-container {
            display: flex;
            gap: 1rem;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        /* Latest Posts */
        .latest-posts {
            margin: 3rem 0;
        }
        
        .post-card {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .post-image {
            width: 200px;
            height: 150px;
            object-fit: cover;
            border-radius: 8px;
        }
        
        /* Recipe Collections */
        .recipe-collections {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 8px;
        }
        
        /* Footer */
        .footer {
            background: #6b3c62;
            color: white;
            padding: 3rem 2rem;
            margin-top: 3rem;
        }
        
        .footer-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2rem;
        }
        
        .social-links {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .social-icon {
            width: 30px;
            height: 30px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Email Signup */
        .email-signup {
            background: #6b3c62;
            padding: 2rem;
            border-radius: 8px;
            text-align: center;
            color: white;
        }
        
        .email-form {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .email-input {
            padding: 0.5rem;
            border: none;
            border-radius: 4px;
            flex: 1;
        }
        
        .submit-button {
            background: #ffd43b;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
        }
        
        /* Blog Posts Section */
        .latest-greatest {
            margin: 3rem 0;
            color: #333;
        }
        
        .section-title {
            color: #6B3C62;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            font-weight: 600;
        }
        
        .blog-post {
            margin-bottom: 2.5rem;
            display: flex;
            gap: 1.5rem;
        }
        
        .post-image {
            width: 200px;
            height: 150px;
            object-fit: cover;
            border-radius: 8px;
        }
        
        .post-content {
            flex: 1;
        }
        
        .post-date {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }
        
        .post-title {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        .post-excerpt {
            color: #666;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        
        .continue-reading {
            color: #F4B942;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        /* Recipe Collections */
        .recipe-collections {
            background: #F3F5F7;
            padding: 2rem;
            border-radius: 8px;
        }
        
        .collections-title {
            color: #6B3C62;
            font-size: 1rem;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }
        
        .collection-link {
            display: flex;
            align-items: center;
            padding: 0.8rem 0;
            color: #333;
            text-decoration: none;
            border-bottom: 1px solid #E9ECEF;
        }
        
        .collection-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            margin-right: 1rem;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .collection-count {
            color: #666;
            font-size: 0.9rem;
            margin-left: auto;
        }
        
        /* View More Button */
        .view-more-btn {
            display: block;
            width: 100%;
            padding: 1rem;
            background: #6B3C62;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 4px;
            margin: 2rem 0;
            font-weight: 600;
        }
        
        /* Featured Section */
        .featured-section {
            text-align: center;
            margin: 3rem 0;
        }
        
        .featured-title {
            color: #F4B942;
            font-size: 0.8rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 2rem;
        }
        
        .featured-logos {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 3rem;
            opacity: 0.6;
        }
        
        .featured-logo {
            height: 30px;
        }
# Add this to the existing CSS in load_css()
        /* Featured Section Enhancements */
        .featured-section {
            text-align: center;
            margin: 4rem 0;
            padding: 2rem;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .featured-title {
            color: #6B3C62;
            font-size: 0.9rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 2rem;
            font-weight: 600;
        }
        
        .featured-logos {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 3rem;
            flex-wrap: wrap;
        }
        
        .featured-logo {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            transition: transform 0.2s ease;
        }
        
        .featured-logo:hover {
            transform: translateY(-5px);
        }
        
        .featured-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .featured-name {
            font-size: 0.8rem;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
        }

        </style>
    """
