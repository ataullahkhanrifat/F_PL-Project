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
