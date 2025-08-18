"""
Current Season Points Module

Handles logic for displaying current gameweek points, previous gameweek points,
and live season statistics for FPL players.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import sys
import os

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_current_season_data():
    """Fetch current season data from FPL API"""
    try:
        # Fetch main data
        response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
        response.raise_for_status()
        data = response.json()
        
        # Find current gameweek
        current_gw = None
        current_event = None
        for event in data['events']:
            if event['is_current']:
                current_gw = event['id']
                current_event = event
                break
        
        if current_gw is None:
            # Fallback: find the latest finished gameweek
            for event in reversed(data['events']):
                if event['finished']:
                    current_gw = event['id']
                    current_event = event
                    break
            if current_gw:
                current_gw += 1  # Next gameweek
        
        # Get player data with current season stats
        players = data['elements']
        teams = {team['id']: team['name'] for team in data['teams']}
        positions = {pos['id']: pos['singular_name'] for pos in data['element_types']}
        
        # Process player data for current season
        season_data = []
        for player in players:
            season_data.append({
                'id': player['id'],
                'name': f"{player['first_name']} {player['second_name']}",
                'web_name': player['web_name'],
                'team': teams[player['team']],
                'position': positions[player['element_type']],
                'cost': player['now_cost'] / 10.0,
                'total_points': player['total_points'],
                'event_points': player['event_points'],  # Current/last gameweek points
                'form': float(player['form']) if player['form'] else 0.0,
                'points_per_game': float(player['points_per_game']) if player['points_per_game'] else 0.0,
                'selected_by_percent': float(player['selected_by_percent']),
                'minutes': player['minutes'],
                'goals_scored': player['goals_scored'],
                'assists': player['assists'],
                'clean_sheets': player['clean_sheets'],
                'goals_conceded': player['goals_conceded'],
                'own_goals': player['own_goals'],
                'penalties_saved': player['penalties_saved'],
                'penalties_missed': player['penalties_missed'],
                'yellow_cards': player['yellow_cards'],
                'red_cards': player['red_cards'],
                'saves': player['saves'],
                'bonus': player['bonus'],
                'bps': player['bps'],
                'influence': float(player['influence']) if player['influence'] else 0.0,
                'creativity': float(player['creativity']) if player['creativity'] else 0.0,
                'threat': float(player['threat']) if player['threat'] else 0.0,
                'ict_index': float(player['ict_index']) if player['ict_index'] else 0.0,
                'value_form': float(player['value_form']) if player['value_form'] else 0.0,
                'value_season': float(player['value_season']) if player['value_season'] else 0.0,
                'transfers_in': player['transfers_in'],
                'transfers_out': player['transfers_out'],
                'transfers_in_event': player['transfers_in_event'],
                'transfers_out_event': player['transfers_out_event'],
                'dreamteam_count': player['dreamteam_count'],
                'ep_this': float(player['ep_this']) if player['ep_this'] else 0.0,
                'ep_next': float(player['ep_next']) if player['ep_next'] else 0.0,
                'status': player['status']
            })
        
        return pd.DataFrame(season_data), current_gw, current_event, data['events']
    
    except Exception as e:
        st.error(f"Error fetching current season data: {str(e)}")
        return None, None, None, None

def create_current_season_page(players_df):
    """Create the Current Season Points analysis page"""
    st.title("📊 Current Season Points Analysis")
    st.markdown("**Live gameweek data, season leaders, and current form analysis**")
    
    # Navigation buttons to other pages
    col1, col2, col3, col4, col5 = st.columns(5)
    with col2:
        if st.button("🚀 Squad Optimizer", key="goto_optimizer_from_season"):
            st.session_state.current_page = 'optimizer'
            st.rerun()
    with col3:
        if st.button("📈 Player Stats", key="goto_stats_from_season"):
            st.session_state.current_page = 'stats'
            st.rerun()
    with col4:
        if st.button("🗓️ Next 3 Gameweeks", key="goto_fixtures_from_season"):
            st.session_state.current_page = 'fixtures'
            st.rerun()
    
    st.divider()
    
    # Fetch current season data
    with st.spinner("🔄 Fetching live FPL data..."):
        season_df, current_gw, current_event, all_events = fetch_current_season_data()
    
    if season_df is None:
        st.error("❌ Failed to fetch current season data. Please try again later.")
        return
    
    # Display current gameweek info
    if current_gw and current_event:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏆 Current Gameweek", f"GW {current_gw}")
        with col2:
            if current_event.get('finished', False):
                st.metric("📊 Status", "Finished")
            elif current_event.get('is_current', False):
                st.metric("📊 Status", "In Progress")
            else:
                st.metric("📊 Status", "Upcoming")
        with col3:
            deadline = current_event.get('deadline_time', 'N/A')
            if deadline != 'N/A':
                deadline = deadline.split('T')[0]  # Extract date only
            st.metric("⏰ Deadline", deadline)
        with col4:
            avg_score = current_event.get('average_entry_score', 0)
            st.metric("📈 Average Score", f"{avg_score} pts")
    
    st.divider()
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔥 Current GW", 
        "📈 Previous GW", 
        "🏆 Season Leaders",
        "📊 Form Analysis",
        "💎 Value Players"
    ])
    
    with tab1:
        display_current_gameweek(season_df, current_gw)
    
    with tab2:
        display_previous_gameweek(season_df, current_gw)
    
    with tab3:
        display_season_leaders(season_df)
    
    with tab4:
        display_form_analysis(season_df)
    
    with tab5:
        display_value_players(season_df)

def display_current_gameweek(season_df, current_gw):
    """Display current gameweek top performers"""
    st.markdown(f"### 🔥 Gameweek {current_gw if current_gw else 'Current'} Top Performers")
    
    # Filter players with points in current gameweek
    current_gw_performers = season_df[season_df['event_points'] > 0].sort_values('event_points', ascending=False)
    
    if len(current_gw_performers) > 0:
        # Top performers metrics
        col1, col2, col3, col4 = st.columns(4)
        
        highest_scorer = current_gw_performers.iloc[0]
        with col1:
            st.metric("🥇 Highest Scorer", 
                     f"{highest_scorer['web_name']}", 
                     f"{highest_scorer['event_points']} pts")
        
        with col2:
            avg_points = current_gw_performers['event_points'].mean()
            st.metric("📊 Average Points", f"{avg_points:.1f}")
        
        with col3:
            total_scorers = len(current_gw_performers)
            st.metric("👥 Players Scored", total_scorers)
        
        with col4:
            goals_scored = current_gw_performers['goals_scored'].sum()
            st.metric("⚽ Total Goals", goals_scored)
        
        st.markdown("---")
        
        # Top 20 performers table
        st.markdown("**🏆 Top 20 Current Gameweek Performers:**")
        
        top_performers = current_gw_performers.head(20)[
            ['web_name', 'name', 'team', 'position', 'event_points', 'cost', 'minutes', 'goals_scored', 'assists', 'bonus']
        ].copy()
        
        top_performers.columns = ['Player', 'Full Name', 'Team', 'Pos', 'GW Points', 'Cost (£m)', 'Minutes', 'Goals', 'Assists', 'Bonus']
        
        # Style the dataframe
        styled_df = top_performers.style.format({
            'Cost (£m)': '£{:.1f}m',
            'GW Points': '{:.0f}',
            'Minutes': '{:.0f}',
            'Goals': '{:.0f}',
            'Assists': '{:.0f}',
            'Bonus': '{:.0f}'
        }).background_gradient(subset=['GW Points'], cmap='RdYlGn', vmin=0, vmax=20)
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Position breakdown
        st.markdown("**📊 Points by Position:**")
        position_stats = current_gw_performers.groupby('position').agg({
            'event_points': ['count', 'sum', 'mean'],
            'goals_scored': 'sum',
            'assists': 'sum'
        }).round(1)
        
        position_stats.columns = ['Players', 'Total Points', 'Avg Points', 'Goals', 'Assists']
        st.dataframe(position_stats, use_container_width=True)
        
    else:
        st.info("⏳ Current gameweek in progress or no scoring data available yet.")
        
        # Show players with highest expected points for current gameweek
        st.markdown("**🎯 Players with Highest Expected Points:**")
        expected_performers = season_df.sort_values('ep_this', ascending=False).head(15)
        
        if len(expected_performers) > 0:
            expected_table = expected_performers[
                ['web_name', 'team', 'position', 'ep_this', 'cost', 'form']
            ].copy()
            expected_table.columns = ['Player', 'Team', 'Pos', 'Expected Points', 'Cost (£m)', 'Form']
            st.dataframe(expected_table, use_container_width=True, hide_index=True)

def display_previous_gameweek(season_df, current_gw):
    """Display previous gameweek analysis"""
    prev_gw = current_gw - 1 if current_gw and current_gw > 1 else 1
    st.markdown(f"### 📈 Gameweek {prev_gw} High Form Players")
    
    # Since we don't have specific previous GW data, show high form players
    st.markdown("**🔥 Players in Excellent Form (Last 5 Games):**")
    
    high_form = season_df[season_df['form'] > 0].sort_values('form', ascending=False).head(20)
    
    if len(high_form) > 0:
        # Form analysis metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            best_form = high_form.iloc[0]
            st.metric("🔥 Best Form", 
                     f"{best_form['web_name']}", 
                     f"{best_form['form']:.1f} pts/game")
        
        with col2:
            avg_form = high_form['form'].mean()
            st.metric("📊 Avg Form (Top 20)", f"{avg_form:.1f}")
        
        with col3:
            consistent_players = len(high_form[high_form['form'] >= 4.0])
            st.metric("⭐ Consistent Players", f"{consistent_players}")
        
        with col4:
            total_minutes = high_form['minutes'].mean()
            st.metric("⏱️ Avg Minutes", f"{total_minutes:.0f}")
        
        st.markdown("---")
        
        # High form players table
        form_table = high_form[
            ['web_name', 'team', 'position', 'form', 'points_per_game', 'total_points', 'cost', 'minutes']
        ].copy()
        
        form_table.columns = ['Player', 'Team', 'Pos', 'Form', 'PPG', 'Total Pts', 'Cost (£m)', 'Minutes']
        
        # Style with form gradient
        styled_form = form_table.style.format({
            'Form': '{:.1f}',
            'PPG': '{:.1f}',
            'Total Pts': '{:.0f}',
            'Cost (£m)': '£{:.1f}m',
            'Minutes': '{:.0f}'
        }).background_gradient(subset=['Form'], cmap='RdYlGn', vmin=0, vmax=8)
        
        st.dataframe(styled_form, use_container_width=True, hide_index=True)
        
        # Form distribution chart
        st.markdown("**📊 Form Distribution:**")
        form_ranges = pd.cut(season_df['form'], bins=[0, 2, 4, 6, 8, 10], labels=['0-2', '2-4', '4-6', '6-8', '8+'])
        form_counts = form_ranges.value_counts()
        
        fig = px.bar(x=form_counts.index, y=form_counts.values, 
                    title="Number of Players by Form Range",
                    labels={'x': 'Form Range', 'y': 'Number of Players'},
                    color=form_counts.values,
                    color_continuous_scale='RdYlGn')
        
        st.plotly_chart(fig, use_container_width=True)

def display_season_leaders(season_df):
    """Display season leaders across different categories"""
    st.markdown("### 🏆 2024/25 Season Leaders")
    
    # Overall leaders metrics
    col1, col2, col3, col4 = st.columns(4)
    
    top_scorer = season_df.sort_values('total_points', ascending=False).iloc[0]
    with col1:
        st.metric("👑 Points Leader", 
                 f"{top_scorer['web_name']}", 
                 f"{top_scorer['total_points']} pts")
    
    top_goals = season_df.sort_values('goals_scored', ascending=False).iloc[0]
    with col2:
        st.metric("⚽ Goals Leader", 
                 f"{top_goals['web_name']}", 
                 f"{top_goals['goals_scored']} goals")
    
    top_assists = season_df.sort_values('assists', ascending=False).iloc[0]
    with col3:
        st.metric("🎯 Assists Leader", 
                 f"{top_assists['web_name']}", 
                 f"{top_assists['assists']} assists")
    
    most_valuable = season_df.sort_values('value_season', ascending=False).iloc[0]
    with col4:
        st.metric("💎 Best Value", 
                 f"{most_valuable['web_name']}", 
                 f"{most_valuable['value_season']:.1f}")
    
    st.markdown("---")
    
    # Leaders tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Total Points Leaders:**")
        points_leaders = season_df.sort_values('total_points', ascending=False).head(15)[
            ['web_name', 'team', 'position', 'total_points', 'points_per_game', 'cost']
        ].copy()
        points_leaders.columns = ['Player', 'Team', 'Pos', 'Total Pts', 'PPG', 'Cost (£m)']
        
        styled_points = points_leaders.style.format({
            'Total Pts': '{:.0f}',
            'PPG': '{:.1f}',
            'Cost (£m)': '£{:.1f}m'
        }).background_gradient(subset=['Total Pts'], cmap='RdYlGn')
        
        st.dataframe(styled_points, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**⚽ Goals + Assists Leaders:**")
        season_df['goals_assists'] = season_df['goals_scored'] + season_df['assists']
        goal_leaders = season_df.sort_values('goals_assists', ascending=False).head(15)
        
        goal_table = goal_leaders[
            ['web_name', 'team', 'position', 'goals_scored', 'assists', 'goals_assists', 'cost']
        ].copy()
        goal_table.columns = ['Player', 'Team', 'Pos', 'Goals', 'Assists', 'G+A', 'Cost (£m)']
        
        styled_goals = goal_table.style.format({
            'Goals': '{:.0f}',
            'Assists': '{:.0f}',
            'G+A': '{:.0f}',
            'Cost (£m)': '£{:.1f}m'
        }).background_gradient(subset=['G+A'], cmap='RdYlGn')
        
        st.dataframe(styled_goals, use_container_width=True, hide_index=True)
    
    # Defensive leaders
    st.markdown("**🛡️ Defensive Leaders:**")
    defensive_stats = season_df[season_df['position'].isin(['Goalkeeper', 'Defender'])].copy()
    defensive_stats['defensive_points'] = defensive_stats['clean_sheets'] * 4 + defensive_stats['saves'] * 0.5
    
    def_leaders = defensive_stats.sort_values('defensive_points', ascending=False).head(12)
    def_table = def_leaders[
        ['web_name', 'team', 'position', 'clean_sheets', 'saves', 'goals_conceded', 'total_points', 'cost']
    ].copy()
    def_table.columns = ['Player', 'Team', 'Pos', 'Clean Sheets', 'Saves', 'Goals Conceded', 'Total Pts', 'Cost (£m)']
    
    st.dataframe(def_table, use_container_width=True, hide_index=True)

def display_form_analysis(season_df):
    """Display comprehensive form analysis"""
    st.markdown("### 📊 Form Analysis & Trends")
    
    # Form vs Performance correlation
    st.markdown("**🔥 Form vs Total Points Correlation:**")
    
    # Create scatter plot
    fig = px.scatter(season_df, x='form', y='total_points', 
                    color='position', size='cost',
                    hover_name='web_name',
                    hover_data=['team', 'cost'],
                    title="Player Form vs Season Points",
                    labels={'form': 'Current Form (Last 5 Games)', 'total_points': 'Total Season Points'})
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Form categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔥 Hot Form (5.0+ avg):**")
        hot_form = season_df[season_df['form'] >= 5.0].sort_values('form', ascending=False)
        if len(hot_form) > 0:
            hot_table = hot_form.head(10)[['web_name', 'team', 'form', 'total_points']].copy()
            hot_table.columns = ['Player', 'Team', 'Form', 'Total Pts']
            st.dataframe(hot_table, use_container_width=True, hide_index=True)
        else:
            st.info("No players currently in hot form")
    
    with col2:
        st.markdown("**📈 Good Form (3.0-4.9 avg):**")
        good_form = season_df[(season_df['form'] >= 3.0) & (season_df['form'] < 5.0)].sort_values('form', ascending=False)
        if len(good_form) > 0:
            good_table = good_form.head(10)[['web_name', 'team', 'form', 'total_points']].copy()
            good_table.columns = ['Player', 'Team', 'Form', 'Total Pts']
            st.dataframe(good_table, use_container_width=True, hide_index=True)
        else:
            st.info("No players in good form range")
    
    with col3:
        st.markdown("**❄️ Cold Form (0-2.9 avg):**")
        cold_form = season_df[(season_df['form'] > 0) & (season_df['form'] < 3.0)].sort_values('total_points', ascending=False)
        if len(cold_form) > 0:
            cold_table = cold_form.head(10)[['web_name', 'team', 'form', 'total_points']].copy()
            cold_table.columns = ['Player', 'Team', 'Form', 'Total Pts']
            st.dataframe(cold_table, use_container_width=True, hide_index=True)
        else:
            st.info("No players in cold form")
    
    # Transfer trends
    st.markdown("**📈 Transfer Trends:**")
    
    # Most transferred in/out this gameweek
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⬆️ Most Transferred IN:**")
        transfers_in = season_df.sort_values('transfers_in_event', ascending=False).head(10)
        transfers_in_table = transfers_in[
            ['web_name', 'team', 'transfers_in_event', 'form', 'cost']
        ].copy()
        transfers_in_table.columns = ['Player', 'Team', 'Transfers In', 'Form', 'Cost (£m)']
        st.dataframe(transfers_in_table, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**⬇️ Most Transferred OUT:**")
        transfers_out = season_df.sort_values('transfers_out_event', ascending=False).head(10)
        transfers_out_table = transfers_out[
            ['web_name', 'team', 'transfers_out_event', 'form', 'cost']
        ].copy()
        transfers_out_table.columns = ['Player', 'Team', 'Transfers Out', 'Form', 'Cost (£m)']
        st.dataframe(transfers_out_table, use_container_width=True, hide_index=True)

def display_value_players(season_df):
    """Display value players and budget options"""
    st.markdown("### 💎 Value Players & Budget Options")
    
    # Value metrics
    col1, col2, col3, col4 = st.columns(4)
    
    best_value = season_df.sort_values('value_season', ascending=False).iloc[0]
    with col1:
        st.metric("💎 Best Season Value", 
                 f"{best_value['web_name']}", 
                 f"{best_value['value_season']:.1f}")
    
    best_ppg_value = season_df.sort_values('points_per_game', ascending=False).iloc[0]
    with col2:
        st.metric("📊 Best PPG", 
                 f"{best_ppg_value['web_name']}", 
                 f"{best_ppg_value['points_per_game']:.1f}")
    
    # Budget options (under £6m)
    budget_players = season_df[season_df['cost'] <= 6.0]
    if len(budget_players) > 0:
        best_budget = budget_players.sort_values('total_points', ascending=False).iloc[0]
        with col3:
            st.metric("💰 Best Budget Option", 
                     f"{best_budget['web_name']}", 
                     f"£{best_budget['cost']:.1f}m")
    
    # Differential picks (under 5% ownership)
    differentials = season_df[season_df['selected_by_percent'] <= 5.0]
    if len(differentials) > 0:
        best_diff = differentials.sort_values('total_points', ascending=False).iloc[0]
        with col4:
            st.metric("🎯 Best Differential", 
                     f"{best_diff['web_name']}", 
                     f"{best_diff['selected_by_percent']:.1f}%")
    
    st.markdown("---")
    
    # Value categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💎 Best Value Players (Season):**")
        value_players = season_df.sort_values('value_season', ascending=False).head(15)
        value_table = value_players[
            ['web_name', 'team', 'position', 'value_season', 'total_points', 'cost', 'selected_by_percent']
        ].copy()
        value_table.columns = ['Player', 'Team', 'Pos', 'Value', 'Total Pts', 'Cost (£m)', 'Ownership (%)']
        
        styled_value = value_table.style.format({
            'Value': '{:.1f}',
            'Total Pts': '{:.0f}',
            'Cost (£m)': '£{:.1f}m',
            'Ownership (%)': '{:.1f}%'
        }).background_gradient(subset=['Value'], cmap='RdYlGn')
        
        st.dataframe(styled_value, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**💰 Budget Options (Under £6.0m):**")
        budget_options = season_df[season_df['cost'] <= 6.0].sort_values('total_points', ascending=False).head(15)
        
        if len(budget_options) > 0:
            budget_table = budget_options[
                ['web_name', 'team', 'position', 'total_points', 'form', 'cost', 'minutes']
            ].copy()
            budget_table.columns = ['Player', 'Team', 'Pos', 'Total Pts', 'Form', 'Cost (£m)', 'Minutes']
            
            styled_budget = budget_table.style.format({
                'Total Pts': '{:.0f}',
                'Form': '{:.1f}',
                'Cost (£m)': '£{:.1f}m',
                'Minutes': '{:.0f}'
            }).background_gradient(subset=['Total Pts'], cmap='RdYlGn')
            
            st.dataframe(styled_budget, use_container_width=True, hide_index=True)
        else:
            st.info("No budget players found under £6.0m")
    
    # Differential picks
    st.markdown("**🎯 Differential Picks (Under 5% Ownership):**")
    differential_picks = season_df[season_df['selected_by_percent'] <= 5.0].sort_values('total_points', ascending=False).head(15)
    
    if len(differential_picks) > 0:
        diff_table = differential_picks[
            ['web_name', 'team', 'position', 'total_points', 'form', 'cost', 'selected_by_percent']
        ].copy()
        diff_table.columns = ['Player', 'Team', 'Pos', 'Total Pts', 'Form', 'Cost (£m)', 'Ownership (%)']
        
        styled_diff = diff_table.style.format({
            'Total Pts': '{:.0f}',
            'Form': '{:.1f}',
            'Cost (£m)': '£{:.1f}m',
            'Ownership (%)': '{:.1f}%'
        }).background_gradient(subset=['Total Pts'], cmap='RdYlGn')
        
        st.dataframe(styled_diff, use_container_width=True, hide_index=True)
    else:
        st.info("No differential picks found under 5% ownership")
    
    # Ownership vs Points chart
    st.markdown("**📊 Ownership vs Points Analysis:**")
    
    fig = px.scatter(season_df, x='selected_by_percent', y='total_points',
                    color='position', size='cost',
                    hover_name='web_name',
                    hover_data=['team', 'cost', 'form'],
                    title="Player Ownership vs Season Points",
                    labels={'selected_by_percent': 'Ownership (%)', 'total_points': 'Total Points'})
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
