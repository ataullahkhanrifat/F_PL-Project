#!/usr/bin/env python3
"""
FPL Squad Optimizer Web App

A Streamlit application for optimizing Fantasy Premier League squads
using machine learning predictions and linear programming.

This is the main entry point that orchestrates all modules.
"""

import streamlit as st

# Import our custom modules
from utils import (
    setup_page_config, 
    initialize_session_state, 
    apply_custom_css,
    create_navigation_sidebar,
    load_player_data,
    fetch_fresh_player_data,
    get_data_freshness_info,
    filter_available_players,
    create_footer,
    display_error_message,
    validate_data_quality
)

from FPL_Squad_Optimizer import create_optimizer_page
from FPL_Player_Statistics import create_stats_page
from Next_3_Gameweeks import create_fixtures_page
from Current_Season_Points import create_current_season_page

def main():
    """Main application function with page navigation"""
    
    # Setup page configuration
    setup_page_config()
    
    # Initialize session state
    initialize_session_state()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Auto-refresh for real-time timestamp updates (smart refresh to avoid button conflicts)
    import time
    if 'last_auto_refresh' not in st.session_state:
        st.session_state.last_auto_refresh = time.time()
    
    if 'last_user_interaction' not in st.session_state:
        st.session_state.last_user_interaction = time.time()
    
    # Only auto-refresh if no recent user interaction (prevents double-click issues)
    current_time = time.time()
    time_since_refresh = current_time - st.session_state.last_auto_refresh
    time_since_interaction = current_time - st.session_state.last_user_interaction
    
    # Auto-refresh only if:
    # 1. 15 seconds have passed since last refresh AND
    # 2. At least 3 seconds have passed since last user interaction
    if time_since_refresh > 15 and time_since_interaction > 3:
        st.session_state.last_auto_refresh = current_time
        st.rerun()
    
    # Load and validate data
    with st.spinner("Loading player data..."):
        players_df = load_player_data()
    
    if players_df is None:
        display_error_message("Player data not found!")
        st.info("Please run the following command first: `python src/fetch_fpl_data.py`")
        st.stop()
    
    # Validate data quality
    validation_results = validate_data_quality(players_df)
    if not validation_results['valid']:
        for error in validation_results['errors']:
            display_error_message(error, "error")
        st.stop()
    
    # Display warnings if any
    for warning in validation_results['warnings']:
        display_error_message(warning, "warning")
    
    # Filter out unavailable players
    players_df = filter_available_players(players_df)
    
    if players_df is None or len(players_df) == 0:
        display_error_message("No available players found after filtering!")
        st.stop()
    
    # Create navigation sidebar
    create_navigation_sidebar()
    
    # Route to appropriate page based on session state
    current_page = st.session_state.current_page
    
    try:
        if current_page == 'stats':
            create_stats_page(players_df)
        elif current_page == 'fixtures':
            create_fixtures_page(players_df)
        elif current_page == 'current_season':
            create_current_season_page(players_df)
        else:  # Default to optimizer
            create_optimizer_page(players_df)
    except Exception as e:
        display_error_message(f"Error loading {current_page} page: {str(e)}")
        st.error("Please try refreshing the page or contact support if the issue persists.")
    
    # Shared Footer
    create_footer()

# Run the app
if __name__ == "__main__":
    main()
