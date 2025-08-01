"""
FPL Player Statistics Module

Handles data retrieval and analysis for individual player statistics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

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

def get_top_performers(players_df, metric='total_points', top_n=10, position=None):
    """
    Get top performing players based on specified metric
    
    Args:
        players_df: DataFrame containing player data
        metric: Column name to rank by (default: 'total_points')
        top_n: Number of top players to return (default: 10)
        position: Filter by position (optional)
    
    Returns:
        DataFrame with top performers
    """
    # Filter by position if specified
    if position:
        filtered_df = players_df[players_df['position'] == position].copy()
    else:
        filtered_df = players_df.copy()
    
    # Get top performers
    top_performers = filtered_df.nlargest(top_n, metric)[
        ['name', 'position', 'team', metric, 'cost']
    ].reset_index(drop=True)
    
    return top_performers

def get_player_comparison(players_df, player_names):
    """
    Compare multiple players across key metrics
    
    Args:
        players_df: DataFrame containing player data
        player_names: List of player names to compare
    
    Returns:
        DataFrame with comparison data
    """
    comparison_players = players_df[players_df['name'].isin(player_names)].copy()
    
    if comparison_players.empty:
        return pd.DataFrame()
    
    # Select key comparison metrics
    comparison_cols = [
        'name', 'position', 'team', 'cost', 'total_points', 'form',
        'goals_scored', 'assists', 'minutes', 'selected_by_percent'
    ]
    
    # Filter columns that exist in the DataFrame
    available_cols = [col for col in comparison_cols if col in comparison_players.columns]
    
    return comparison_players[available_cols].reset_index(drop=True)

def get_position_analysis(players_df):
    """
    Analyze players by position with key statistics
    
    Args:
        players_df: DataFrame containing player data
    
    Returns:
        Dictionary with position analysis
    """
    position_analysis = {}
    
    for position in players_df['position'].unique():
        pos_players = players_df[players_df['position'] == position]
        
        analysis = {
            'count': len(pos_players),
            'avg_cost': pos_players['cost'].mean(),
            'avg_points': pos_players['total_points'].mean(),
            'avg_form': pos_players['form'].mean(),
            'top_scorer': {
                'name': pos_players.loc[pos_players['total_points'].idxmax(), 'name'],
                'points': pos_players['total_points'].max()
            },
            'most_expensive': {
                'name': pos_players.loc[pos_players['cost'].idxmax(), 'name'],
                'cost': pos_players['cost'].max()
            },
            'best_value': pos_players.loc[
                (pos_players['total_points'] / pos_players['cost']).idxmax(),
                ['name', 'total_points', 'cost']
            ].to_dict()
        }
        
        position_analysis[position] = analysis
    
    return position_analysis

def get_team_analysis(players_df):
    """
    Analyze teams based on their players' performance
    
    Args:
        players_df: DataFrame containing player data
    
    Returns:
        DataFrame with team analysis
    """
    team_stats = players_df.groupby('team').agg({
        'total_points': ['sum', 'mean'],
        'goals_scored': 'sum',
        'assists': 'sum',
        'cost': 'mean',
        'form': 'mean',
        'minutes': 'sum',
        'name': 'count'  # Number of players
    }).round(2)
    
    # Flatten column names
    team_stats.columns = [
        'total_points_sum', 'total_points_avg', 'goals_scored', 'assists',
        'avg_cost', 'avg_form', 'total_minutes', 'player_count'
    ]
    
    # Calculate additional metrics
    team_stats['points_per_player'] = team_stats['total_points_sum'] / team_stats['player_count']
    team_stats['goals_per_player'] = team_stats['goals_scored'] / team_stats['player_count']
    
    return team_stats.sort_values('total_points_sum', ascending=False)

def get_player_search(players_df, search_term):
    """
    Search for players by name or team
    
    Args:
        players_df: DataFrame containing player data
        search_term: String to search for
    
    Returns:
        DataFrame with matching players
    """
    search_term = search_term.lower()
    
    # Search in name and team columns
    mask = (
        players_df['name'].str.lower().str.contains(search_term, na=False) |
        players_df['team'].str.lower().str.contains(search_term, na=False)
    )
    
    return players_df[mask].sort_values('total_points', ascending=False)

def get_form_analysis(players_df, min_minutes=90):
    """
    Analyze player form with filtering options
    
    Args:
        players_df: DataFrame containing player data
        min_minutes: Minimum minutes played to be considered
    
    Returns:
        Dictionary with form analysis
    """
    # Filter players with minimum minutes
    active_players = players_df[players_df['minutes'] >= min_minutes].copy()
    
    form_analysis = {
        'hot_players': active_players.nlargest(10, 'form')[
            ['name', 'position', 'team', 'form', 'total_points']
        ].to_dict('records'),
        
        'cold_players': active_players.nsmallest(10, 'form')[
            ['name', 'position', 'team', 'form', 'total_points']
        ].to_dict('records'),
        
        'form_by_position': active_players.groupby('position')['form'].agg([
            'mean', 'std', 'max', 'min'
        ]).round(2).to_dict(),
        
        'form_by_team': active_players.groupby('team')['form'].agg([
            'mean', 'count'
        ]).round(2).sort_values('mean', ascending=False).to_dict()
    }
    
    return form_analysis

def calculate_player_metrics(players_df):
    """
    Calculate additional metrics for players
    
    Args:
        players_df: DataFrame containing player data
    
    Returns:
        DataFrame with additional calculated metrics
    """
    df = players_df.copy()
    
    # Avoid division by zero
    df['points_per_game'] = np.where(
        df['minutes'] > 0,
        df['total_points'] / (df['minutes'] / 90),
        0
    )
    
    df['points_per_cost'] = df['total_points'] / df['cost']
    df['form_per_cost'] = df['form'] / df['cost']
    
    # Goals + Assists
    if 'goals_scored' in df.columns and 'assists' in df.columns:
        df['goal_involvement'] = df['goals_scored'] + df['assists']
    
    # Value rating (combination of points per cost and form)
    df['value_rating'] = (df['points_per_cost'] * 0.7) + (df['form_per_cost'] * 0.3)
    
    return df
