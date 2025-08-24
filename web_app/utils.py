"""
Utility Functions Module

Contains shared constants, helper functions, and common utilities used across the FPL application.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import time

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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_player_data():
    """Load and cache player data from CSV file with 5-minute refresh"""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
        
        if not os.path.exists(data_path):
            return None
        
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Error loading player data: {str(e)}")
        return None

def load_player_data_fresh():
    """Load player data without any caching - for immediate refresh"""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
        
        if not os.path.exists(data_path):
            return None
        
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Error loading fresh player data: {str(e)}")
        return None

def fetch_fresh_player_data():
    """Fetch fresh player data from FPL API and update local file - NO CACHE"""
    try:
        import sys
        import os
        import time
        project_root = os.path.dirname(os.path.dirname(__file__))
        sys.path.append(os.path.join(project_root, 'src'))
        
        from fetch_fpl_data import FPLDataFetcher
        
        # Clear any cached data first
        st.cache_data.clear()
        
        # Show current timestamp before refresh
        data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
        if os.path.exists(data_path):
            old_time = os.path.getmtime(data_path)
            st.info(f"Before refresh: File timestamp {time.ctime(old_time)}")
        
        # Create fetcher and fetch fresh data
        fetcher = FPLDataFetcher()
        
        # First, clean up all old timestamped files (web app mode)
        st.info("🧹 Cleaning up old data files...")
        try:
            removed_count = fetcher.cleanup_all_old_files(web_app_mode=True)
            if removed_count > 0:
                st.info(f"Cleaned up {removed_count} old files")
        except Exception as e:
            st.warning(f"Cleanup warning: {e}")
        
        # Show progress and run complete pipeline
        with st.spinner("Fetching data from FPL API..."):
            st.info("🌐 Connecting to FPL API...")
            
            # Run the complete pipeline with error handling
            try:
                fetcher.run(web_app_mode=True)  # Enable web app mode for aggressive cleanup
                st.success("✅ Data pipeline completed successfully")
            except Exception as e:
                st.error(f"❌ Data pipeline failed: {str(e)}")
                st.error("Please check your internet connection and try again.")
                return None
        
        # Verify files were created
        raw_data_files = [f for f in os.listdir(os.path.join(project_root, "data", "raw")) if f.startswith('fpl_data_') and not f.endswith('_latest.json')]
        fixture_files = [f for f in os.listdir(os.path.join(project_root, "data", "raw")) if f.startswith('fpl_fixtures_') and not f.endswith('_latest.json')]
        processed_files = [f for f in os.listdir(os.path.join(project_root, "data", "processed")) if f.startswith('fpl_players_') and not f.endswith('_latest.csv')]
        
        st.info(f"📁 Files created: {len(raw_data_files)} data, {len(fixture_files)} fixtures, {len(processed_files)} processed")
        
        # Force update the file timestamp to current time (backup approach)
        if os.path.exists(data_path):
            # Touch the file to ensure it has current timestamp
            os.utime(data_path, None)
            new_time = os.path.getmtime(data_path)
            st.info(f"After refresh: File timestamp {time.ctime(new_time)}")
        
        # Clear cache again to force reload
        st.cache_data.clear()
        
        # Load the fresh data without cache
        return load_player_data_fresh()
        
    except Exception as e:
        st.error(f"❌ Error in refresh process: {str(e)}")
        st.error("Please check the console for detailed error information.")
        import traceback
        st.text(traceback.format_exc())
        return None
        
    except Exception as e:
        st.error(f"Could not fetch fresh data: {str(e)}")
        import traceback
        st.error(f"Error details: {traceback.format_exc()}")
        # Fall back to cached data
        return load_player_data()

def get_data_freshness_info():
    """Get information about when data was last updated with real-time calculation"""
    try:
        import time
        import datetime
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
        
        current_time = time.time()
        
        # Check if we have a recent manual refresh first (highest priority)
        if hasattr(st.session_state, 'last_manual_refresh') and st.session_state.last_manual_refresh is not None:
            manual_refresh_time = st.session_state.last_manual_refresh
            time_since_manual = current_time - manual_refresh_time
            
            # If manual refresh was less than 10 minutes ago, use that as reference
            if time_since_manual < 600:  # 10 minutes
                total_seconds = int(time_since_manual)
                if total_seconds < 60:
                    return f"🟢 Data is fresh (refreshed {total_seconds}s ago)"
                else:
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    if seconds > 0:
                        return f"🟢 Data is fresh (refreshed {minutes}m {seconds}s ago)"
                    else:
                        return f"🟢 Data is fresh (refreshed {minutes}m ago)"
        
        # Fall back to file timestamp
        if os.path.exists(data_path):
            modified_time = os.path.getmtime(data_path)
            time_diff_seconds = current_time - modified_time
            total_seconds = int(time_diff_seconds)
            
            if total_seconds < 60:  # Less than 1 minute
                return f"🟢 Data is fresh (updated {total_seconds}s ago)"
            elif total_seconds < 3600:  # Less than 1 hour
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                if seconds > 0:
                    return f"🟡 Data is recent (updated {minutes}m {seconds}s ago)"
                else:
                    return f"🟡 Data is recent (updated {minutes}m ago)"
            elif total_seconds < 86400:  # Less than 1 day
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                if minutes > 0:
                    return f"🔴 Data is stale (updated {hours}h {minutes}m ago)"
                else:
                    return f"🔴 Data is stale (updated {hours}h ago)"
            else:  # More than 1 day
                days = total_seconds // 86400
                hours = (total_seconds % 86400) // 3600
                if hours > 0:
                    return f"🔴 Data is very stale (updated {days}d {hours}h ago)"
                else:
                    return f"🔴 Data is very stale (updated {days}d ago)"
        else:
            return "❌ No data file found"
            
    except Exception as e:
        return f"❓ Could not determine data freshness: {str(e)}"

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
    
    # Navigation buttons with immediate page switching
    if st.sidebar.button("🚀 Squad Optimizer", use_container_width=True):
        st.session_state.current_page = 'optimizer'
        st.session_state.last_user_interaction = time.time()  # Track user interaction
        st.rerun()  # Force immediate page change
    
    if st.sidebar.button("📊 Player Stats", use_container_width=True):
        st.session_state.current_page = 'stats'
        st.session_state.last_user_interaction = time.time()
        st.rerun()
    
    if st.sidebar.button("🗓️ Next 3 Gameweeks", use_container_width=True):
        st.session_state.current_page = 'fixtures'
        st.session_state.last_user_interaction = time.time()
        st.rerun()
    
    if st.sidebar.button("📈 Current Season Points", use_container_width=True):
        st.session_state.current_page = 'current_season'
        st.session_state.last_user_interaction = time.time()
        st.rerun()
    
    st.sidebar.divider()
    
    # Data refresh controls
    st.sidebar.markdown("## 🔄 Data Controls")
    
    # Real-time data freshness indicator
    freshness_info = get_data_freshness_info()
    st.sidebar.markdown(f"**Status:** {freshness_info}")
    
    # Refresh buttons
    refresh_clicked = st.sidebar.button("🔄 Refresh Data", use_container_width=True, help="Fetch latest data from FPL API", key="refresh_data_btn")
    
    if refresh_clicked:
        # Track user interaction to prevent auto-refresh conflicts
        st.session_state.last_user_interaction = time.time()
        
        # Clear cache before fetching
        st.cache_data.clear()
        
        # Store refresh time in session state immediately (this will reset the timer)
        st.session_state.last_manual_refresh = time.time()
        
        # Also reset auto-refresh timer to ensure immediate UI update
        st.session_state.last_auto_refresh = time.time()
        
        # Set a flag to indicate refresh is in progress (prevents double execution)
        if 'refresh_in_progress' not in st.session_state:
            st.session_state.refresh_in_progress = True
            
            # Show immediate feedback
            with st.spinner("Fetching fresh data from FPL API..."):
                players_df = fetch_fresh_player_data()
            
            if players_df is not None:
                st.success("✅ Data refreshed successfully!")
                # Update the loaded data in session state
                st.session_state.players_df = players_df
            else:
                st.error("❌ Failed to refresh data")
            
            # Clear the flag
            del st.session_state.refresh_in_progress
            
            # Force immediate rerun to update timestamp
            st.rerun()
        else:
            st.info("🔄 Refresh already in progress, please wait...")
    
    app_refresh_clicked = st.sidebar.button("🔄 Refresh App", use_container_width=True, help="Force refresh all cached data", key="refresh_app_btn")
    
    if app_refresh_clicked:
        st.session_state.last_user_interaction = time.time()
        st.cache_data.clear()
        # Clear any refresh flags
        if 'refresh_in_progress' in st.session_state:
            del st.session_state.refresh_in_progress
        st.rerun()
    
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
