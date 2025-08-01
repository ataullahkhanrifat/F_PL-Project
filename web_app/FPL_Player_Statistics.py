"""
FPL Player Statistics Module

Handles data retrieval and analysis for individual player statistics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

def _style_dataframe(df):
    """Apply consistent styling to dataframes for better alignment"""
    # Create a style object
    styled_df = df.style
    
    # Apply left alignment to ALL columns (both text and numeric)
    for col in df.columns:
        styled_df = styled_df.set_properties(subset=[col], **{
            'text-align': 'left',
            'white-space': 'nowrap'
        })
    
    # Apply table-wide styles with consistent left alignment
    styled_df = styled_df.set_table_styles([
        dict(selector='th', props=[
            ('font-weight', 'bold'),
            ('background-color', '#f0f2f6'),
            ('padding', '8px 12px'),
            ('border-bottom', '2px solid #ddd'),
            ('text-align', 'left')  # Force all headers to left align
        ]),
        dict(selector='td', props=[
            ('padding', '6px 12px'),
            ('border-bottom', '1px solid #e0e0e0'),
            ('text-align', 'left')  # Force all cells to left align
        ])
    ])
    
    return styled_df

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
    
    # Create comprehensive stats tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏆 Top Performers", 
        "⚽ Attack Stats", 
        "🛡️ Defense Stats",
        "📊 General Stats",
        "💎 Advanced Stats",
        "📈 Team Analysis"
    ])
    
    with tab1:
        _display_top_performers(players_df)
    
    with tab2:
        _display_attack_stats(players_df)
    
    with tab3:
        _display_defense_stats(players_df)
    
    with tab4:
        _display_general_stats(players_df)
    
    with tab5:
        _display_advanced_stats(players_df)
    
    with tab6:
        _display_team_analysis(players_df)

def _display_top_performers(players_df):
    """Display top performers section"""
    st.subheader("⭐ Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 10 Points Scorers")
        top_points = players_df.nlargest(10, 'total_points')[
            ['name', 'position', 'team', 'total_points', 'cost']
        ].reset_index(drop=True)
        top_points.index = top_points.index + 1
        st.dataframe(
            _style_dataframe(top_points), 
            use_container_width=True, 
            hide_index=False,
            column_config={
                "name": st.column_config.TextColumn("Player", width="medium"),
                "position": st.column_config.TextColumn("Position", width="small"),
                "team": st.column_config.TextColumn("Team", width="medium"),
                "total_points": st.column_config.NumberColumn("Points", width="small"),
                "cost": st.column_config.NumberColumn("Cost", width="small", format="£%.1f")
            }
        )
    
    with col2:
        st.markdown("### 📈 Top 10 Form Players")
        top_form = players_df[players_df['form'] > 0].nlargest(10, 'form')[
            ['name', 'position', 'team', 'form', 'total_points', 'cost']
        ].reset_index(drop=True)
        top_form.index = top_form.index + 1
        st.dataframe(
            _style_dataframe(top_form), 
            use_container_width=True, 
            hide_index=False,
            column_config={
                "name": st.column_config.TextColumn("Player", width="medium"),
                "position": st.column_config.TextColumn("Position", width="small"),
                "team": st.column_config.TextColumn("Team", width="medium"),
                "form": st.column_config.NumberColumn("Form", width="small", format="%.1f"),
                "total_points": st.column_config.NumberColumn("Points", width="small"),
                "cost": st.column_config.NumberColumn("Cost", width="small", format="£%.1f")
            }
        )
    
    # ICT Index Leaders
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 🎯 Top 10 ICT Index")
        if 'ict_index' in players_df.columns:
            top_ict = players_df.nlargest(10, 'ict_index')[
                ['name', 'position', 'team', 'ict_index', 'total_points']
            ].reset_index(drop=True)
            top_ict.index = top_ict.index + 1
            st.dataframe(
                _style_dataframe(top_ict), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "ict_index": st.column_config.NumberColumn("ICT Index", width="small", format="%.1f"),
                    "total_points": st.column_config.NumberColumn("Points", width="small")
                }
            )
        else:
            st.info("ICT Index data not available")
    
    with col4:
        st.markdown("### ⏱️ Top 10 Minutes Played")
        top_minutes = players_df.nlargest(10, 'minutes')[
            ['name', 'position', 'team', 'minutes', 'total_points']
        ].reset_index(drop=True)
        top_minutes.index = top_minutes.index + 1
        st.dataframe(
            _style_dataframe(top_minutes), 
            use_container_width=True, 
            hide_index=False,
            column_config={
                "name": st.column_config.TextColumn("Player", width="medium"),
                "position": st.column_config.TextColumn("Position", width="small"),
                "team": st.column_config.TextColumn("Team", width="medium"),
                "minutes": st.column_config.NumberColumn("Minutes", width="small"),
                "total_points": st.column_config.NumberColumn("Points", width="small")
            }
        )

def _display_attack_stats(players_df):
    """Display attacking statistics"""
    st.subheader("⚽ Attacking Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥅 Top 10 Goal Scorers")
        if 'goals_scored' in players_df.columns:
            top_goals = players_df[players_df['goals_scored'] > 0].nlargest(10, 'goals_scored')[
                ['name', 'position', 'team', 'goals_scored', 'total_points']
            ].reset_index(drop=True)
            top_goals.index = top_goals.index + 1
            st.dataframe(
                _style_dataframe(top_goals), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "goals_scored": st.column_config.NumberColumn("Goals", width="small"),
                    "total_points": st.column_config.NumberColumn("Points", width="small")
                }
            )
        else:
            st.info("Goals data not available")
    
    with col2:
        st.markdown("### 🎯 Top 10 Assist Providers")
        if 'assists' in players_df.columns:
            top_assists = players_df[players_df['assists'] > 0].nlargest(10, 'assists')[
                ['name', 'position', 'team', 'assists', 'total_points']
            ].reset_index(drop=True)
            top_assists.index = top_assists.index + 1
            st.dataframe(
                _style_dataframe(top_assists), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "assists": st.column_config.NumberColumn("Assists", width="small"),
                    "total_points": st.column_config.NumberColumn("Points", width="small")
                }
            )
        else:
            st.info("Assists data not available")
    
    # Goal Involvement and Minutes
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### ⚽ Goal Involvement (Goals + Assists)")
        if 'goals_scored' in players_df.columns and 'assists' in players_df.columns:
            players_with_involvement = players_df.copy()
            players_with_involvement['goal_involvement'] = players_with_involvement['goals_scored'] + players_with_involvement['assists']
            top_involvement = players_with_involvement[players_with_involvement['goal_involvement'] > 0].nlargest(10, 'goal_involvement')[
                ['name', 'position', 'team', 'goal_involvement', 'goals_scored', 'assists']
            ].reset_index(drop=True)
            top_involvement.index = top_involvement.index + 1
            st.dataframe(top_involvement, use_container_width=True, hide_index=False)
        else:
            st.info("Goal involvement data not available")
    
    with col4:
        st.markdown("### ⏱️ Minutes Per Goal/Assist")
        if 'goals_scored' in players_df.columns and 'assists' in players_df.columns and 'minutes' in players_df.columns:
            players_efficiency = players_df.copy()
            players_efficiency['goal_involvement'] = players_efficiency['goals_scored'] + players_efficiency['assists']
            players_efficiency = players_efficiency[players_efficiency['goal_involvement'] > 0].copy()
            players_efficiency['minutes_per_involvement'] = players_efficiency['minutes'] / players_efficiency['goal_involvement']
            top_efficiency = players_efficiency.nsmallest(10, 'minutes_per_involvement')[
                ['name', 'position', 'team', 'minutes_per_involvement', 'goal_involvement', 'minutes']
            ].reset_index(drop=True)
            top_efficiency['minutes_per_involvement'] = top_efficiency['minutes_per_involvement'].round(1)
            top_efficiency.index = top_efficiency.index + 1
            st.dataframe(
                _style_dataframe(top_efficiency), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "minutes_per_involvement": st.column_config.NumberColumn("Min/Goal+Assist", width="small", format="%.1f"),
                    "goal_involvement": st.column_config.NumberColumn("G+A", width="small"),
                    "minutes": st.column_config.NumberColumn("Minutes", width="small")
                }
            )
        else:
            st.info("Efficiency data not available")
    
    # Penalties
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### ❌ Penalties Missed")
        if 'penalties_missed' in players_df.columns:
            pen_missed = players_df[players_df['penalties_missed'] > 0].nlargest(10, 'penalties_missed')[
                ['name', 'position', 'team', 'penalties_missed', 'total_points']
            ].reset_index(drop=True)
            pen_missed.index = pen_missed.index + 1
            st.dataframe(pen_missed, use_container_width=True, hide_index=False)
        else:
            st.info("Penalty miss data not available")
    
    with col6:
        st.markdown("### 📊 Points Per Game")
        if 'points_per_game' in players_df.columns:
            top_ppg = players_df[players_df['points_per_game'] > 0].nlargest(10, 'points_per_game')[
                ['name', 'position', 'team', 'points_per_game', 'total_points', 'minutes']
            ].reset_index(drop=True)
            top_ppg.index = top_ppg.index + 1
            st.dataframe(top_ppg, use_container_width=True, hide_index=False)
        else:
            st.info("Points per game data not available")

def _display_defense_stats(players_df):
    """Display defensive statistics"""
    st.subheader("🛡️ Defensive Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚫 Most Clean Sheets")
        if 'clean_sheets' in players_df.columns:
            top_cs = players_df[players_df['clean_sheets'] > 0].nlargest(10, 'clean_sheets')[
                ['name', 'position', 'team', 'clean_sheets', 'total_points']
            ].reset_index(drop=True)
            top_cs.index = top_cs.index + 1
            st.dataframe(
                _style_dataframe(top_cs), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "clean_sheets": st.column_config.NumberColumn("Clean Sheets", width="small"),
                    "total_points": st.column_config.NumberColumn("Total Points", width="small")
                }
            )
        else:
            st.info("Clean sheets data not available")
    
    with col2:
        st.markdown("### 🥅 Most Saves (Goalkeepers)")
        if 'saves' in players_df.columns:
            gk_saves = players_df[
                (players_df['position'] == 'Goalkeeper') & 
                (players_df['saves'] > 0)
            ].nlargest(10, 'saves')[
                ['name', 'team', 'saves', 'clean_sheets', 'total_points']
            ].reset_index(drop=True)
            gk_saves.index = gk_saves.index + 1
            st.dataframe(gk_saves, use_container_width=True, hide_index=False)
        else:
            st.info("Saves data not available")
    
    # Penalty Stats
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 🚫 Penalty Saves")
        if 'penalties_saved' in players_df.columns:
            pen_saves = players_df[players_df['penalties_saved'] > 0].nlargest(10, 'penalties_saved')[
                ['name', 'position', 'team', 'penalties_saved', 'total_points']
            ].reset_index(drop=True)
            pen_saves.index = pen_saves.index + 1
            st.dataframe(pen_saves, use_container_width=True, hide_index=False)
        else:
            st.info("Penalty saves data not available")
    
    with col4:
        st.markdown("### ❌ Own Goals")
        if 'own_goals' in players_df.columns:
            own_goals = players_df[players_df['own_goals'] > 0].nlargest(10, 'own_goals')[
                ['name', 'position', 'team', 'own_goals', 'total_points']
            ].reset_index(drop=True)
            own_goals.index = own_goals.index + 1
            st.dataframe(own_goals, use_container_width=True, hide_index=False)
        else:
            st.info("Own goals data not available")
    
    # Goals Conceded
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### 🥅 Goals Conceded")
        if 'goals_conceded' in players_df.columns:
            goals_conceded = players_df[players_df['goals_conceded'] > 0].nlargest(10, 'goals_conceded')[
                ['name', 'position', 'team', 'goals_conceded', 'minutes']
            ].reset_index(drop=True)
            goals_conceded.index = goals_conceded.index + 1
            st.dataframe(goals_conceded, use_container_width=True, hide_index=False)
        else:
            st.info("Goals conceded data not available")

def _display_general_stats(players_df):
    """Display general statistics"""
    st.subheader("📊 General Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟨 Most Yellow Cards")
        if 'yellow_cards' in players_df.columns:
            top_yellows = players_df[players_df['yellow_cards'] > 0].nlargest(10, 'yellow_cards')[
                ['name', 'position', 'team', 'yellow_cards', 'total_points']
            ].reset_index(drop=True)
            top_yellows.index = top_yellows.index + 1
            st.dataframe(
                _style_dataframe(top_yellows), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "yellow_cards": st.column_config.NumberColumn("Yellow Cards", width="small"),
                    "total_points": st.column_config.NumberColumn("Total Points", width="small")
                }
            )
        else:
            st.info("Yellow cards data not available")
    
    with col2:
        st.markdown("### 🟥 Most Red Cards")
        if 'red_cards' in players_df.columns:
            top_reds = players_df[players_df['red_cards'] > 0].nlargest(10, 'red_cards')[
                ['name', 'position', 'team', 'red_cards', 'total_points']
            ].reset_index(drop=True)
            top_reds.index = top_reds.index + 1
            st.dataframe(
                _style_dataframe(top_reds), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "red_cards": st.column_config.NumberColumn("Red Cards", width="small"),
                    "total_points": st.column_config.NumberColumn("Total Points", width="small")
                }
            )
        else:
            st.info("Red cards data not available")
    
    # Bonus and Ownership
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 🎁 Most Bonus Points")
        if 'bonus' in players_df.columns:
            top_bonus = players_df[players_df['bonus'] > 0].nlargest(10, 'bonus')[
                ['name', 'position', 'team', 'bonus', 'total_points']
            ].reset_index(drop=True)
            top_bonus.index = top_bonus.index + 1
            st.dataframe(
                _style_dataframe(top_bonus), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "bonus": st.column_config.NumberColumn("Bonus", width="small"),
                    "total_points": st.column_config.NumberColumn("Total Points", width="small")
                }
            )
        else:
            st.info("Bonus points data not available")
    
    with col4:
        st.markdown("### 📈 Highest Ownership %")
        if 'selected_by_percent' in players_df.columns:
            top_owned = players_df.nlargest(10, 'selected_by_percent')[
                ['name', 'position', 'team', 'selected_by_percent', 'total_points']
            ].reset_index(drop=True)
            top_owned.index = top_owned.index + 1
            st.dataframe(
                _style_dataframe(top_owned), 
                use_container_width=True, 
                hide_index=False,
                column_config={
                    "name": st.column_config.TextColumn("Player", width="medium"),
                    "position": st.column_config.TextColumn("Position", width="small"),
                    "team": st.column_config.TextColumn("Team", width="medium"),
                    "selected_by_percent": st.column_config.NumberColumn("Selected By %", width="small", format="%.1f%%"),
                    "total_points": st.column_config.NumberColumn("Total Points", width="small")
                }
            )
        else:
            st.info("Ownership data not available")
    
    # Advanced Stats
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### 🎯 Highest BPS (Bonus Point System)")
        if 'bps' in players_df.columns:
            top_bps = players_df[players_df['bps'] > 0].nlargest(10, 'bps')[
                ['name', 'position', 'team', 'bps', 'bonus']
            ].reset_index(drop=True)
            top_bps.index = top_bps.index + 1
            st.dataframe(top_bps, use_container_width=True, hide_index=False)
        else:
            st.info("BPS data not available")
    
    with col6:
        st.markdown("### 🎖️ Best Value Players")
        if 'cost_efficiency' in players_df.columns:
            top_value = players_df[players_df['total_points'] > 50].nlargest(10, 'cost_efficiency')[
                ['name', 'position', 'team', 'cost_efficiency', 'cost', 'total_points']
            ].reset_index(drop=True)
            top_value.index = top_value.index + 1
            st.dataframe(top_value, use_container_width=True, hide_index=False)
        else:
            st.info("Value efficiency data not available")

def _display_advanced_stats(players_df):
    """Display advanced statistics and insights"""
    st.subheader("💎 Advanced Statistics & Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Highest Influence")
        if 'influence' in players_df.columns:
            top_influence = players_df[players_df['influence'] > 0].nlargest(10, 'influence')[
                ['name', 'position', 'team', 'influence', 'total_points']
            ].reset_index(drop=True)
            top_influence.index = top_influence.index + 1
            st.dataframe(top_influence, use_container_width=True, hide_index=False)
        else:
            st.info("Influence data not available")
    
    with col2:
        st.markdown("### 🧠 Highest Creativity")
        if 'creativity' in players_df.columns:
            top_creativity = players_df[players_df['creativity'] > 0].nlargest(10, 'creativity')[
                ['name', 'position', 'team', 'creativity', 'assists']
            ].reset_index(drop=True)
            top_creativity.index = top_creativity.index + 1
            st.dataframe(top_creativity, use_container_width=True, hide_index=False)
        else:
            st.info("Creativity data not available")
    
    # Threat and Transfers
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### ⚡ Highest Threat")
        if 'threat' in players_df.columns:
            top_threat = players_df[players_df['threat'] > 0].nlargest(10, 'threat')[
                ['name', 'position', 'team', 'threat', 'goals_scored']
            ].reset_index(drop=True)
            top_threat.index = top_threat.index + 1
            st.dataframe(top_threat, use_container_width=True, hide_index=False)
        else:
            st.info("Threat data not available")
    
    with col4:
        st.markdown("### 📈 Most Transferred In")
        if 'transfers_in' in players_df.columns:
            top_transfers_in = players_df[players_df['transfers_in'] > 0].nlargest(10, 'transfers_in')[
                ['name', 'position', 'team', 'transfers_in', 'selected_by_percent']
            ].reset_index(drop=True)
            top_transfers_in.index = top_transfers_in.index + 1
            st.dataframe(top_transfers_in, use_container_width=True, hide_index=False)
        else:
            st.info("Transfer data not available")
    
    # Value insights
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### 💰 Best Value Form")
        if 'value_form' in players_df.columns:
            top_value_form = players_df[players_df['value_form'] > 0].nlargest(10, 'value_form')[
                ['name', 'position', 'team', 'value_form', 'form', 'cost']
            ].reset_index(drop=True)
            top_value_form.index = top_value_form.index + 1
            st.dataframe(top_value_form, use_container_width=True, hide_index=False)
        else:
            st.info("Value form data not available")
    
    with col6:
        st.markdown("### 🏆 Best Value Season")
        if 'value_season' in players_df.columns:
            top_value_season = players_df[players_df['value_season'] > 0].nlargest(10, 'value_season')[
                ['name', 'position', 'team', 'value_season', 'total_points', 'cost']
            ].reset_index(drop=True)
            top_value_season.index = top_value_season.index + 1
            st.dataframe(top_value_season, use_container_width=True, hide_index=False)
        else:
            st.info("Value season data not available")
    
    # Differential Players
    st.markdown("### 💎 Differential Players (Low Ownership, High Points)")
    differentials = get_differential_players(players_df, max_ownership=10, min_points=50)
    if not differentials.empty:
        differentials.index = differentials.index + 1
        st.dataframe(differentials, use_container_width=True, hide_index=False)
    else:
        st.info("No suitable differential players found")
    
    # Budget Options
    st.markdown("### 💰 Budget Options (Under £6.0m, 30+ Points)")
    budget_options = get_budget_options(players_df, max_cost=6.0, min_points=30)
    if not budget_options.empty:
        budget_options.index = budget_options.index + 1
        st.dataframe(budget_options, use_container_width=True, hide_index=False)
    else:
        st.info("No suitable budget options found")

def _display_team_analysis(players_df):
    """Display team analysis"""
    st.subheader("📈 Team Analysis")
    
    # Team performance summary
    team_stats = players_df.groupby('team').agg({
        'total_points': 'sum',
        'goals_scored': 'sum',
        'assists': 'sum',
        'cost': 'mean',
        'minutes': 'sum',
        'name': 'count'
    }).round(2)
    
    team_stats.columns = ['Total Points', 'Goals', 'Assists', 'Avg Cost', 'Total Minutes', 'Player Count']
    team_stats = team_stats.sort_values('Total Points', ascending=False)
    
    st.markdown("### 🏆 Team Performance Summary")
    st.dataframe(
        _style_dataframe(team_stats), 
        use_container_width=True,
        column_config={
            "team": st.column_config.TextColumn("Team", width="medium"),
            "Total Points": st.column_config.NumberColumn("Total Points", width="small", format="%d"),
            "Goals": st.column_config.NumberColumn("Goals", width="small", format="%d"),
            "Assists": st.column_config.NumberColumn("Assists", width="small", format="%d"),
            "Avg Cost": st.column_config.NumberColumn("Avg Cost", width="small", format="£%.2f"),
            "Total Minutes": st.column_config.NumberColumn("Total Minutes", width="small", format="%d"),
            "Player Count": st.column_config.NumberColumn("Player Count", width="small", format="%d")
        }
    )
    
    # Additional team insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥅 Most Goals by Team")
        goals_by_team = players_df.groupby('team')['goals_scored'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(goals_by_team)
    
    with col2:
        st.markdown("### 🎯 Most Assists by Team")
        assists_by_team = players_df.groupby('team')['assists'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(assists_by_team)

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
    
    # Cost efficiency (points per million)
    df['cost_efficiency'] = df['total_points'] / df['cost']
    
    # Goals + Assists
    if 'goals_scored' in df.columns and 'assists' in df.columns:
        df['goal_involvement'] = df['goals_scored'] + df['assists']
    
    # Value rating (combination of points per cost and form)
    df['value_rating'] = (df['points_per_cost'] * 0.7) + (df['form_per_cost'] * 0.3)
    
    # Minutes per game
    df['minutes_per_game'] = np.where(
        df['minutes'] > 0,
        df['minutes'] / (df['minutes'] / 90).round(),
        0
    )
    
    # Expected vs actual performance ratios
    if 'expected_goals' in df.columns and 'goals_scored' in df.columns:
        df['goal_conversion'] = np.where(
            df['expected_goals'] > 0,
            df['goals_scored'] / df['expected_goals'],
            0
        )
    
    if 'expected_assists' in df.columns and 'assists' in df.columns:
        df['assist_conversion'] = np.where(
            df['expected_assists'] > 0,
            df['assists'] / df['expected_assists'],
            0
        )
    
    return df

def get_differential_players(players_df, max_ownership=15, min_points=50):
    """
    Find differential players (low ownership, high points)
    
    Args:
        players_df: DataFrame containing player data
        max_ownership: Maximum ownership percentage for differentials
        min_points: Minimum points required
    
    Returns:
        DataFrame with differential players
    """
    if 'selected_by_percent' not in players_df.columns:
        return pd.DataFrame()
    
    differentials = players_df[
        (players_df['selected_by_percent'] <= max_ownership) &
        (players_df['total_points'] >= min_points)
    ].sort_values('total_points', ascending=False)
    
    return differentials[
        ['name', 'position', 'team', 'total_points', 'selected_by_percent', 'cost']
    ].head(10)

def get_budget_options(players_df, max_cost=6.0, min_points=30):
    """
    Find budget-friendly options
    
    Args:
        players_df: DataFrame containing player data
        max_cost: Maximum cost for budget options
        min_points: Minimum points required
    
    Returns:
        DataFrame with budget options
    """
    budget_players = players_df[
        (players_df['cost'] <= max_cost) &
        (players_df['total_points'] >= min_points)
    ].sort_values('total_points', ascending=False)
    
    return budget_players[
        ['name', 'position', 'team', 'total_points', 'cost', 'form']
    ].head(10)

def get_rotation_risks(players_df, min_cost=8.0):
    """
    Identify potential rotation risks (expensive players with low minutes)
    
    Args:
        players_df: DataFrame containing player data
        min_cost: Minimum cost to be considered expensive
    
    Returns:
        DataFrame with rotation risk players
    """
    expensive_players = players_df[players_df['cost'] >= min_cost].copy()
    
    if expensive_players.empty:
        return pd.DataFrame()
    
    # Calculate minutes per gameweek (assuming 38 gameweeks)
    expensive_players['minutes_per_gw'] = expensive_players['minutes'] / 38
    
    rotation_risks = expensive_players[
        expensive_players['minutes_per_gw'] < 60  # Less than 60 minutes per gameweek
    ].sort_values('cost', ascending=False)
    
    return rotation_risks[
        ['name', 'position', 'team', 'cost', 'minutes', 'minutes_per_gw', 'total_points']
    ].head(10)
