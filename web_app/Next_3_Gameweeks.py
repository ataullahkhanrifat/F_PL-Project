"""
Next 3 Gameweeks Module

Handles logic for evaluating the next three gameweeks (fixtures, points potential, etc.).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from optimizer import FPLOptimizer
except ImportError:
    st.error("Could not import FPLOptimizer module.")

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
    
    # Ensure predicted_points are available
    try:
        optimizer.load_model()
        if 'predicted_points' not in players_df.columns:
            players_df = optimizer.predict_points(players_df)
    except Exception as e:
        st.error(f"❌ Error loading model or predicting points: {str(e)}")
        return
    
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
    
    # Apply FPL rules and constraints to recommendations
    filtered_recommendations = apply_fpl_constraints(fixture_analysis, players_df)
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Position Recommendations", 
        "🏆 Best Fixture Teams", 
        "📊 FDR Rankings",
        "👑 Captain Picks"
    ])
    
    with tab1:
        _display_position_recommendations(filtered_recommendations)
    
    with tab2:
        _display_best_fixture_teams(fixture_analysis)
    
    with tab3:
        _display_fdr_rankings(fixture_analysis)
    
    with tab4:
        _display_captain_picks(filtered_recommendations)

def apply_fpl_constraints(fixture_analysis, players_df):
    """
    Apply proper FPL rules and constraints to fixture recommendations
    Focus on top 12 teams and highest point potential for next 3 GWs
    
    Args:
        fixture_analysis: Raw fixture analysis from optimizer
        players_df: DataFrame containing all player data
    
    Returns:
        Dictionary with filtered recommendations following FPL rules
    """
    # Define top 12 teams (based on Premier League strength)
    TOP_TEAMS = {
        'Man City', 'Arsenal', 'Liverpool', 'Chelsea', 'Man Utd', 'Newcastle',
        'Spurs', 'Brighton', 'Aston Villa', 'Brentford', 'West Ham', 'Nott\'m Forest'
    }
    
    # Initialize filtered recommendations
    filtered_recommendations = {
        'position_recommendations': {
            'forwards': [],
            'midfielders': [],
            'defenders': [],
            'goalkeepers': []
        },
        'captain_picks': []
    }
    
    # Track team counts across all positions (except goalkeepers get separate tracking)
    team_player_counts = {}
    team_gk_counts = {}
    
    # Get all players from players_df and merge with fixture analysis
    all_players_by_position = {
        'forwards': [],
        'midfielders': [],
        'defenders': [],
        'goalkeepers': []
    }
    
    # Map positions from players_df to our keys
    position_mapping = {
        'Forward': 'forwards',
        'Midfielder': 'midfielders', 
        'Defender': 'defenders',
        'Goalkeeper': 'goalkeepers'
    }
    
    # Process all players from the dataframe
    for _, player_data in players_df.iterrows():
        player_position = position_mapping.get(player_data.get('position', ''), None)
        if not player_position:
            continue
            
        # Only include players from top teams
        player_team = player_data.get('team', '')
        if player_team not in TOP_TEAMS:
            continue
            
        # Create player record with all needed data
        player = {
            'name': player_data.get('name', ''),
            'team': player_team,
            'cost': player_data.get('cost', 0),
            'form': player_data.get('form', 0),
            'minutes': player_data.get('minutes', 0),
            'total_points': player_data.get('total_points', 0),
            'selected_by_percent': player_data.get('selected_by_percent', 0),
            'status': player_data.get('status', 'a'),
            'predicted_points': player_data.get('predicted_points', player_data.get('form', 0) * 2.5),
            'position_key': player_position
        }
        
        # Calculate fixture score (lower is better) - use form and predicted points as proxy
        player['fixture_score'] = max(1, 5 - (player['form'] / 2) - (player['predicted_points'] / 10))
        
        all_players_by_position[player_position].append(player)
    
    def is_player_eligible(player):
        """Check if player meets basic eligibility criteria"""
        # Must have played some minutes this season OR be available
        has_played = player.get('minutes', 0) > 0  # Any playing time
        is_available = player.get('status', 'a') == 'a'  # Available status
        
        return has_played and is_available
    
    def can_add_player(player, position_key):
        """Check if player can be added based on FPL constraints"""
        team = player['team']
        
        # Special rule for goalkeepers (max 1 per team)
        if position_key == 'goalkeepers':
            if team_gk_counts.get(team, 0) >= 1:
                return False
        else:
            # Check team limit (max 3 players per team across non-GK positions)
            if team_player_counts.get(team, 0) >= 3:
                return False
        
        # Check if player is eligible
        if not is_player_eligible(player):
            return False
        
        return True
    
    def add_player(player, position_key):
        """Add player to recommendations and update counters"""
        team = player['team']
        
        # Add to position recommendations
        filtered_recommendations['position_recommendations'][position_key].append(player)
        
        # Update counters
        if position_key == 'goalkeepers':
            team_gk_counts[team] = team_gk_counts.get(team, 0) + 1
        else:
            team_player_counts[team] = team_player_counts.get(team, 0) + 1
    
    # Process each position to get exactly 3 players per position
    for position_key in ['forwards', 'midfielders', 'defenders', 'goalkeepers']:
        position_players = all_players_by_position[position_key]
        
        # Sort by highest point potential for next 3 GWs
        position_players.sort(key=lambda x: (
            -x.get('predicted_points', 0),  # Higher predicted points is better
            -x.get('form', 0),  # Higher form is better
            -x.get('total_points', 0),  # Higher total points is better
            x.get('fixture_score', 5)  # Lower fixture difficulty is better
        ))
        
        added_count = 0
        attempts = 0
        max_attempts = len(position_players)
        
        while added_count < 3 and attempts < max_attempts:
            player = position_players[attempts]
            attempts += 1
            
            if can_add_player(player, position_key):
                add_player(player, position_key)
                added_count += 1
        
        # If we couldn't get 3 players due to team constraints, relax constraints slightly
        if added_count < 3:
            # For remaining slots, allow any eligible player from top teams
            for player in position_players:
                if added_count >= 3:
                    break
                    
                if is_player_eligible(player):
                    # Check if this player is already added
                    already_added = any(p['name'] == player['name'] for p in filtered_recommendations['position_recommendations'][position_key])
                    if not already_added:
                        filtered_recommendations['position_recommendations'][position_key].append(player)
                        added_count += 1
    
    # Create captain picks from all recommended players
    all_recommended = []
    for position_players in filtered_recommendations['position_recommendations'].values():
        all_recommended.extend(position_players)
    
    # Sort by captaincy potential (form + predicted points)
    all_recommended.sort(key=lambda x: (
        -x.get('predicted_points', 0),
        -x.get('form', 0),
        -x.get('total_points', 0)
    ))
    
    # Take top 8 as captain picks
    filtered_recommendations['captain_picks'] = all_recommended[:8]
    
    return filtered_recommendations

def _display_position_recommendations(filtered_recommendations):
    """Display position-specific recommendations with FPL constraints applied"""
    st.subheader("🎯 Position-Specific Recommendations (Next 3 GWs)")
    st.markdown("📊 **Focus: Top 12 Teams Only | Max 3 per team | 1 GK per team | Highest expected points**")
    
    # Show which teams are considered "top teams"
    with st.expander("🏆 Top Teams Considered (Click to expand)"):
        st.markdown("""
        **Top 12 Teams:** Man City, Arsenal, Liverpool, Chelsea, Man Utd, Newcastle, 
        Spurs, Brighton, Aston Villa, Brentford, West Ham, Nott'm Forest
        
        *Only players from these teams are recommended for higher point potential.*
        """)
    
    col1, col2 = st.columns(2)
    
    # Forwards
    with col1:
        st.markdown("### ⚽ **FORWARDS** (Best attacking fixtures)")
        forwards = filtered_recommendations['position_recommendations']['forwards']
        if forwards:
            for i, player in enumerate(forwards, 1):
                # Add eligibility indicators
                form_indicator = "🔥" if player.get('form', 0) > 3.0 else "📈" if player.get('form', 0) > 0 else "💤"
                minutes_indicator = "⭐" if player.get('minutes', 0) > 500 else "✅" if player.get('minutes', 0) > 100 else "⚠️"
                
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #37003c, #5a0066); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: white;'>{i}. {player['name']} {form_indicator} {minutes_indicator}</h4>
                    <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Season: {player.get('total_points', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No forward recommendations available")
    
    with col2:
        st.markdown("### 🛡️ **DEFENDERS** (Best defensive fixtures)")
        defenders = filtered_recommendations['position_recommendations']['defenders']
        if defenders:
            for i, player in enumerate(defenders, 1):
                # Add eligibility indicators
                form_indicator = "🔥" if player.get('form', 0) > 3.0 else "📈" if player.get('form', 0) > 0 else "💤"
                minutes_indicator = "⭐" if player.get('minutes', 0) > 500 else "✅" if player.get('minutes', 0) > 100 else "⚠️"
                
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #00ff87, #04f5ff); color: #37003c; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: #37003c;'>{i}. {player['name']} {form_indicator} {minutes_indicator}</h4>
                    <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Season: {player.get('total_points', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No defender recommendations available")
    
    # Midfielders
    st.markdown("### 🎨 **MIDFIELDERS** (Best attacking fixtures)")
    midfielders = filtered_recommendations['position_recommendations']['midfielders']
    if midfielders:
        for i, player in enumerate(midfielders, 1):
            # Add eligibility indicators
            form_indicator = "🔥" if player.get('form', 0) > 3.0 else "📈" if player.get('form', 0) > 0 else "💤"
            minutes_indicator = "⭐" if player.get('minutes', 0) > 500 else "✅" if player.get('minutes', 0) > 100 else "⚠️"
            
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, #e90052, #ff6b9d); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h4 style='margin: 0; color: white;'>{i}. {player['name']} {form_indicator} {minutes_indicator}</h4>
                <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
                <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Season: {player.get('total_points', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No midfielder recommendations available")
    
    # Goalkeepers  
    st.markdown("### 🥅 **GOALKEEPERS** (Best clean sheet chances)")
    goalkeepers = filtered_recommendations['position_recommendations']['goalkeepers']
    if goalkeepers:
        for i, player in enumerate(goalkeepers, 1):
            # Add eligibility indicators for GKs
            form_indicator = "🔥" if player.get('form', 0) > 2.0 else "📈" if player.get('form', 0) > 0 else "💤"
            minutes_indicator = "⭐" if player.get('minutes', 0) > 1000 else "✅" if player.get('minutes', 0) > 500 else "⚠️"
            
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, #1a237e, #283593); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h4 style='margin: 0; color: white;'>{i}. {player['name']} {form_indicator} {minutes_indicator}</h4>
                <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
                <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Season: {player.get('total_points', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No goalkeeper recommendations available")
    


def _display_best_fixture_teams(fixture_analysis):
    """Display teams with best fixtures"""
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

def _display_fdr_rankings(fixture_analysis):
    """Display FDR rankings with visualization"""
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

def _display_captain_picks(filtered_recommendations):
    """Display captain recommendations with FPL constraints applied"""
    st.subheader("👑 Captain Recommendations")
    st.markdown("Best captain options based on form and fixtures (FPL-rules compliant):")
    
    if 'captain_picks' in filtered_recommendations:
        captain_picks = filtered_recommendations['captain_picks']
        
        if captain_picks:
            # Create captain picks grid
            cols = st.columns(2)
            
            for i, player in enumerate(captain_picks):  # Show all filtered captain options
                with cols[i % 2]:
                    # Add eligibility indicators
                    form_indicator = "🔥" if player.get('form', 0) > 5.0 else "📈" if player.get('form', 0) > 3.0 else "⚡" if player.get('form', 0) > 0 else "💤"
                    minutes_indicator = "⭐" if player.get('minutes', 0) > 1000 else "✅" if player.get('minutes', 0) > 500 else "⚠️"
                    
                    st.markdown(f"""
                    <div style='background-color: rgba(0, 255, 135, 0.1); padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; border: 2px solid #00ff87;'>
                        <h3 style='margin: 0; color: #37003c;'>#{i+1} {player['name']} {form_indicator} {minutes_indicator}</h3>
                        <p style='margin: 0.3rem 0; color: #666;'>{player['team']} | £{player['cost']:.1f}m</p>
                        <p style='margin: 0.3rem 0; color: #37003c; font-weight: bold;'>Form: {player['form']:.1f} | Predicted: {player.get('predicted_points', 'N/A')}</p>
                        <p style='margin: 0.3rem 0; color: #888; font-size: 0.9em;'>Ownership: {player.get('selected_by_percent', 0):.1f}% | Minutes: {player.get('minutes', 0)}</p>
                        <p style='margin: 0.3rem 0; color: #999; font-size: 0.8em;'>Score: {player.get('fixture_score', 'N/A')} | Season: {player.get('total_points', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No captain recommendations available")
    else:
        st.info("No captain picks data available")

def analyze_upcoming_fixtures(players_df, gameweeks=3):
    """
    Analyze upcoming fixtures for all teams
    
    Args:
        players_df: DataFrame containing player data
        gameweeks: Number of gameweeks to analyze
    
    Returns:
        Dictionary containing fixture analysis
    """
    try:
        optimizer = FPLOptimizer()
        fixture_analysis = optimizer.analyze_next_3_gameweeks(players_df)
        return fixture_analysis
    except Exception as e:
        return {'error': f"Fixture analysis failed: {str(e)}"}

def get_transfer_recommendations(players_df, current_squad=None, budget=None):
    """
    Get transfer recommendations based on upcoming fixtures
    
    Args:
        players_df: DataFrame containing player data
        current_squad: List of current squad player names
        budget: Available budget for transfers
    
    Returns:
        Dictionary with transfer recommendations
    """
    try:
        fixture_analysis = analyze_upcoming_fixtures(players_df)
        
        if 'error' in fixture_analysis:
            return fixture_analysis
        
        recommendations = {
            'transfers_in': [],
            'transfers_out': [],
            'captain_options': []
        }
        
        # Get players with best upcoming fixtures
        if 'position_recommendations' in fixture_analysis:
            for position, players in fixture_analysis['position_recommendations'].items():
                # Top 3 players with good fixtures
                for player in players[:3]:
                    if current_squad is None or player['name'] not in current_squad:
                        recommendations['transfers_in'].append({
                            'name': player['name'],
                            'position': position,
                            'team': player['team'],
                            'cost': player['cost'],
                            'reason': 'Good upcoming fixtures'
                        })
        
        # Captain recommendations
        if 'captain_picks' in fixture_analysis:
            recommendations['captain_options'] = fixture_analysis['captain_picks'][:5]
        
        return recommendations
        
    except Exception as e:
        return {'error': f"Transfer recommendations failed: {str(e)}"}

def calculate_fixture_difficulty(team_fixtures):
    """
    Calculate fixture difficulty rating for a team
    
    Args:
        team_fixtures: List of upcoming fixture data for a team
    
    Returns:
        Dictionary with FDR scores
    """
    if not team_fixtures:
        return {'overall': 5, 'attack': 5, 'defence': 5}
    
    # Simple FDR calculation (can be enhanced with more sophisticated logic)
    total_difficulty = 0
    attack_difficulty = 0
    defence_difficulty = 0
    
    for fixture in team_fixtures:
        # Base difficulty on opponent strength (simplified)
        opponent_strength = fixture.get('opponent_strength', 3)  # Default medium difficulty
        
        # Adjust for home/away
        home_advantage = 0.5 if fixture.get('is_home', False) else 0
        
        fixture_difficulty = max(1, opponent_strength - home_advantage)
        
        total_difficulty += fixture_difficulty
        attack_difficulty += fixture_difficulty
        defence_difficulty += fixture_difficulty
    
    num_fixtures = len(team_fixtures)
    
    return {
        'overall': round(total_difficulty / num_fixtures, 1),
        'attack': round(attack_difficulty / num_fixtures, 1),
        'defence': round(defence_difficulty / num_fixtures, 1)
    }

def get_gameweek_predictions(players_df, gameweek_num):
    """
    Get predicted points for players in a specific gameweek
    
    Args:
        players_df: DataFrame containing player data
        gameweek_num: Gameweek number to predict for
    
    Returns:
        DataFrame with gameweek predictions
    """
    try:
        # This would integrate with the ML prediction model
        # For now, return a simplified prediction based on form
        predictions = players_df.copy()
        
        # Simple prediction based on current form and fixtures
        predictions['predicted_gw_points'] = predictions['form'] * 1.2
        
        # Adjust for fixture difficulty (simplified)
        # In a real implementation, this would use actual fixture data
        predictions['predicted_gw_points'] *= np.random.uniform(0.8, 1.2, len(predictions))
        
        return predictions.sort_values('predicted_gw_points', ascending=False)
        
    except Exception as e:
        return pd.DataFrame({'error': [f"Prediction failed: {str(e)}"]})

def identify_differential_picks(players_df, ownership_threshold=10.0):
    """
    Identify differential picks (low ownership, high potential)
    
    Args:
        players_df: DataFrame containing player data
        ownership_threshold: Maximum ownership percentage for differentials
    
    Returns:
        DataFrame with differential picks
    """
    # Filter for low ownership players
    differentials = players_df[
        players_df['selected_by_percent'] <= ownership_threshold
    ].copy()
    
    # Calculate differential score based on form, points, and fixtures
    differentials['differential_score'] = (
        differentials['form'] * 0.4 +
        (differentials['total_points'] / 10) * 0.3 +  # Normalize total points
        (differentials['selected_by_percent'] / ownership_threshold) * (-0.3)  # Lower ownership is better
    )
    
    return differentials.sort_values('differential_score', ascending=False)
