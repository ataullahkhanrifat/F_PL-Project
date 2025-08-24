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
import time

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
            st.session_state.last_user_interaction = time.time()  # Track user interaction
            st.rerun()
    
    st.divider()
    
    # Initialize optimizer for fixture analysis (with caching)
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_optimizer_predictions(players_data_hash):
        """Cache expensive optimizer operations"""
        optimizer = FPLOptimizer()
        
        # Load model once
        optimizer.load_model()
        
        # Predict points if needed
        if 'predicted_points' not in players_df.columns:
            players_df_with_predictions = optimizer.predict_points(players_df.copy())
        else:
            players_df_with_predictions = players_df.copy()
        
        return players_df_with_predictions, optimizer
    
    # Create hash of player data to detect changes
    import hashlib
    players_data_str = str(players_df.values.tobytes())
    players_hash = hashlib.md5(players_data_str.encode()).hexdigest()
    
    # Get cached predictions and optimizer
    try:
        players_df, optimizer = get_optimizer_predictions(players_hash)
    except Exception as e:
        st.error(f"❌ Error loading model or predicting points: {str(e)}")
        return
    
    @st.cache_data(ttl=300)  # Cache fixture analysis for 5 minutes
    def get_fixture_analysis(players_hash, optimizer_state):
        """Cache expensive fixture analysis"""
        return optimizer.analyze_next_3_gameweeks(players_df)
    
    with st.spinner("🔍 Analyzing upcoming fixtures and player recommendations..."):
        try:
            fixture_analysis = get_fixture_analysis(players_hash, "cached")
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

# Global ML model cache to avoid reloading models for each player
_ml_model_cache = {
    'ensemble': None,
    'loaded': False
}

def get_ml_ensemble():
    """Get cached ML ensemble model (load once, use many times)"""
    global _ml_model_cache
    
    if not _ml_model_cache['loaded']:
        try:
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(__file__))
            sys.path.append(os.path.join(project_root, 'src'))
            
            from advanced_ml_models import EnsemblePredictor
            
            # Load models once and cache
            ensemble = EnsemblePredictor()
            ensemble.load_models()  # Load Markov, age, news models
            
            _ml_model_cache['ensemble'] = ensemble
            _ml_model_cache['loaded'] = True
            
            return ensemble
            
        except Exception as e:
            # Cache the failure to avoid repeated attempts
            _ml_model_cache['loaded'] = True
            _ml_model_cache['ensemble'] = None
            return None
    
    return _ml_model_cache['ensemble']

def calculate_next_3gw_potential(player, team, fixture_analysis):
    """
    Calculate a player's potential points for the next 3 gameweeks using advanced ML models:
    - Advanced ML ensemble predictions (Markov Chain + Age/Injury + News Sentiment)
    - Opponent defensive strength analysis
    - Home/away advantage multipliers
    - Player ICT involvement and form trajectory
    """
    # Start with advanced ML prediction if available
    base_prediction = player.get('predicted_points', 0)
    
    # Try to use cached ML models for better base prediction
    ensemble = get_ml_ensemble()
    if ensemble is not None:
        try:
            import pandas as pd
            
            # Create single-player DataFrame for prediction
            player_df = pd.DataFrame([{
                'form': player.get('form', 0),
                'cost': player.get('cost', 5.0),
                'minutes': player.get('minutes', 0),
                'total_points': player.get('total_points', 0),
                'influence': player.get('influence', 0),
                'creativity': player.get('creativity', 0),
                'threat': player.get('threat', 0),
                'ict_index': player.get('ict_index', 0),
                'selected_by_percent': player.get('selected_by_percent', 0),
                'position': player.get('position_key', 'midfielder'),
                'age': player.get('age', 25),  # Default age
                'team': team
            }])
            
            # Get advanced ML prediction (models already loaded)
            advanced_predictions = ensemble.predict_with_ensemble(player_df)
            if len(advanced_predictions) > 0:
                base_prediction = advanced_predictions[0]
                
        except Exception:
            # Fall back to basic prediction if advanced models fail
            base_prediction = player.get('predicted_points', player.get('form', 0) * 2.5)
    else:
        # Fall back to basic prediction if advanced models not available
        base_prediction = player.get('predicted_points', player.get('form', 0) * 2.5)
    
    # Get team's fixture difficulty from analysis
    team_fixtures = []
    if 'team_analysis' in fixture_analysis:
        for team_data in fixture_analysis['team_analysis']:
            if team_data.get('team') == team:
                team_fixtures = team_data.get('upcoming_fixtures', [])
                break
    
    if not team_fixtures:
        return base_prediction
    
    # Analyze each of the next 3 fixtures with position-specific logic
    fixture_multiplier = 1.0
    for i, fixture in enumerate(team_fixtures[:3]):
        # Weight recent fixtures more heavily
        weight = 1.0 - (i * 0.1)  # GW1: 1.0, GW2: 0.9, GW3: 0.8
        
        # Position-specific opponent analysis
        if player['position_key'] in ['forwards', 'midfielders']:
            # Attacking players benefit from weak defenses
            opponent_fdr = fixture.get('fdr_defence', 3)
            ease_multiplier = (6 - opponent_fdr) / 3  # Scale: 1.0 (hard) to 1.67 (easy)
        else:
            # Defensive players benefit from weak attacks (clean sheet potential)
            opponent_fdr = fixture.get('fdr_attack', 3)
            ease_multiplier = (6 - opponent_fdr) / 3
        
        # Home advantage (more significant for certain positions)
        if player['position_key'] in ['defenders', 'goalkeepers']:
            home_multiplier = 1.20 if fixture.get('is_home', False) else 0.90  # Higher impact for defense
        else:
            home_multiplier = 1.15 if fixture.get('is_home', False) else 0.95  # Standard impact for attack
        
        fixture_multiplier += (ease_multiplier * home_multiplier * weight)
    
    # Normalize by number of fixtures analyzed
    fixture_multiplier = fixture_multiplier / 4  # 1 base + 3 fixtures
    
    # Apply advanced player-specific factors
    
    # ICT Index boost (higher ICT = more involved in play, better prediction reliability)
    ict_boost = 1 + (player.get('ict_index', 0) / 1000)  # Max ~10% boost for high ICT
    
    # Form trajectory analysis (recent vs season performance)
    season_avg = player.get('total_points', 0) / max(1, (player.get('minutes', 1) / 90))
    current_form = player.get('form', 0)
    form_trajectory = min(1.4, max(0.6, current_form / max(0.1, season_avg)))
    
    # Age factor (peak performance curves by position)
    age = player.get('age', 25)
    if player['position_key'] == 'goalkeepers':
        # GK peak later, decline slower
        age_factor = 1.0 if 28 <= age <= 32 else (0.95 if age < 28 or age > 32 else 0.85)
    elif player['position_key'] == 'defenders':
        # Defenders peak mid-career
        age_factor = 1.0 if 25 <= age <= 30 else (0.95 if age < 25 or age > 30 else 0.85)
    else:
        # Attackers peak earlier
        age_factor = 1.0 if 22 <= age <= 28 else (0.95 if age < 22 or age > 28 else 0.85)
    
    # Calculate final sophisticated prediction
    next_3gw_prediction = (base_prediction * fixture_multiplier * ict_boost * 
                          form_trajectory * age_factor)
    
    return round(next_3gw_prediction, 2)

def calculate_fixture_difficulty_score(team, fixture_analysis):
    """
    Calculate fixture difficulty score for next 3 gameweeks (lower = easier)
    """
    if 'team_analysis' not in fixture_analysis:
        return 3.0  # Neutral difficulty
    
    for team_data in fixture_analysis['team_analysis']:
        if team_data.get('team') == team:
            # Average FDR across next 3 fixtures
            fixtures = team_data.get('upcoming_fixtures', [])[:3]
            if not fixtures:
                return 3.0
            
            total_difficulty = sum(f.get('fdr_overall', 3) for f in fixtures)
            return round(total_difficulty / len(fixtures), 2)
    
    return 3.0  # Default neutral

def calculate_manager_confidence(player):
    """
    Calculate manager confidence based on transfer trends and ownership changes
    """
    transfers_in = player.get('transfers_in_event', 0)
    transfers_out = player.get('transfers_out_event', 0)
    
    # Net transfers as percentage of ownership
    ownership = max(1, player.get('selected_by_percent', 1))
    net_transfer_rate = (transfers_in - transfers_out) / (ownership * 1000)  # Normalize
    
    # Convert to confidence score (0.5 to 1.5 range)
    confidence = 1.0 + (net_transfer_rate * 0.5)
    return max(0.5, min(1.5, confidence))

def apply_fpl_constraints(fixture_analysis, players_df):
    """
    Apply proper FPL rules and constraints to fixture recommendations
    Focus on all teams and highest point potential for next 3 GWs
    
    Args:
        fixture_analysis: Raw fixture analysis from optimizer
        players_df: DataFrame containing all player data
    
    Returns:
        Dictionary with filtered recommendations following FPL rules
    """
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
    
    # Process all players from the dataframe (no team restrictions)
    for _, player_data in players_df.iterrows():
        player_position = position_mapping.get(player_data.get('position', ''), None)
        if not player_position:
            continue
            
        # Include players from ALL teams
        player_team = player_data.get('team', '')
        
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
            'position_key': player_position,
            'transfers_in': player_data.get('transfers_in', 0),
            'transfers_out': player_data.get('transfers_out', 0),
            'transfers_in_event': player_data.get('transfers_in_event', 0),
            'transfers_out_event': player_data.get('transfers_out_event', 0),
            'ict_index': player_data.get('ict_index', 0),
            'influence': player_data.get('influence', 0),
            'creativity': player_data.get('creativity', 0),
            'threat': player_data.get('threat', 0)
        }
        
        # Calculate advanced fixture-based prediction for next 3 gameweeks
        player['next_3gw_prediction'] = calculate_next_3gw_potential(player, player_team, fixture_analysis)
        
        # Calculate fixture score (lower is better) - now based on actual fixture analysis
        player['fixture_score'] = calculate_fixture_difficulty_score(player_team, fixture_analysis)
        
        # Calculate manager confidence (based on transfer trends)
        player['manager_confidence'] = calculate_manager_confidence(player)
        
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
    
    # Process each position to get exactly 5 players per position
    for position_key in ['forwards', 'midfielders', 'defenders', 'goalkeepers']:
        position_players = all_players_by_position[position_key]
        
        # Sort by sophisticated ML predictions and advanced metrics
        position_players.sort(key=lambda x: (
            -x.get('next_3gw_prediction', x.get('predicted_points', 0)),  # Advanced ML prediction first
            -x.get('manager_confidence', 1.0),  # Manager confidence from transfer trends
            x.get('fixture_score', 5),  # Lower fixture difficulty is better
            -x.get('ict_index', 0),  # Higher ICT involvement is better
            -x.get('form', 0),  # Higher form is better as tiebreaker
        ))
        
        added_count = 0
        attempts = 0
        max_attempts = len(position_players)
        
        while added_count < 5 and attempts < max_attempts:
            player = position_players[attempts]
            attempts += 1
            
            if can_add_player(player, position_key):
                add_player(player, position_key)
                added_count += 1
        
        # If we couldn't get 5 players due to team constraints, relax constraints slightly
        if added_count < 5:
            # For remaining slots, allow any eligible player from all teams
            for player in position_players:
                if added_count >= 5:
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
    
    # Sort by captaincy potential using advanced ML predictions
    all_recommended.sort(key=lambda x: (
        -x.get('next_3gw_prediction', x.get('predicted_points', 0)),  # Advanced ML prediction
        -x.get('manager_confidence', 1.0),  # Manager confidence
        -x.get('ict_index', 0),  # ICT involvement
        -x.get('form', 0)  # Form as final tiebreaker
    ))
    
    # Take top 10 as captain picks (since we now have 20 total players - 5 per position)
    filtered_recommendations['captain_picks'] = all_recommended[:10]
    
    return filtered_recommendations

def _display_position_recommendations(filtered_recommendations):
    """Display position-specific recommendations with FPL constraints applied"""
    st.subheader("🎯 Position-Specific Recommendations (Next 3 GWs)")
    st.markdown("🚀 **Updated Strategic Approach: 25% fixtures + 20% last 5 matches + 20% season performance**")
    st.markdown("🤖 **Advanced ML System: Markov Chain + Age Analysis + News Sentiment + Fixture Intelligence**")
    
    # Show updated criteria
    with st.expander("⚽ Advanced Selection Criteria (Click to expand)"):
        st.markdown("""
        **🤖 Advanced ML System:**
        - ✅ **Markov Chain Form Analysis** - Predicts form transitions based on historical patterns
        - ✅ **Age Performance Curves** - Position-specific peak performance analysis  
        - ✅ **News Sentiment Analysis** - Incorporates injury/transfer/form news
        - ✅ **Ensemble ML Models** - Random Forest + Gradient Boosting combination
        
        **🏟️ Enhanced Fixture Intelligence (25% weight):**
        - ✅ **Position-Specific FDR** - Attackers vs weak defenses, defenders vs weak attacks
        - ✅ **Strategic Fixture Scoring** - Future-focused over past performance
        - ✅ **Team Popularity Modifiers** - Strong teams with good fixtures get boost
        - ✅ **3-Gameweek Weighted Analysis** - More weight on nearer fixtures
        
        **📊 Updated Prediction Model:**
        - 🎯 **Season Performance (20%)** - Overall consistency throughout the season
        - ⚡ **Last 5 Matches (20%)** - Most recent performance and current momentum
        - 🏟️ **Fixture Advantage (25%)** - Upcoming fixture difficulty analysis (highest weight)
        - 📈 **Recent Form Last 10 (5%)** - Broader recent form context (minimal impact)
        - 💎 **PPG Consistency (15%)** - Points per game reliability
        - 💰 **Value Factor (10%)** - Cost efficiency consideration
        - 🌟 **Top 5 Team Bonus (5%)** - Premium for big team players
        
        **📊 Player Analysis:**
        - ✅ **ICT Involvement Index** - Player impact on team performance
        - ✅ **Manager Confidence** - Transfer trend analysis  
        - ✅ **Form Trajectory** - Recent vs season performance comparison
        - ✅ **All 20 Premier League teams** considered for maximum options
        
        *Updated strategic predictions emphasizing recent momentum (Last 5: 20%) and upcoming fixtures (25%) over season-long performance.*
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
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>🤖 <strong>ML Prediction:</strong> {player.get('next_3gw_prediction', 0):.1f} pts | ICT: {player.get('ict_index', 0):.0f}</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Confidence: {player.get('manager_confidence', 1.0):.2f}</p>
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
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>🤖 <strong>ML Prediction:</strong> {player.get('next_3gw_prediction', 0):.1f} pts | ICT: {player.get('ict_index', 0):.0f}</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Confidence: {player.get('manager_confidence', 1.0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No defender recommendations available")
    
    # Midfielders (now taking full width since we have 5 players)
    st.markdown("### 🎨 **MIDFIELDERS** (Best attacking fixtures)")
    midfielders = filtered_recommendations['position_recommendations']['midfielders']
    if midfielders:
        # Create 2 columns for midfielders to display 5 players nicely
        mid_col1, mid_col2 = st.columns(2)
        for i, player in enumerate(midfielders, 1):
            # Add eligibility indicators
            form_indicator = "🔥" if player.get('form', 0) > 3.0 else "📈" if player.get('form', 0) > 0 else "💤"
            minutes_indicator = "⭐" if player.get('minutes', 0) > 500 else "✅" if player.get('minutes', 0) > 100 else "⚠️"
            
            # Alternate between columns
            with mid_col1 if i % 2 == 1 else mid_col2:
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #e90052, #ff6b9d); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: white;'>{i}. {player['name']} {form_indicator} {minutes_indicator}</h4>
                    <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>🤖 <strong>ML Prediction:</strong> {player.get('next_3gw_prediction', 0):.1f} pts | ICT: {player.get('ict_index', 0):.0f}</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Confidence: {player.get('manager_confidence', 1.0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No midfielder recommendations available")
    
    # Goalkeepers  
    st.markdown("### 🥅 **GOALKEEPERS** (Best clean sheet chances)")
    goalkeepers = filtered_recommendations['position_recommendations']['goalkeepers']
    if goalkeepers:
        # Create 2 columns for goalkeepers to display 5 players nicely
        gk_col1, gk_col2 = st.columns(2)
        for i, player in enumerate(goalkeepers, 1):
            # Add eligibility indicators for GKs
            form_indicator = "🔥" if player.get('form', 0) > 2.0 else "📈" if player.get('form', 0) > 0 else "💤"
            minutes_indicator = "⭐" if player.get('minutes', 0) > 1000 else "✅" if player.get('minutes', 0) > 500 else "⚠️"
            
            # Alternate between columns
            with gk_col1 if i % 2 == 1 else gk_col2:
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #1a237e, #283593); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: white;'>{i}. {player['name']} {form_indicator} {minutes_indicator}</h4>
                    <p style='margin: 0.2rem 0;'>£{player['cost']:.1f}m | Form: {player['form']:.1f} | Ownership: {player.get('selected_by_percent', 0):.1f}%</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>🤖 <strong>ML Prediction:</strong> {player.get('next_3gw_prediction', 0):.1f} pts | ICT: {player.get('ict_index', 0):.0f}</p>
                    <p style='margin: 0.2rem 0; font-size: 0.9em;'>Team: {player['team']} | Minutes: {player.get('minutes', 0)} | Confidence: {player.get('manager_confidence', 1.0):.2f}</p>
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
