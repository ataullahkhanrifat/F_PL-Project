"""
Utility Functions Module

Contains shared constants, helper functions, and common utilities used across the FPL application.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# FPL Constants
FPL_CONSTANTS = {
    'MAX_BUDGET': 100.0,
    'SQUAD_SIZE': 15,
    'STARTING_XI_SIZE': 11,
    'MAX_PLAYERS_PER_TEAM': 3,
    'POSITION_LIMITS': {
        'Goalkeeper': 2,
        'Defender': 5,
        'Midfielder': 5,
        'Forward': 3
    },
    'STARTING_FORMATION_LIMITS': {
        'Goalkeeper': 1,
        'Defender': {'min': 3, 'max': 5},
        'Midfielder': {'min': 3, 'max': 5},
        'Forward': {'min': 1, 'max': 3}
    }
}

# FPL Theme Colors
FPL_COLORS = {
    'primary': '#37003c',
    'secondary': '#5a0066',
    'accent': '#00ff87',
    'info': '#04f5ff',
    'warning': '#e90052',
    'success': '#00bcd4',
    'background': '#ffffff',
    'sidebar': '#f0f2f6',
    'text': '#262730'
}

@st.cache_data
def load_player_data():
    """Load and cache player data from CSV file"""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
        
        if not os.path.exists(data_path):
            return None
        
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Error loading player data: {str(e)}")
        return None

def filter_available_players(players_df):
    """
    Filter out players who are not available for selection
    
    Args:
        players_df: Raw player DataFrame
    
    Returns:
        Filtered DataFrame with available players only
    """
    if players_df is None:
        return None
    
    # Remove players with 0 minutes played and very low ownership (likely not active)
    inactive_players = players_df[
        (players_df['minutes'] == 0) & 
        (players_df['selected_by_percent'] < 0.1) &
        (players_df['total_points'] == 0)
    ]
    
    if not inactive_players.empty:
        print(f"[Background] Filtered out {len(inactive_players)} inactive players")
    
    players_df = players_df[~(
        (players_df['minutes'] == 0) & 
        (players_df['selected_by_percent'] < 0.1) &
        (players_df['total_points'] == 0)
    )].copy()
    
    return players_df

def apply_custom_css():
    """Apply custom CSS styling for the FPL app"""
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {FPL_COLORS['background']} !important;
            color: {FPL_COLORS['text']} !important;
        }}
        
        .main .block-container {{
            background-color: {FPL_COLORS['background']} !important;
            color: {FPL_COLORS['text']} !important;
            padding-top: 2rem;
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: {FPL_COLORS['sidebar']} !important;
            color: {FPL_COLORS['text']} !important;
        }}
        
        .main-header {{
            font-size: 3rem;
            color: {FPL_COLORS['primary']} !important;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }}
        
        .stButton > button {{
            background-color: {FPL_COLORS['primary']} !important;
            color: {FPL_COLORS['background']} !important;
            border: 2px solid {FPL_COLORS['primary']} !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
        }}
        
        .stButton > button:hover {{
            background-color: {FPL_COLORS['secondary']} !important;
            color: {FPL_COLORS['background']} !important;
            border-color: {FPL_COLORS['secondary']} !important;
        }}
        
        section[data-testid="stSidebar"] .stButton > button {{
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* Hide Streamlit deploy button */
        .stDeployButton {{
            display: none !important;
        }}
        
        button[data-testid="stDecoratedHeader"] {{
            display: none !important;
        }}
        
        .stActionButton {{
            display: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_footer():
    """Create the shared footer for all pages"""
    st.divider()
    
    # Developer info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style='text-align: center; color: #666;'>
                <p><strong>Developed by: Md Ataullah Khan Rifat</strong></p>
                <p>Built with ❤️ for FPL managers</p>
                <p><small>Data from official FPL API</small></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Disclaimer
    st.markdown(
        f"""
        <div style='background-color: {FPL_COLORS['sidebar']}; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
            <h4 style='color: {FPL_COLORS['primary']}; margin-bottom: 0.5rem;'>📢 Disclaimer</h4>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Educational Use Only:</strong> This application is developed for educational and research purposes only.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Data Source:</strong> All player data is sourced from the official Fantasy Premier League API.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0;'>
                <strong>No Warranty:</strong> Predictions and recommendations are based on statistical models and should be used as guidance only.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def format_currency(amount, symbol='£'):
    """Format currency values consistently"""
    return f"{symbol}{amount:.1f}m"

def format_percentage(value, decimal_places=1):
    """Format percentage values consistently"""
    return f"{value:.{decimal_places}f}%"

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is 0"""
    if denominator == 0:
        return default
    return numerator / denominator

def calculate_player_value_score(points, cost, form_weight=0.3):
    """
    Calculate a value score for players
    
    Args:
        points: Total points scored
        cost: Player cost
        form_weight: Weight for recent form (0-1)
    
    Returns:
        Value score
    """
    if cost == 0:
        return 0
    
    base_value = points / cost
    # This could be enhanced with form data
    return base_value

def validate_data_quality(players_df):
    """
    Validate the quality of player data
    
    Args:
        players_df: Player DataFrame to validate
    
    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'data_quality_score': 100
    }
    
    required_columns = ['name', 'position', 'team', 'cost', 'total_points']
    missing_columns = [col for col in required_columns if col not in players_df.columns]
    
    if missing_columns:
        validation['valid'] = False
        validation['errors'].append(f"Missing required columns: {missing_columns}")
        validation['data_quality_score'] -= 50
    
    # Check for missing values in critical columns
    for col in required_columns:
        if col in players_df.columns:
            missing_count = players_df[col].isna().sum()
            if missing_count > 0:
                validation['warnings'].append(f"{missing_count} missing values in {col}")
                validation['data_quality_score'] -= (missing_count / len(players_df)) * 10
    
    # Check for unrealistic values
    if 'cost' in players_df.columns:
        if players_df['cost'].max() > 20 or players_df['cost'].min() < 3:
            validation['warnings'].append("Some player costs seem unrealistic")
            validation['data_quality_score'] -= 5
    
    return validation

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="FPL Squad Optimizer",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'optimizer'
    
    if 'selected_players' not in st.session_state:
        st.session_state.selected_players = []
    
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None

def create_navigation_sidebar():
    """Create the navigation sidebar"""
    st.sidebar.markdown("## 🧭 Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🚀 Squad Optimizer", use_container_width=True):
        st.session_state.current_page = 'optimizer'
    
    if st.sidebar.button("📊 Player Stats", use_container_width=True):
        st.session_state.current_page = 'stats'
    
    if st.sidebar.button("🗓️ Next 3 Gameweeks", use_container_width=True):
        st.session_state.current_page = 'fixtures'
    
    if st.sidebar.button("📈 Current Season Points", use_container_width=True):
        st.session_state.current_page = 'current_season'
    
    st.sidebar.divider()

def display_error_message(error_msg, error_type="error"):
    """Display formatted error messages"""
    if error_type == "error":
        st.error(f"❌ {error_msg}")
    elif error_type == "warning":
        st.warning(f"⚠️ {error_msg}")
    elif error_type == "info":
        st.info(f"💡 {error_msg}")

def format_player_card(player, style="default"):
    """
    Format a player card with consistent styling
    
    Args:
        player: Player data dictionary
        style: Card style ("forward", "defender", "midfielder", "goalkeeper", "default")
    
    Returns:
        HTML string for the player card
    """
    style_configs = {
        'forward': {'gradient': 'linear-gradient(90deg, #37003c, #5a0066)', 'text_color': 'white'},
        'defender': {'gradient': 'linear-gradient(90deg, #00ff87, #04f5ff)', 'text_color': '#37003c'},
        'midfielder': {'gradient': 'linear-gradient(90deg, #e90052, #ff6b9d)', 'text_color': 'white'},
        'goalkeeper': {'gradient': 'linear-gradient(90deg, #04f5ff, #00bcd4)', 'text_color': 'white'},
        'default': {'gradient': 'linear-gradient(90deg, #f0f2f6, #e0e0e0)', 'text_color': '#37003c'}
    }
    
    config = style_configs.get(style, style_configs['default'])
    
    return f"""
    <div style='background: {config["gradient"]}; color: {config["text_color"]}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
        <h4 style='margin: 0; color: {config["text_color"]};'>{player['name']}</h4>
        <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player.get('form', 0):.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
        <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Points: {player.get('total_points', 0)}</p>
    </div>
    """
