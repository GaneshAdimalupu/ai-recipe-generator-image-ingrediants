import streamlit as st

def create_page_anchor():
    """Create an anchor point at the top of the page"""
    st.markdown("<div id='page-top'></div>", unsafe_allow_html=True)

def render_pagination(page_number, total_pages):
    """Render pagination controls with scroll to top functionality"""
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if page_number > 1:
            if st.button("← Previous", key="prev_btn"):
                st.session_state.page_number = page_number - 1
                st.session_state.should_scroll = True
                st.rerun()

    with col3:
        if page_number < total_pages:
            if st.button("Next →", key="next_btn"):
                st.session_state.page_number = page_number + 1
                st.session_state.should_scroll = True
                st.rerun()

    # Add back to top button
    st.markdown("""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
            <a href="#page-top" target="_self" style="
                background-color: var(--primary-color);
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                text-decoration: none;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 14px;
            ">
                <span>⬆️</span>
                <span>Back to Top</span>
            </a>
        </div>
    """, unsafe_allow_html=True)

    # Add scroll to top behavior
    if st.session_state.should_scroll:
        st.markdown("""
            <script>
                setTimeout(function() { window.scrollTo({ top: 0, behavior: 'smooth' }); }, 100);
            </script>
        """, unsafe_allow_html=True)
        st.session_state.should_scroll = False