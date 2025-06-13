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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #37003c;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #37003c;
    }
    .player-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 0.5rem;
    }
    .stats-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    .stats-header {
        color: #37003c;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    .nav-button {
        background-color: #37003c;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem;
        cursor: pointer;
    }
    .nav-button:hover {
        background-color: #5a0066;
    }
    .nav-button.active {
        background-color: #00ff87;
        color: #37003c;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_player_data():
    """Load and cache player data"""
    data_path = "data/processed/fpl_players_latest.csv"
    
    if not os.path.exists(data_path):
        return None
    
    return pd.read_csv(data_path)

@st.cache_resource
def load_optimizer(budget):
    """Load and cache the optimizer"""
    return FPLOptimizer(budget=budget)

def display_squad_table(selected_players):
    """Display the optimized squad in a formatted table"""
    
    # Position order for display
    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
    
    for position in position_order:
        position_players = selected_players[selected_players['position'] == position]
        
        if len(position_players) > 0:
            st.subheader(f"{position}s ({len(position_players)})")
            
            # Create columns for better layout
            cols = st.columns([3, 2, 1, 1, 1])
            cols[0].write("**Player**")
            cols[1].write("**Team**")
            cols[2].write("**Cost**")
            cols[3].write("**Form**")
            cols[4].write("**Pred. Pts**")
            
            for _, player in position_players.iterrows():
                cols = st.columns([3, 2, 1, 1, 1])
                cols[0].write(player['name'])
                cols[1].write(player['team'])
                cols[2].write(f"£{player['cost']:.1f}m")
                cols[3].write(f"{player['form']:.1f}")
                cols[4].write(f"{player['predicted_points']:.1f}")
            
            st.divider()

def create_position_pie_chart(selected_players):
    """Create a pie chart showing position distribution"""
    position_counts = selected_players['position'].value_counts()
    
    fig = px.pie(
        values=position_counts.values,
        names=position_counts.index,
        title="Squad Composition by Position",
        color_discrete_sequence=['#37003c', '#00ff87', '#e90052', '#04f5ff']
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    
    return fig

def create_team_distribution_chart(selected_players):
    """Create a bar chart showing team distribution"""
    team_counts = selected_players['team'].value_counts()
    
    fig = px.bar(
        x=team_counts.index,
        y=team_counts.values,
        title="Players per Team",
        labels={'x': 'Team', 'y': 'Number of Players'},
        color=team_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig

def create_cost_vs_points_scatter(selected_players):
    """Create a scatter plot of cost vs predicted points"""
    fig = px.scatter(
        selected_players,
        x='cost',
        y='predicted_points',
        color='position',
        size='form',
        hover_data=['name', 'team'],
        title="Cost vs Predicted Points",
        labels={'cost': 'Cost (£m)', 'predicted_points': 'Predicted Points'}
    )
    
    fig.update_layout(showlegend=True)
    
    return fig

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
    
    # Filter by position
    st.sidebar.header("🔍 Filters")
    position_filter = st.sidebar.selectbox(
        "Filter by Position",
        ["All Positions"] + sorted(players_df['position'].unique().tolist()),
        help="Filter statistics by player position"
    )
    
    # Apply position filter
    if position_filter != "All Positions":
        filtered_df = players_df[players_df['position'] == position_filter].copy()
    else:
        filtered_df = players_df.copy()
    
    # Remove managers if they exist
    filtered_df = filtered_df[filtered_df['position'] != 'Manager']
    
    # Create tabs for different stats
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥅 Goals & Assists", "⭐ Top Performers", "⏰ Playing Time", "💰 Value Analysis", "🏆 Elite Stats"])
    
    with tab1:
        st.markdown("### 🥅 Goals and Assists Leaders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🎯 Top 10 Goal Scorers</div>', unsafe_allow_html=True)
            
            top_scorers = filtered_df.nlargest(10, 'goals_scored')[
                ['name', 'position', 'team', 'goals_scored', 'cost', 'total_points']
            ].reset_index(drop=True)
            top_scorers.index = top_scorers.index + 1
            
            st.dataframe(
                top_scorers,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "goals_scored": st.column_config.NumberColumn("Goals", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🎯 Top 10 Assist Providers</div>', unsafe_allow_html=True)
            
            top_assists = filtered_df.nlargest(10, 'assists')[
                ['name', 'position', 'team', 'assists', 'cost', 'total_points']
            ].reset_index(drop=True)
            top_assists.index = top_assists.index + 1
            
            st.dataframe(
                top_assists,
                column_config={
                    "name": "Player",
                    "position": "Position", 
                    "team": "Team",
                    "assists": st.column_config.NumberColumn("Assists", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Goals + Assists Combined
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-header">🔥 Top 10 Goal Contributions (Goals + Assists)</div>', unsafe_allow_html=True)
        
        filtered_df['goal_contributions'] = filtered_df['goals_scored'] + filtered_df['assists']
        top_contributors = filtered_df.nlargest(10, 'goal_contributions')[
            ['name', 'position', 'team', 'goals_scored', 'assists', 'goal_contributions', 'cost', 'total_points']
        ].reset_index(drop=True)
        top_contributors.index = top_contributors.index + 1
        
        st.dataframe(
            top_contributors,
            column_config={
                "name": "Player",
                "position": "Position",
                "team": "Team", 
                "goals_scored": st.column_config.NumberColumn("Goals", format="%d"),
                "assists": st.column_config.NumberColumn("Assists", format="%d"),
                "goal_contributions": st.column_config.NumberColumn("Total", format="%d"),
                "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                "total_points": st.column_config.NumberColumn("Points", format="%d")
            },
            use_container_width=True,
            hide_index=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### ⭐ Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🏆 Top 10 Points Scorers</div>', unsafe_allow_html=True)
            
            top_points = filtered_df.nlargest(10, 'total_points')[
                ['name', 'position', 'team', 'total_points', 'points_per_game', 'cost']
            ].reset_index(drop=True)
            top_points.index = top_points.index + 1
            
            st.dataframe(
                top_points,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "total_points": st.column_config.NumberColumn("Total Points", format="%d"),
                    "points_per_game": st.column_config.NumberColumn("PPG", format="%.1f"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">📈 Top 10 Form Players</div>', unsafe_allow_html=True)
            
            top_form = filtered_df[filtered_df['form'] > 0].nlargest(10, 'form')[
                ['name', 'position', 'team', 'form', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_form.index = top_form.index + 1
            
            st.dataframe(
                top_form,
                column_config={
                    "name": "Player", 
                    "position": "Position",
                    "team": "Team",
                    "form": st.column_config.NumberColumn("Form", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### ⏰ Playing Time Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">⏱️ Top 10 Average Minutes Per Game</div>', unsafe_allow_html=True)
            
            # Filter players with at least some playing time
            playing_players = filtered_df[filtered_df['minutes'] > 0].copy()
            top_minutes = playing_players.nlargest(10, 'minutes_per_game')[
                ['name', 'position', 'team', 'minutes_per_game', 'minutes', 'total_points']
            ].reset_index(drop=True)
            top_minutes.index = top_minutes.index + 1
            
            st.dataframe(
                top_minutes,
                column_config={
                    "name": "Player",
                    "position": "Position", 
                    "team": "Team",
                    "minutes_per_game": st.column_config.NumberColumn("Avg Min/Game", format="%.1f"),
                    "minutes": st.column_config.NumberColumn("Total Minutes", format="%d"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🕐 Top 10 Total Minutes Played</div>', unsafe_allow_html=True)
            
            top_total_minutes = playing_players.nlargest(10, 'minutes')[
                ['name', 'position', 'team', 'minutes', 'minutes_per_game', 'total_points']
            ].reset_index(drop=True)
            top_total_minutes.index = top_total_minutes.index + 1
            
            st.dataframe(
                top_total_minutes,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team", 
                    "minutes": st.column_config.NumberColumn("Total Minutes", format="%d"),
                    "minutes_per_game": st.column_config.NumberColumn("Avg Min/Game", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 💰 Value Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">💎 Top 10 Cost Efficiency (Points per £)</div>', unsafe_allow_html=True)
            
            value_players = filtered_df[filtered_df['cost'] > 0].copy()
            top_value = value_players.nlargest(10, 'cost_efficiency')[
                ['name', 'position', 'team', 'cost_efficiency', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_value.index = top_value.index + 1
            
            st.dataframe(
                top_value,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "cost_efficiency": st.column_config.NumberColumn("Points per £", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d"),
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">📊 Top 10 Most Expensive Players</div>', unsafe_allow_html=True)
            
            expensive_players = filtered_df.nlargest(10, 'cost')[
                ['name', 'position', 'team', 'cost', 'total_points', 'cost_efficiency']
            ].reset_index(drop=True)
            expensive_players.index = expensive_players.index + 1
            
            st.dataframe(
                expensive_players,
                column_config={
                    "name": "Player",
                    "position": "Position",
                    "team": "Team",
                    "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", format="%d"),
                    "cost_efficiency": st.column_config.NumberColumn("Value", format="%.1f")
                },
                use_container_width=True,
                hide_index=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 🏆 Elite Performance Stats")
        
        # Position-specific elite stats
        if position_filter == "All Positions" or position_filter == "Goalkeeper":
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown('<div class="stats-header">🥅 Top 10 Goalkeepers (Clean Sheets & Saves)</div>', unsafe_allow_html=True)
            
            gk_df = filtered_df[filtered_df['position'] == 'Goalkeeper']
            if len(gk_df) > 0:
                top_gks = gk_df.nlargest(10, 'clean_sheets')[
                    ['name', 'team', 'clean_sheets', 'saves', 'total_points', 'cost']
                ].reset_index(drop=True)
                top_gks.index = top_gks.index + 1
                
                st.dataframe(
                    top_gks,
                    column_config={
                        "name": "Goalkeeper",
                        "team": "Team",
                        "clean_sheets": st.column_config.NumberColumn("Clean Sheets", format="%d"),
                        "saves": st.column_config.NumberColumn("Saves", format="%d"),
                        "total_points": st.column_config.NumberColumn("Points", format="%d"),
                        "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
                    },
                    use_container_width=True,
                    hide_index=False
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ICT Index Leaders
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-header">🎭 Top 10 ICT Index (Influence, Creativity, Threat)</div>', unsafe_allow_html=True)
        
        top_ict = filtered_df.nlargest(10, 'ict_index')[
            ['name', 'position', 'team', 'ict_index', 'influence', 'creativity', 'threat', 'total_points']
        ].reset_index(drop=True)
        top_ict.index = top_ict.index + 1
        
        st.dataframe(
            top_ict,
            column_config={
                "name": "Player",
                "position": "Position",
                "team": "Team",
                "ict_index": st.column_config.NumberColumn("ICT Index", format="%.1f"),
                "influence": st.column_config.NumberColumn("Influence", format="%.1f"),
                "creativity": st.column_config.NumberColumn("Creativity", format="%.1f"),
                "threat": st.column_config.NumberColumn("Threat", format="%.1f"),
                "total_points": st.column_config.NumberColumn("Points", format="%d")
            },
            use_container_width=True,
            hide_index=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ownership Analysis
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-header">👥 Top 10 Most Owned Players</div>', unsafe_allow_html=True)
        
        most_owned = filtered_df.nlargest(10, 'selected_by_percent')[
            ['name', 'position', 'team', 'selected_by_percent', 'total_points', 'cost']
        ].reset_index(drop=True)
        most_owned.index = most_owned.index + 1
        
        st.dataframe(
            most_owned,
            column_config={
                "name": "Player",
                "position": "Position",
                "team": "Team",
                "selected_by_percent": st.column_config.NumberColumn("Ownership %", format="%.1f%%"),
                "total_points": st.column_config.NumberColumn("Points", format="%d"),
                "cost": st.column_config.NumberColumn("Cost", format="£%.1f")
            },
            use_container_width=True,
            hide_index=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Summary stats at bottom
    st.divider()
    st.markdown("### 📈 Quick Statistics Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Players",
            len(filtered_df),
            f"Position: {position_filter}"
        )
    
    with col2:
        avg_cost = filtered_df['cost'].mean()
        st.metric(
            "Average Cost", 
            f"£{avg_cost:.1f}m",
            f"Range: £{filtered_df['cost'].min():.1f}-{filtered_df['cost'].max():.1f}m"
        )
    
    with col3:
        total_goals = filtered_df['goals_scored'].sum()
        st.metric(
            "Total Goals",
            f"{total_goals:,}",
            f"Avg: {filtered_df['goals_scored'].mean():.1f} per player"
        )
    
    with col4:
        total_assists = filtered_df['assists'].sum()
        st.metric(
            "Total Assists",
            f"{total_assists:,}",
            f"Avg: {filtered_df['assists'].mean():.1f} per player"
        )
    
    with col5:
        avg_ownership = filtered_df['selected_by_percent'].mean()
        st.metric(
            "Avg Ownership",
            f"{avg_ownership:.1f}%",
            f"Most owned: {filtered_df['selected_by_percent'].max():.1f}%"
        )

def create_footer():
    """Create the shared footer for all pages"""
    # Footer
    st.divider()
    
    # Developer info and photo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if developer photo exists (support multiple formats)
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        photo_path = None
        
        for ext in photo_extensions:
            potential_path = f"web_app/assets/images/developer{ext}"
            if os.path.exists(potential_path):
                photo_path = potential_path
                break
        
        if photo_path:
            # Display photo in circular frame with custom CSS
            st.markdown(
                """
                <style>
                .developer-photo {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 1rem;
                }
                .developer-photo img {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 4px solid #37003c;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease;
                }
                .developer-photo img:hover {
                    transform: scale(1.05);
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Use HTML to display the circular photo
            import base64
            with open(photo_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <div class="developer-photo">
                    <img src="data:image/jpeg;base64,{img_base64}" alt="Md Ataullah Khan Rifat">
                </div>
                """,
                unsafe_allow_html=True
            )
        
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
                It is not intended for commercial use.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Data Source:</strong> All player data is sourced from the official Fantasy Premier League API. 
                This application is not affiliated with or endorsed by the Premier League or Fantasy Premier League.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0;'>
                <strong>No Warranty:</strong> Predictions and recommendations are based on statistical models and should be used 
                as guidance only. The developer assumes no responsibility for Fantasy Premier League performance based on this tool.
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
    
    # Page navigation in sidebar
    st.sidebar.markdown("## 🧭 Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🚀 Squad Optimizer", use_container_width=True):
        st.session_state.current_page = 'optimizer'
    
    if st.sidebar.button("📊 Player Stats", use_container_width=True):
        st.session_state.current_page = 'stats'
    
    st.sidebar.divider()
    
    # Route to appropriate page
    if st.session_state.current_page == 'stats':
        create_stats_page(players_df)
    else:
        create_optimizer_page(players_df)
    
    # Shared Footer
    create_footer()

def create_optimizer_page(players_df):
    """Create the main optimizer page"""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ FPL Squad Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("**Optimize your Fantasy Premier League squad using machine learning and mathematical optimization**")
    
    st.success(f"✅ Loaded {len(players_df)} players")
    
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
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")
    
    # Team filter
    all_teams = ['All Teams'] + sorted(players_df['team'].unique().tolist())
    excluded_teams = st.sidebar.multiselect(
        "Exclude Teams",
        options=all_teams[1:],  # Exclude 'All Teams' from options
        help="Select teams to exclude from optimization"
    )
    
    # FDR Settings
    fdr_settings = st.sidebar.expander("🌟 FDR (Fixture Difficulty) Settings")
    with fdr_settings:
        use_fdr = st.checkbox("Use FDR in optimization", value=True, 
                             help="Consider fixture difficulty when selecting players")
        if use_fdr:
            st.info("Lower FDR = easier fixtures = higher player value")
            fdr_attack_weight = st.slider("Attack FDR Impact", 0.0, 0.3, 0.1, 0.05, 
                                        help="How much attack FDR affects forwards/midfielders")
            fdr_defence_weight = st.slider("Defence FDR Impact", 0.0, 0.3, 0.1, 0.05,
                                         help="How much defence FDR affects defenders/goalkeepers")
            fdr_overall_weight = st.slider("Overall FDR Impact", 0.0, 0.2, 0.05, 0.01,
                                         help="General FDR impact on all players")
    
    # Team Position Limits
    team_position_limits = st.sidebar.expander("🏆 Team Position Limits")
    with team_position_limits:
        st.info("Prevent algorithm from selecting too many players of same position from one team")
        selected_limit_teams = st.multiselect("Select teams to limit", all_teams[1:])
        
        team_pos_limits = {}
        for team in selected_limit_teams:
            st.write(f"**{team} Limits:**")
            col1, col2 = st.columns(2)
            with col1:
                def_limit = st.number_input(f"Max Defenders", min_value=0, max_value=3, value=2, key=f"def_{team}")
                fwd_limit = st.number_input(f"Max Forwards", min_value=0, max_value=3, value=1, key=f"fwd_{team}")
            with col2:
                mid_limit = st.number_input(f"Max Midfielders", min_value=0, max_value=3, value=2, key=f"mid_{team}")
                gk_limit = st.number_input(f"Max Goalkeepers", min_value=0, max_value=2, value=1, key=f"gk_{team}")
            
            team_pos_limits[team] = {
                'Defender': def_limit,
                'Midfielder': mid_limit, 
                'Forward': fwd_limit,
                'Goalkeeper': gk_limit
            }
    
    # Team requirements
    team_requirements = st.sidebar.expander("Team Requirements (Optional)")
    with team_requirements:
        st.info("Set exact number of players from specific teams")
        all_teams = sorted(players_df['team'].unique().tolist()) if players_df is not None else []
        selected_teams = st.multiselect("Select teams", all_teams)
        
        team_reqs = {}
        for team in selected_teams:
            team_reqs[team] = st.number_input(f"{team} players", min_value=0, max_value=3, value=1, key=f"team_{team}")
    
    # Budget usage
    min_budget_usage = st.sidebar.slider(
        "Minimum Budget Usage (%)",
        min_value=85,
        max_value=100,
        value=99,
        step=1,
        help="Force optimizer to use at least this percentage of budget"
    ) / 100
    
    # Expensive player settings
    expensive_player_settings = st.sidebar.expander("💰 Expensive Player Strategy")
    with expensive_player_settings:
        expensive_threshold = st.slider(
            "Expensive Player Threshold (£m)",
            min_value=6.0,
            max_value=12.0,
            value=8.0,
            step=0.5,
            help="Players above this cost should prioritize starting XI"
        )
        
        very_expensive_threshold = st.slider(
            "Very Expensive Threshold (£m)", 
            min_value=8.0,
            max_value=15.0,
            value=10.0,
            step=0.5,
            help="Limit these premium players on bench"
        )
        
        max_expensive_bench = st.number_input(
            "Max Very Expensive on Bench",
            min_value=0,
            max_value=3,
            value=1,
            help="Maximum very expensive players allowed on bench"
        )
    
    # Optimize button
    if st.sidebar.button("🚀 Optimize Squad", type="primary"):
        
        # Filter data based on user selections
        filtered_df = players_df.copy()
        
        if excluded_teams:
            filtered_df = filtered_df[~filtered_df['team'].isin(excluded_teams)]
        
        with st.spinner("🤖 Finding optimal squad..."):
            # Load optimizer with enhanced settings
            optimizer = load_optimizer(budget)
            optimizer.min_budget_usage = min_budget_usage
            
            # Set FDR weights if enabled
            if use_fdr:
                optimizer.use_fdr = True
                optimizer.set_fdr_weights({
                    'attack': fdr_attack_weight,
                    'defence': fdr_defence_weight,
                    'overall': fdr_overall_weight
                })
            else:
                optimizer.use_fdr = False
            
            # Set team position limits
            if team_pos_limits:
                optimizer.set_team_position_limits(team_pos_limits)
            
            # Set expensive player thresholds
            optimizer.expensive_threshold = expensive_threshold
            optimizer.very_expensive_threshold = very_expensive_threshold
            optimizer.max_expensive_bench = max_expensive_bench
            
            # Set team requirements if any
            if team_reqs:
                optimizer.set_team_requirements(team_reqs)
            
            # Load model and predict points
            optimizer.load_model()
            filtered_df = optimizer.predict_points(filtered_df)
            
            # Run optimization
            results = optimizer.optimize_squad(filtered_df)
        
        # Display results
        if results['status'] == 'optimal':
            st.success("✅ Optimization completed successfully!")
            
            selected_players = results['selected_players']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Cost",
                    f"£{results['total_cost']:.1f}m",
                    f"Budget: £{budget}m"
                )
            
            with col2:
                st.metric(
                    "Predicted Points",
                    f"{results['total_predicted_points']:.1f}",
                    f"Starting XI: {results.get('starting_predicted_points', 0):.1f}"
                )
            
            with col3:
                st.metric(
                    "Budget Usage",
                    f"{results.get('budget_usage_pct', 0):.1f}%",
                    f"£{results['remaining_budget']:.1f}m left"
                )
            
            with col4:
                avg_cost = results['total_cost'] / 15
                st.metric(
                    "Avg Player Cost",
                    f"£{avg_cost:.1f}m",
                    f"Max: £{selected_players['cost'].max():.1f}m"
                )
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 Starting XI", "📋 Full Squad", "📊 Analytics", "🏆 Top Players", "⚙️ Details"])
            
            with tab1:
                st.header("Starting XI (Most Important)")
                
                if 'starting_players' in results:
                    starting_players = results['starting_players']
                    
                    # Display starting formation
                    formation = f"GK: {len(starting_players[starting_players['position']=='Goalkeeper'])}-"
                    formation += f"DEF: {len(starting_players[starting_players['position']=='Defender'])}-"
                    formation += f"MID: {len(starting_players[starting_players['position']=='Midfielder'])}-"
                    formation += f"FWD: {len(starting_players[starting_players['position']=='Forward'])}"
                    
                    st.info(f"Formation: {formation} | Predicted Points: {results.get('starting_predicted_points', 0):.1f}")
                    
                    # Starting XI table
                    display_squad_table(starting_players)
                    
                    # Bench
                    if 'bench_players' in results and len(results['bench_players']) > 0:
                        st.subheader("Bench (4 players)")
                        bench_cols = st.columns([3, 2, 1, 1])
                        bench_cols[0].write("**Player**")
                        bench_cols[1].write("**Team**")
                        bench_cols[2].write("**Cost**")
                        bench_cols[3].write("**Role**")
                        
                        for _, player in results['bench_players'].iterrows():
                            bench_cols = st.columns([3, 2, 1, 1])
                            bench_cols[0].write(player['name'])
                            bench_cols[1].write(player['team'])
                            bench_cols[2].write(f"£{player['cost']:.1f}m")
                            bench_cols[3].write("Bench")
                else:
                    st.info("Starting XI breakdown not available. Showing top 11 players.")
                    top_11 = selected_players.head(11)
                    display_squad_table(top_11)
            
            with tab2:
                st.header("Complete Squad (15 Players)")
                display_squad_table(selected_players)
                
                # Download button
                csv = selected_players.to_csv(index=False)
                st.download_button(
                    label="📥 Download Squad CSV",
                    data=csv,
                    file_name=f"fpl_optimal_squad_budget_{budget}.csv",
                    mime="text/csv"
                )
            
            with tab3:
                st.header("Squad Analytics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Position pie chart
                    fig1 = create_position_pie_chart(selected_players)
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Team distribution
                    fig2 = create_team_distribution_chart(selected_players)
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Cost vs Points scatter
                fig3 = create_cost_vs_points_scatter(selected_players)
                st.plotly_chart(fig3, use_container_width=True)
            
            with tab4:
                st.header("Top Players by Predicted Points")
                
                # Top players table
                top_players = selected_players.nlargest(10, 'predicted_points')[
                    ['name', 'position', 'team', 'cost', 'form', 'predicted_points', 'total_points', 'selected_by_percent']
                ]
                
                st.dataframe(
                    top_players,
                    column_config={
                        "name": "Player",
                        "position": "Position",
                        "team": "Team",
                        "cost": st.column_config.NumberColumn("Cost", format="£%.1f"),
                        "form": st.column_config.NumberColumn("Form", format="%.1f"),
                        "predicted_points": st.column_config.NumberColumn("Predicted Points", format="%.1f"),
                        "total_points": st.column_config.NumberColumn("Season Points", format="%d"),
                        "selected_by_percent": st.column_config.NumberColumn("Ownership %", format="%.1f%%")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            with tab5:
                st.header("Optimization Details")
                
                # Settings applied
                st.subheader("Settings Applied")
                settings_data = [
                    ['Budget', f'£{budget}m'],
                    ['Min Budget Usage', f'{min_budget_usage*100:.0f}%'],
                    ['FDR Enabled', 'Yes' if use_fdr else 'No'],
                    ['Team Requirements', str(team_reqs) if team_reqs else 'None'],
                    ['Max per Team', f'{3} players']
                ]
                
                if use_fdr:
                    settings_data.extend([
                        ['FDR Attack Weight', f'{fdr_attack_weight:.2f}'],
                        ['FDR Defence Weight', f'{fdr_defence_weight:.2f}'],
                        ['FDR Overall Weight', f'{fdr_overall_weight:.2f}']
                    ])
                
                if team_pos_limits:
                    settings_data.append(['Team Position Limits', f'{len(team_pos_limits)} teams'])
                
                # Add expensive player settings
                settings_data.extend([
                    ['Expensive Player Threshold', f'£{expensive_threshold}m'],
                    ['Very Expensive Threshold', f'£{very_expensive_threshold}m'],
                    ['Max Expensive on Bench', str(max_expensive_bench)]
                ])
                
                settings_df = pd.DataFrame(settings_data, columns=['Setting', 'Value'])
                st.dataframe(settings_df, hide_index=True, use_container_width=True)
                
                # Constraints summary
                st.subheader("Constraints Applied")
                constraints_df = pd.DataFrame({
                    'Constraint': [
                        'Total Budget',
                        'Squad Size',
                        'Goalkeepers',
                        'Defenders',
                        'Midfielders',
                        'Forwards',
                        'Max per Team'
                    ],
                    'Requirement': [
                        f'≤ £{budget}m',
                        '= 15 players',
                        '= 2 players',
                        '= 5 players',
                        '= 5 players',
                        '= 3 players',
                        '≤ 3 players'
                    ],
                    'Actual': [
                        f'£{results["total_cost"]:.1f}m',
                        f'{len(selected_players)} players',
                        f'{results["position_breakdown"].get("Goalkeeper", 0)} players',
                        f'{results["position_breakdown"].get("Defender", 0)} players',
                        f'{results["position_breakdown"].get("Midfielder", 0)} players',
                        f'{results["position_breakdown"].get("Forward", 0)} players',
                        f'{max(results["team_breakdown"].values())} players'
                    ]
                })
                
                st.dataframe(constraints_df, hide_index=True, use_container_width=True)
                
                # Team breakdown
                st.subheader("Team Distribution")
                team_df = pd.DataFrame(list(results['team_breakdown'].items()), 
                                     columns=['Team', 'Players'])
                team_df = team_df.sort_values('Players', ascending=False)
                st.dataframe(team_df, hide_index=True, use_container_width=True)
        
        else:
            st.error("❌ Optimization failed!")
            st.error(results.get('message', 'No feasible solution found'))
            st.info("Try adjusting your budget or constraints.")
    
    # Footer
    st.divider()
    
    # Developer info and photo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if developer photo exists (support multiple formats)
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        photo_path = None
        
        for ext in photo_extensions:
            potential_path = f"web_app/assets/images/developer{ext}"
            if os.path.exists(potential_path):
                photo_path = potential_path
                break
        
        if photo_path:
            # Display photo in circular frame with custom CSS
            st.markdown(
                """
                <style>
                .developer-photo {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 1rem;
                }
                .developer-photo img {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 4px solid #37003c;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease;
                }
                .developer-photo img:hover {
                    transform: scale(1.05);
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Use HTML to display the circular photo
            import base64
            with open(photo_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <div class="developer-photo">
                    <img src="data:image/jpeg;base64,{img_base64}" alt="Md Ataullah Khan Rifat">
                </div>
                """,
                unsafe_allow_html=True
            )
        
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
                It is not intended for commercial use.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>
                <strong>Data Source:</strong> All player data is sourced from the official Fantasy Premier League API. 
                This application is not affiliated with or endorsed by the Premier League or Fantasy Premier League.
            </p>
            <p style='color: #666; font-size: 0.9rem; margin-bottom: 0;'>
                <strong>No Warranty:</strong> Predictions and recommendations are based on statistical models and should be used 
                as guidance only. The developer assumes no responsibility for Fantasy Premier League performance based on this tool.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
