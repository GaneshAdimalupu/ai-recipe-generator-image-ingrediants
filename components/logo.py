# components/logo.py
import streamlit as st
import base64
from pathlib import Path

def img_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def add_logo_with_rotating_text():
    img_path = "asset/images/chef.png"
    try:
        img_base64 = img_to_base64(img_path)
    except FileNotFoundError:
        st.warning("Logo image not found. Please check the path.")
        return
    
    logo_html = f'''
    <div style="display: flex; justify-content: center; width: 100%; margin-bottom: 2rem;">
        <div style="width: 400px; height: 400px; position: relative;">
            <style>
                @keyframes rotate {{
                    from {{ transform: rotate(0deg); }}
                    to {{ transform: rotate(360deg); }}
                }}
                @keyframes float {{
                    0%, 100% {{ transform: translate(-50%, -50%) scale(1); }}
                    50% {{ transform: translate(-50%, -52%) scale(1.02); }}
                }}
                @keyframes glow {{
                    0%, 100% {{ filter: drop-shadow(0 0 3px rgba(57, 79, 121, 0.3)); }}
                    50% {{ filter: drop-shadow(0 0 8px rgba(57, 79, 121, 0.6)); }}
                }}
                .rotating-text {{
                    animation: rotate 20s linear infinite;
                    transform-origin: center;
                    transition: all 0.3s ease;
                }}
                .rotating-text:hover {{
                    animation-play-state: paused;
                    filter: drop-shadow(0 0 5px rgba(57, 79, 121, 0.5));
                }}
                .chef-image {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 222px;
                    height: 240px;
                    z-index: 2;
                    animation: float 3s ease-in-out infinite;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }}
                .chef-image:hover {{
                    animation: float 3s ease-in-out infinite, glow 2s ease-in-out infinite;
                    transform: translate(-50%, -50%) scale(1.05);
                }}
            </style>
            <div class="svg-container">
                <svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <path id="circlePath" 
                              d="M200,200 m-160,0 a160,160 0 1,1 320,0 a160,160 0 1,1 -320,0"
                              fill="none"/>
                    </defs>
                    <g class="rotating-text">
                        <text>
                            <textPath href="#circlePath" startOffset="0%">
                                BE MY CHEF AI • YOUR VIRTUAL SOUS CHEF • TRY YOUR RECIPE •
                            </textPath>
                        </text>
                    </g>
                    <style>
                        text {{
                            font-size: 24px;
                            fill: #394F79;
                            letter-spacing: 4px;
                            font-family: 'Poppins', sans-serif;
                        }}
                    </style>
                </svg>
                <img src="data:image/png;base64,{img_base64}" class="chef-image" alt="Chef Logo">
            </div>
        </div>
    </div>
    '''
    
    st.components.v1.html(logo_html, height=400)