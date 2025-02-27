import streamlit as st
from asset.css.home import load_css

def render_header():
    st.markdown("""
        <div class="header-container">
            <div class="header-content">
                <div class="nav-container">
                    <div class="logo">
                        <h1 style="color: #6b3c62; font-size: 1.8rem; font-weight: 700;">
                            🍳 Be My Chef
                        </h1>
                    </div>
                    <div class="nav-links">
                        <a href="#" class="nav-link">HOME</a>
                        <a href="#" class="nav-link">ABOUT</a>
                        <a href="#" class="nav-link">RECIPES</a>
                        <a href="#" class="nav-link">START HERE</a>
                    </div>
                </div>
                <div class="tagline">
                    SIMPLE RECIPES MADE FOR <em>real, actual, everyday life</em>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_blog_posts():
    """Render the blog posts section"""
    st.markdown('<div class="blog-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="blog-title">THE LATEST & GREATEST</h2>', unsafe_allow_html=True)
    
    posts = [
        {
            "date": "FEBRUARY 2, 2023",
            "title": "The Best Foods At Disney World",
            "excerpt": "There's actually really very delicious food at Disney World! As a food lover, these are my favorite foods from all the parks.",
            "image": "https://images.unsplash.com/photo-1583112244390-e1496e8f8ba9"
        },
        {
            "date": "JANUARY 24, 2023",
            "title": "Crockpot Chicken Bowls with Yellow Rice and Cilantro Pesto",
            "excerpt": "Saucy shredded chicken, yellow rice, pickled onions, greens, and cilantro pesto on top. It's a flavor and color delight!",
            "image": "https://images.unsplash.com/photo-1585937421612-70a008356fbe"
        }
    ]
    
    for post in posts:
        st.markdown(f"""
            <div class="blog-post">
                <img src="{post['image']}" class="blog-image" alt="{post['title']}">
                <div class="blog-content">
                    <div class="blog-date">{post['date']}</div>
                    <h3 class="blog-heading">{post['title']}</h3>
                    <p class="blog-excerpt">{post['excerpt']}</p>
                    <a href="#" class="continue-reading">CONTINUE READING</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="view-more">VIEW MORE RECENT POSTS</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_featured_section():
    """Render the featured section with food publication logos"""
    st.markdown("""
        <div class="featured-section">
            <h3 class="featured-title">AS FEATURED IN</h3>
            <div class="featured-logos">
                <div class="featured-logo">
                    <div class="featured-icon">🏆</div>
                    <div class="featured-name">Food & Wine</div>
                </div>
                <div class="featured-logo">
                    <div class="featured-icon">🌟</div>
                    <div class="featured-name">Epicurious</div>
                </div>
                <div class="featured-logo">
                    <div class="featured-icon">👨‍🍳</div>
                    <div class="featured-name">Bon Appétit</div>
                </div>
                <div class="featured-logo">
                    <div class="featured-icon">🍽️</div>
                    <div class="featured-name">Saveur</div>
                </div>
                <div class="featured-logo">
                    <div class="featured-icon">🌎</div>
                    <div class="featured-name">Food Network</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(layout="wide", page_title="Recipe Website")
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Render enhanced header
    render_header()
    load_css()
    
    # Featured Recipes Grid
    recipes = [
        {"image": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db", "category": "WINTER"},
        {"image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8", "category": "SOUPS"},
        {"image": "https://images.unsplash.com/photo-1625398407796-82650a8c135f", "category": "VEGETARIAN"},
        {"image": "https://images.unsplash.com/photo-1601050690597-df0568f70950", "category": "DINNER"}
    ]
    
    cols = st.columns(4)
    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class="recipe-card">
                    <img src="{recipes[idx]['image']}" class="recipe-image">
                    <div class="category-tag">{recipes[idx]['category']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Category Icons
    categories = [
        {"name": "QUICK AND EASY", "icon": "⚡"},
        {"name": "DINNER", "icon": "🍽️"},
        {"name": "VEGETARIAN", "icon": "🥗"},
        {"name": "HEALTHY", "icon": "🥑"},
        {"name": "INSTANT POT", "icon": "🥘"},
        {"name": "VEGAN", "icon": "🌱"},
        {"name": "MEAL PREP", "icon": "🥡"},
        {"name": "SOUPS", "icon": "🥣"},
        {"name": "SALADS", "icon": "🥬"}
    ]
    
    st.markdown('<div class="category-icons">', unsafe_allow_html=True)
    cols = st.columns(len(categories))
    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class="category-item">
                    <div class="category-circle">{categories[idx]['icon']}</div>
                    <div class="category-name">{categories[idx]['name']}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search Bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("", placeholder="Search our recipes")
    with col2:
        st.button("VIEW ALL RECIPES →", use_container_width=True)
    
    # # Latest Posts & Recipe Collections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### THE LATEST & GREATEST")
        st.markdown("""
            <div class="post-card">
                <img src="https://images.unsplash.com/photo-1588166524941-3bf61a9c41db" class="post-image">
                <div>
                    <small>FEBRUARY 2, 2025</small>
                    <h3>The Best Foods At Disney World</h3>
                    <p>There's actually really very delicious food at Disney World! As a food lover, these are my favorite foods from all the parks.</p>
                    <a href="#">CONTINUE READING</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### RECIPE COLLECTIONS")
        st.markdown("""
            <div class="recipe-collections">
                <a href="#">Instant Pot Recipes (27)</a><br>
                <a href="#">Vegan Recipes (158)</a><br>
                <a href="#">Meal Prep Recipes (54)</a><br>
                <a href="#">Quick and Easy Recipes (424)</a>
            </div>
        """, unsafe_allow_html=True)
 
    
    # Featured Section
    render_featured_section()
    
    # Footer
    st.markdown("""
        <div class="footer">
            <div class="footer-grid">
                <div>
                    <h4>FOLLOW US</h4>
                    <div class="social-links">
                        <a href="#" class="social-icon">📷</a>
                        <a href="#" class="social-icon">📌</a>
                        <a href="#" class="social-icon">👥</a>
                        <a href="#" class="social-icon">🐦</a>
                    </div>
                </div>
                <div>
                    <h4>SIGN UP FOR EMAIL UPDATES</h4>
                    <div class="email-form">
                        <input type="email" placeholder="Email" class="email-input">
                        <button class="submit-button">GO</button>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()