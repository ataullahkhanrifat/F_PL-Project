#!/usr/bin/env python3
"""
FPL Squad Optimizer Web App

A Streamlit application for optimizing Fantasy Premier League squads
using machine learning predictions and linear programming.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import os
import sys
import json
import base64

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from optimizer import FPLOptimizer
    from fetch_fpl_data import FPLDataFetcher
except ImportError:
    st.error("Could not import required modules. Please ensure you're running from the project root.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="FPL Squad Optimizer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'optimizer'

# Custom CSS for light theme
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    .main .block-container {
        background-color: #ffffff !important;
        color: #262730 !important;
        padding-top: 2rem;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
    }
    
    .main-header {
        font-size: 3rem;
        color: #37003c !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .stButton > button {
        background-color: #37003c !important;
        color: #ffffff !important;
        border: 2px solid #37003c !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #5a0066 !important;
        color: #ffffff !important;
        border-color: #5a0066 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_player_data():
    """Load and cache player data"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(project_root, "data", "processed", "fpl_players_latest.csv")
    
    if not os.path.exists(data_path):
        return None
    
    return pd.read_csv(data_path)

@st.cache_resource
def load_optimizer(budget):
    """Load and cache the optimizer"""
    return FPLOptimizer(budget=budget)

def filter_available_players(players_df):
    """Silently filter out players who are not available for selection"""
    if players_df is None:
        return None
    
    # Note: Relegation filtering removed - all teams in dataset are current Premier League teams
    
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

def create_fixtures_page(players_df):
    """Create the Next 3 Gameweeks fixtures analysis page"""
    st.title("🗓️ Next 3 Gameweeks Analysis")
    st.markdown("**Optimize your transfers and captaincy based on upcoming fixture difficulty**")
    
    # Navigation button to other pages
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        if st.button("🚀 Back to Optimizer", key="goto_optimizer_from_fixtures"):
            st.session_state.current_page = 'optimizer'
            st.rerun()
    
    st.divider()
    
    # Initialize optimizer for fixture analysis
    optimizer = FPLOptimizer()
    
    with st.spinner("🔍 Analyzing upcoming fixtures and player recommendations..."):
        try:
            fixture_analysis = optimizer.analyze_next_3_gameweeks(players_df)
        except Exception as e:
            st.error(f"❌ Error analyzing fixtures: {str(e)}")
            st.info("💡 This might be due to missing fixture data. Please try refreshing the player data.")
            return
    
    if not fixture_analysis:
        st.warning("⚠️ No fixture analysis data available")
        return
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Position Recommendations", 
        "🏆 Best Fixture Teams", 
        "📊 FDR Rankings",
        "👑 Captain Picks"
    ])
    
    with tab1:
        st.subheader("🎯 Position-Specific Recommendations (Next 3 GWs)")
        st.markdown("📊 **These recommendations are based on Fixture Difficulty Rating (FDR) - Lower FDR = Easier opponents**")
        
        col1, col2 = st.columns(2)
        
        # Forwards
        with col1:
            st.markdown("### ⚽ **FORWARDS** (Best attacking fixtures)")
            if 'forwards' in fixture_analysis.get('position_recommendations', {}):
                forwards = fixture_analysis['position_recommendations']['forwards']
                for i, player in enumerate(forwards[:3], 1):
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, #37003c, #5a0066); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                        <h4 style='margin: 0; color: white;'>{i}. {player['name']}</h4>
                        <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player['selected_by_percent']:.1f}%</p>
                        <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Season: {player.get('season_points', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No forward recommendations available")
        
        with col2:
            st.markdown("### 🛡️ **DEFENDERS** (Best defensive fixtures)")
            if 'defenders' in fixture_analysis.get('position_recommendations', {}):
                defenders = fixture_analysis['position_recommendations']['defenders']
                for i, player in enumerate(defenders[:3], 1):
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, #00ff87, #04f5ff); color: #37003c; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                        <h4 style='margin: 0; color: #37003c;'>{i}. {player['name']}</h4>
                        <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player['selected_by_percent']:.1f}%</p>
                        <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Season: {player.get('season_points', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No defender recommendations available")
        
        # Midfielders
        st.markdown("### 🎨 **MIDFIELDERS** (Best attacking fixtures)")
        if 'midfielders' in fixture_analysis.get('position_recommendations', {}):
            midfielders = fixture_analysis['position_recommendations']['midfielders']
            for i, player in enumerate(midfielders[:3], 1):
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #e90052, #ff6b9d); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: white;'>{i}. {player['name']}</h4>
                    <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player['selected_by_percent']:.1f}%</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Season: {player.get('season_points', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No midfielder recommendations available")
        
        # Goalkeepers  
        st.markdown("### 🥅 **GOALKEEPERS** (Best clean sheet chances)")
        if 'goalkeepers' in fixture_analysis.get('position_recommendations', {}):
            goalkeepers = fixture_analysis['position_recommendations']['goalkeepers']
            for i, player in enumerate(goalkeepers[:3], 1):
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #04f5ff, #00bcd4); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: white;'>{i}. {player['name']}</h4>
                    <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player['selected_by_percent']:.1f}%</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Season: {player.get('season_points', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No goalkeeper recommendations available")
    
    with tab2:
        st.subheader("🏆 Teams with Best Fixtures")
        st.markdown("Teams with the easiest upcoming fixtures (lower FDR is better):")
        
        if 'team_analysis' in fixture_analysis:
            # Best teams analysis
            best_teams_data = []
            for i, team_data in enumerate(fixture_analysis['team_analysis'][:8]):
                best_teams_data.append({
                    'Rank': i + 1,
                    'Team': team_data['team'],
                    'Next Opponent': team_data.get('next_opponent', 'N/A'),
                    'Home/Away': team_data.get('home_away', 'N/A'),
                    'Overall FDR': f"{team_data.get('fdr_overall', 0):.1f}",
                    'Attack FDR': f"{team_data.get('fdr_attack', 0):.1f}",
                    'Defence FDR': f"{team_data.get('fdr_defence', 0):.1f}",
                    'Fixtures': team_data.get('fixtures_count', 0)
                })
            
            best_teams_df = pd.DataFrame(best_teams_data)
            st.dataframe(best_teams_df, use_container_width=True, hide_index=True)
        else:
            st.info("No team analysis data available")
        
        # FDR explanation
        st.info("""
        **FDR (Fixture Difficulty Rating) Guide:**
        - 🟢 1-2: Very Easy fixtures
        - 🟡 2-3: Moderate fixtures  
        - 🔴 3-5: Difficult fixtures
        """)
    
    with tab3:
        st.subheader("📊 Complete FDR Rankings")
        st.markdown("All teams ranked by fixture difficulty:")
        
        if 'fdr_rankings' in fixture_analysis:
            # Create comprehensive FDR table
            fdr_data = []
            for i, team in enumerate(fixture_analysis['fdr_rankings']):
                fdr_data.append({
                    'Rank': i + 1,
                    'Team': team['team'],
                    'Overall FDR': team.get('fdr_overall', 0),
                    'Attack FDR': team.get('fdr_attack', 0),
                    'Defence FDR': team.get('fdr_defence', 0),
                    'Next Opponent': team.get('next_opponent', 'N/A'),
                    'Venue': 'Home' if team.get('next_fixture_home', False) else 'Away'
                })
            
            fdr_df = pd.DataFrame(fdr_data)
            
            # Create FDR visualization
            fig = px.scatter(
                fdr_df, 
                x='Attack FDR', 
                y='Defence FDR',
                size='Overall FDR',
                color='Overall FDR',
                hover_name='Team',
                hover_data=['Next Opponent', 'Venue'],
                color_continuous_scale='RdYlGn_r',
                title="Team FDR Analysis - Attack vs Defence Difficulty"
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(fdr_df, use_container_width=True, hide_index=True)
        else:
            st.info("No FDR rankings data available")
    
    with tab4:
        st.subheader("👑 Captain Recommendations")
        st.markdown("Best captain options based on form and fixtures:")
        
        if 'captain_picks' in fixture_analysis:
            captain_picks = fixture_analysis['captain_picks']
            
            if captain_picks:
                # Create captain picks grid
                cols = st.columns(2)
                
                for i, player in enumerate(captain_picks[:8]):  # Top 8 captain options
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div style='background-color: rgba(0, 255, 135, 0.1); padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; border: 2px solid #00ff87;'>
                            <h3 style='margin: 0; color: #37003c;'>#{i+1} {player['name']}</h3>
                            <p style='margin: 0.3rem 0; color: #666;'>{player['team']} | £{player['cost']:.1f}m</p>
                            <p style='margin: 0.3rem 0; color: #37003c; font-weight: bold;'>Form: {player['form']:.1f} | Predicted: {player.get('predicted_points', 'N/A')}</p>
                            <p style='margin: 0.3rem 0; color: #888; font-size: 0.9em;'>Ownership: {player['selected_by_percent']:.1f}% | Score: {player.get('fixture_score', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No captain recommendations available")
        else:
            st.info("No captain picks data available")

def create_stats_page(players_df):
    """Create the Stats page with various player statistics"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 FPL Player Statistics</h1>', unsafe_allow_html=True)
    st.markdown("**Comprehensive statistics and leaderboards for all Premier League players**")
    
    # Navigation buttons in the main area
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        if st.button("🔙 Back to Optimizer", key="back_to_optimizer"):
            st.session_state.current_page = 'optimizer'
            st.rerun()
    
    st.divider()
    
    # Create simple stats tabs
    tab1, tab2 = st.tabs(["🏆 Top Performers", "📊 Team Analysis"])
    
    with tab1:
        st.subheader("⭐ Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏆 Top 10 Points Scorers")
            
            top_points = players_df.nlargest(10, 'total_points')[
                ['name', 'position', 'team', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_points.index = top_points.index + 1
            
            st.dataframe(top_points, use_container_width=True, hide_index=False)
        
        with col2:
            st.markdown("### 📈 Top 10 Form Players")
            
            top_form = players_df[players_df['form'] > 0].nlargest(10, 'form')[
                ['name', 'position', 'team', 'form', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_form.index = top_form.index + 1
            
            st.dataframe(top_form, use_container_width=True, hide_index=False)
    
    with tab2:
        st.subheader("📊 Team Analysis")
        
        # Team performance summary
        team_stats = players_df.groupby('team').agg({
            'total_points': 'sum',
            'goals_scored': 'sum',
            'assists': 'sum',
            'cost': 'mean'
        }).round(2)
        
        team_stats = team_stats.sort_values('total_points', ascending=False)
        st.dataframe(team_stats, use_container_width=True)

def create_optimizer_page(players_df):
    """Create the main optimizer page"""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ FPL Squad Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("**Optimize your Fantasy Premier League squad using machine learning and mathematical optimization**")
    
    st.success(f"✅ Loaded {len(players_df)} available players (filtered for quality and availability)")
    
    # Navigation button to Stats page
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        if st.button("📊 View Player Stats", key="goto_stats"):
            st.session_state.current_page = 'stats'
            st.rerun()
    
    st.divider()
    
    # Sidebar controls
    st.sidebar.header("⚙️ Optimization Settings")
    
    # Budget slider
    budget = st.sidebar.slider(
        "Squad Budget (£m)",
        min_value=80.0,
        max_value=120.0,
        value=100.0,
        step=0.5,
        help="Total budget for your 15-player squad"
    )
    
    # Basic optimization
    if st.sidebar.button("🚀 Optimize Squad", type="primary"):
        
        with st.spinner("🤖 Finding optimal squad..."):
            # Load optimizer
            optimizer = load_optimizer(budget)
            
            # Load model and predict points
            optimizer.load_model()
            filtered_df = optimizer.predict_points(players_df)
            
            # Run optimization
            results = optimizer.optimize_squad(filtered_df)
        
        # Display results
        if results['status'] == 'optimal':
            st.success("✅ Optimization completed successfully!")
            
            selected_players = results['selected_players']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Cost", f"£{results['total_cost']:.1f}m")
            
            with col2:
                st.metric("Predicted Points", f"{results['total_predicted_points']:.1f}")
            
            with col3:
                st.metric("Budget Usage", f"{(results['total_cost']/budget*100):.1f}%")
            
            with col4:
                st.metric("Squad Size", f"{len(selected_players)} players")
            
            # Squad table
            st.subheader("Optimized Squad")
            st.dataframe(
                selected_players[['name', 'position', 'team', 'cost', 'predicted_points', 'form']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.error("❌ Optimization failed!")
            st.error(results.get('message', 'No feasible solution found'))

def create_footer():
    """Create the shared footer for all pages"""
    st.divider()
    
    # Developer info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
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
        """
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
            <h4 style='color: #37003c; margin-bottom: 0.5rem;'>📢 Disclaimer</h4>
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

def main():
    """Main application function with page navigation"""
    
    # Load data first
    with st.spinner("Loading player data..."):
        players_df = load_player_data()
    
    if players_df is None:
        st.error("❌ Player data not found!")
        st.info("Please run the following command first: `python src/fetch_fpl_data.py`")
        st.stop()
    
    # Silently filter out unavailable players in the background
    players_df = filter_available_players(players_df)
    
    if players_df is None or len(players_df) == 0:
        st.error("❌ No available players found after filtering!")
        st.stop()
    
    # Page navigation in sidebar
    st.sidebar.markdown("## 🧭 Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🚀 Squad Optimizer", use_container_width=True):
        st.session_state.current_page = 'optimizer'
    
    if st.sidebar.button("📊 Player Stats", use_container_width=True):
        st.session_state.current_page = 'stats'
    
    if st.sidebar.button("🗓️ Next 3 Gameweeks", use_container_width=True):
        st.session_state.current_page = 'fixtures'
    
    st.sidebar.divider()
    
    # Route to appropriate page
    if st.session_state.current_page == 'stats':
        create_stats_page(players_df)
    elif st.session_state.current_page == 'fixtures':
        create_fixtures_page(players_df)
    else:
        create_optimizer_page(players_df)
    
    # Shared Footer
    create_footer()

# Run the app
if __name__ == "__main__":
    main()
