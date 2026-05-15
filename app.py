import torch

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from modules.controller import controller


def main() -> None:
    st.set_page_config(
        page_title="Smart Split Bill AI",
        page_icon="💵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        /* Hide Streamlit Branding & Header */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Global Typography */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        
        /* Main container styling */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
            max-width: 1000px;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5 {
            font-weight: 800 !important;
            letter-spacing: -0.03em;
        }
        
        /* DataFrames & Tables Enhancement */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(128, 128, 128, 0.2);
        }
        
        /* Primary button specifically */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
        }
        .stButton>button[kind="primary"]:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
            color: white;
        }
        
        /* Secondary buttons */
        .stButton>button[kind="secondary"] {
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 1px solid rgba(128, 128, 128, 0.2);
            background: rgba(128, 128, 128, 0.05);
        }
        .stButton>button[kind="secondary"]:hover {
            border-color: #3b82f6;
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
        }

        /* Glassmorphism Containers - Adaptive */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            background: rgba(128, 128, 128, 0.03) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px !important;
            border: 1px solid rgba(128, 128, 128, 0.15) !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            padding: 2rem !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
        }
        
        /* Upload box styling - Adaptive */
        div[data-testid="stFileUploader"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(99, 102, 241, 0.05) 100%);
            backdrop-filter: blur(5px);
            border: 2px dashed rgba(79, 70, 229, 0.4);
            border-radius: 20px;
            padding: 2.5rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #4F46E5;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
            transform: scale(1.01);
        }
        
        /* Info/Warning/Success boxes */
        div[data-testid="stAlert"] {
            border-radius: 14px;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            font-weight: 500;
        }
        
        /* Text Input & Number Input */
        div[data-baseweb="input"] {
            border-radius: 10px !important;
        }
        
        /* Multiselect Tags */
        span[data-baseweb="tag"] {
            background-color: rgba(59, 130, 246, 0.1) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    controller()


if __name__ == "__main__":
    main()