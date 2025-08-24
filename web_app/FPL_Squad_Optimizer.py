"""
FPL Squad Optimizer Module

Contains all logi      budget = st.sid        va            help="Total budget for your 15-player squad"
    )
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")   # Additional filters
    st.sidebar.subheader("Advanced Settings")
    
    # Initialize session state for manually selected players
        step=0.5,
        help="Total budget for your 15-player squad"
    )
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")
    
    # Initialize session state for manually selected players
    if 'manually_selected_players' not in st.session_state:  # Additional filters
    st.sidebar.subheader("Advanced Settings")er(
        "Squad Budget (£m)",
        min_value=80.0,
        max_value=120.0,
        value=100.0,
        step=0.5,
        help="Total budget for your 15-player squad"
    )
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")
    
    # Initialize session state for manually selected playerstal budget for your 15-player squad"
    )
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")Total budget for your 15-player squad"
    )
    
    # Additional filters
    st.sidebar.subheader("Advanced Settings")tions related to squad optimization.
"""

import streamlit as st
import pandas as pd
import sys
import os
import time

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from optimizer import FPLOptimizer
except ImportError:
    st.error("Could not import FPLOptimizer module.")

@st.cache_resource
def load_optimizer(budget):
    """Load and cache the optimizer"""
    return FPLOptimizer(budget=budget)

def create_optimizer_page(players_df):
    """Create the main optimizer page"""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ FPL Squad Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("**Optimize your Fantasy Premier League squad using machine learning and mathematical optimization**")
    
    # Show data and prediction status
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Loaded {len(players_df)} available players (filtered for quality and availability)")

    
    # Navigation button to Stats page
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        if st.button("📊 View Player Stats", key="goto_stats"):
            st.session_state.current_page = 'stats'
            st.session_state.last_user_interaction = time.time()
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
    
    # Initialize session state for manually selected players
    if 'manually_selected_players' not in st.session_state:
        st.session_state.manually_selected_players = []
    
    # Initialize session state for excluded players
    if 'manually_excluded_players' not in st.session_state:
        st.session_state.manually_excluded_players = []
    
    # Manual Player Selection Filter
    manual_selection = st.sidebar.expander("👤 Manual Player Selection")
    with manual_selection:
        st.info("🎯 Pick specific players you want, then optimize the rest!")
        
        # Step 1: Select Team
        all_teams = sorted(players_df['team'].unique().tolist())
        
        def on_team_change():
            st.session_state.last_user_interaction = time.time()
        
        selected_team = st.selectbox(
            "1️⃣ Select Team",
            options=["Choose a team..."] + all_teams,
            key="manual_team_select",
            on_change=on_team_change
        )
        
        if selected_team and selected_team != "Choose a team...":
            # Step 2: Select Position
            team_players = players_df[players_df['team'] == selected_team]
            available_positions = sorted(team_players['position'].unique().tolist())
            
            def on_position_change():
                st.session_state.last_user_interaction = time.time()
            
            selected_position = st.selectbox(
                "2️⃣ Select Position",
                options=["Choose position..."] + available_positions,
                key="manual_position_select",
                on_change=on_position_change
            )
            
            if selected_position and selected_position != "Choose position...":
                # Step 3: Show players with prices (sorted by cost descending)
                position_players = team_players[team_players['position'] == selected_position].copy()
                position_players = position_players.sort_values('cost', ascending=False)
                
                st.write(f"**{selected_position}s from {selected_team}:**")
                
                for idx, player in position_players.iterrows():
                    # Check if player is already selected
                    is_selected = any(p['index'] == idx for p in st.session_state.manually_selected_players)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        player_label = f"{player['name']} - £{player['cost']:.1f}m"
                        if is_selected:
                            player_label += " ✅"
                        st.write(player_label)
                    
                    with col2:
                        if not is_selected:
                            if st.button("➕", key=f"add_{idx}", help="Add player"):
                                # Track user interaction to prevent auto-refresh conflicts
                                st.session_state.last_user_interaction = time.time()
                                # Add player to manual selection
                                st.session_state.manually_selected_players.append({
                                    'index': idx,  # Use dataframe index
                                    'id': player['id'],
                                    'name': player['name'],
                                    'position': player['position'],
                                    'team': player['team'],
                                    'cost': player['cost']
                                })
                                st.rerun()
        
        # Show currently selected manual players
        if st.session_state.manually_selected_players:
            st.write("**🎯 Currently Selected Players:**")
            
            # Calculate totals
            total_cost = sum(p['cost'] for p in st.session_state.manually_selected_players)
            position_count = {'Goalkeeper': 0, 'Defender': 0, 'Midfielder': 0, 'Forward': 0}
            
            for player in st.session_state.manually_selected_players:
                position_count[player['position']] += 1
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {player['name']} ({player['position']}) - £{player['cost']:.1f}m")
                with col2:
                    if st.button("❌", key=f"remove_{player['index']}", help="Remove player"):
                        # Track user interaction to prevent auto-refresh conflicts
                        st.session_state.last_user_interaction = time.time()
                        st.session_state.manually_selected_players = [
                            p for p in st.session_state.manually_selected_players 
                            if p['index'] != player['index']
                        ]
                        st.rerun()
            
            st.write(f"**Total Cost:** £{total_cost:.1f}m")
            st.write(f"**Squad:** GK:{position_count['Goalkeeper']} DEF:{position_count['Defender']} MID:{position_count['Midfielder']} FWD:{position_count['Forward']}")
            
            if st.button("🗑️ Clear All Selected Players", type="secondary"):
                # Track user interaction to prevent auto-refresh conflicts
                st.session_state.last_user_interaction = time.time()
                st.session_state.manually_selected_players = []
                st.rerun()
    
    # Player Exclusion Filter
    player_exclusion = st.sidebar.expander("🚫 Player Exclusion")
    with player_exclusion:
        st.info("🎯 Select specific players you DON'T want in your team!")
        
        # Step 1: Select Team for exclusion
        def on_exclude_team_change():
            st.session_state.last_user_interaction = time.time()
        
        excluded_team = st.selectbox(
            "1️⃣ Select Team",
            options=["Choose a team..."] + all_teams,
            key="exclude_team_select",
            on_change=on_exclude_team_change
        )
        
        if excluded_team and excluded_team != "Choose a team...":
            # Step 2: Select Position for exclusion
            exclude_team_players = players_df[players_df['team'] == excluded_team]
            exclude_available_positions = sorted(exclude_team_players['position'].unique().tolist())
            
            def on_exclude_position_change():
                st.session_state.last_user_interaction = time.time()
            
            excluded_position = st.selectbox(
                "2️⃣ Select Position",
                options=["Choose position..."] + exclude_available_positions,
                key="exclude_position_select",
                on_change=on_exclude_position_change
            )
            
            if excluded_position and excluded_position != "Choose position...":
                # Step 3: Show players for exclusion (sorted by cost descending)
                exclude_position_players = exclude_team_players[exclude_team_players['position'] == excluded_position].copy()
                exclude_position_players = exclude_position_players.sort_values('cost', ascending=False)
                
                st.write(f"**{excluded_position}s from {excluded_team} to exclude:**")
                
                for idx, player in exclude_position_players.iterrows():
                    # Check if player is already excluded
                    is_excluded = any(p['index'] == idx for p in st.session_state.manually_excluded_players)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        player_label = f"{player['name']} - £{player['cost']:.1f}m"
                        if is_excluded:
                            player_label += " ❌"
                        st.write(player_label)
                    
                    with col2:
                        if not is_excluded:
                            if st.button("🚫", key=f"exclude_{idx}", help="Exclude player"):
                                # Track user interaction to prevent auto-refresh conflicts
                                st.session_state.last_user_interaction = time.time()
                                # Add player to exclusion list
                                st.session_state.manually_excluded_players.append({
                                    'index': idx,
                                    'name': player['name'],
                                    'position': player['position'],
                                    'team': player['team'],
                                    'cost': player['cost']
                                })
                                st.rerun()
        
        # Show currently excluded players
        if st.session_state.manually_excluded_players:
            st.write("**🚫 Currently Excluded Players:**")
            
            # Calculate totals
            total_excluded = len(st.session_state.manually_excluded_players)
            exclude_position_count = {'Goalkeeper': 0, 'Defender': 0, 'Midfielder': 0, 'Forward': 0}
            
            for player in st.session_state.manually_excluded_players:
                exclude_position_count[player['position']] += 1
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {player['name']} ({player['position']}) - £{player['cost']:.1f}m")
                with col2:
                    if st.button("✅", key=f"include_{player['index']}", help="Remove from exclusion"):
                        # Track user interaction to prevent auto-refresh conflicts
                        st.session_state.last_user_interaction = time.time()
                        st.session_state.manually_excluded_players = [
                            p for p in st.session_state.manually_excluded_players 
                            if p['index'] != player['index']
                        ]
                        st.rerun()
            
            st.write(f"**Total Excluded:** {total_excluded} players")
            st.write(f"**Excluded by Position:** GK:{exclude_position_count['Goalkeeper']} DEF:{exclude_position_count['Defender']} MID:{exclude_position_count['Midfielder']} FWD:{exclude_position_count['Forward']}")
            
            if st.button("🗑️ Clear All Excluded Players", type="secondary", key="clear_excluded"):
                # Track user interaction to prevent auto-refresh conflicts
                st.session_state.last_user_interaction = time.time()
                st.session_state.manually_excluded_players = []
                st.rerun()
    
    # Team filter
    all_teams = ['All Teams'] + sorted(players_df['team'].unique().tolist())
    
    def on_excluded_teams_change():
        st.session_state.last_user_interaction = time.time()
    
    excluded_teams = st.sidebar.multiselect(
        "Exclude Teams",
        options=all_teams[1:],  # Exclude 'All Teams' from options
        help="Select teams to exclude from optimization",
        on_change=on_excluded_teams_change
    )
    
    # FDR Settings
    fdr_settings = st.sidebar.expander("🌟 FDR (Fixture Difficulty) Settings")
    with fdr_settings:
        def on_fdr_change():
            st.session_state.last_user_interaction = time.time()
        
        use_fdr = st.checkbox(
            "Use FDR in optimization", 
            value=True, 
            help="Consider fixture difficulty when selecting players",
            on_change=on_fdr_change
        )
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
        
        def on_limit_teams_change():
            st.session_state.last_user_interaction = time.time()
        
        selected_limit_teams = st.multiselect(
            "Select teams to limit", 
            all_teams[1:],
            on_change=on_limit_teams_change
        )
        
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
        all_teams_list = sorted(players_df['team'].unique().tolist()) if players_df is not None else []
        
        def on_teams_change():
            st.session_state.last_user_interaction = time.time()
        
        selected_teams = st.multiselect(
            "Select teams", 
            all_teams_list,
            on_change=on_teams_change
        )
        
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
        # Track user interaction to prevent auto-refresh conflicts
        st.session_state.last_user_interaction = time.time()
        
        # Filter data based on user selections
        filtered_df = players_df.copy()
        
        if excluded_teams:
            filtered_df = filtered_df[~filtered_df['team'].isin(excluded_teams)]
        
        # Remove manually excluded players
        if st.session_state.manually_excluded_players:
            excluded_indices = [p['index'] for p in st.session_state.manually_excluded_players]
            filtered_df = filtered_df[~filtered_df.index.isin(excluded_indices)]
        
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
            
            # Set team requirements
            if team_reqs:
                optimizer.set_team_requirements(team_reqs)
            
            # Set team position limits
            if team_pos_limits:
                optimizer.set_team_position_limits(team_pos_limits)
            
            # Set expensive player thresholds
            optimizer.expensive_threshold = expensive_threshold
            optimizer.very_expensive_threshold = very_expensive_threshold
            optimizer.max_expensive_bench = max_expensive_bench
            
            # Load model and predict points
            optimizer.load_model()
            predicted_df = optimizer.predict_points(filtered_df)
            
            # Handle manually selected players
            if st.session_state.manually_selected_players:
                # Force include manually selected players
                manual_player_indices = [p['index'] for p in st.session_state.manually_selected_players]
                
                # Update optimizer to handle manual selections
                optimizer.manually_selected_players = manual_player_indices
            
            # Run optimization
            results = optimizer.optimize_squad(predicted_df)
        
        # Store results in session state
        st.session_state.optimization_results = results
        
        # Display results
        if results['status'] == 'optimal':
            st.success("✅ Optimization completed successfully!")
            
            selected_players = results['selected_players']
            starting_players = results['starting_players']
            bench_players = results['bench_players']
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🏆 Squad Overview", 
                "🎯 Starting XI", 
                "🪑 Bench", 
                "📊 Statistics",
                "⚙️ Settings Applied"
            ])
            
            with tab1:
                st.header("Complete Squad")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Cost", f"£{results['total_cost']:.1f}m")
                
                with col2:
                    st.metric("Predicted Points", f"{results['total_predicted_points']:.1f}")
                
                with col3:
                    st.metric("Budget Usage", f"{results['budget_usage_pct']:.1f}%")
                
                with col4:
                    st.metric("Remaining Budget", f"£{results['remaining_budget']:.1f}m")
                
                # Full squad table
                st.dataframe(
                    selected_players[['name', 'position', 'team', 'cost', 'predicted_points', 'form', 'total_points']],
                    column_config={
                        "name": st.column_config.TextColumn("Player"),
                        "position": st.column_config.TextColumn("Position"),
                        "team": st.column_config.TextColumn("Team"),
                        "cost": st.column_config.NumberColumn("Cost (£m)", format="%.1f"),
                        "predicted_points": st.column_config.NumberColumn("Predicted Points", format="%.1f"),
                        "form": st.column_config.NumberColumn("Form", format="%.1f"),
                        "total_points": st.column_config.NumberColumn("Season Points", format="%d")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            with tab2:
                st.header("Starting XI")
                st.write(f"**Predicted Points: {results['starting_predicted_points']:.1f}**")
                
                # Starting formation display
                formation = results.get('formation', 'Unknown')
                st.subheader(f"Formation: {formation}")
                
                # Starting XI table
                st.dataframe(
                    starting_players[['name', 'position', 'team', 'cost', 'predicted_points', 'form']],
                    column_config={
                        "name": st.column_config.TextColumn("Player"),
                        "position": st.column_config.TextColumn("Position"),
                        "team": st.column_config.TextColumn("Team"),
                        "cost": st.column_config.NumberColumn("Cost (£m)", format="%.1f"),
                        "predicted_points": st.column_config.NumberColumn("Predicted Points", format="%.1f"),
                        "form": st.column_config.NumberColumn("Form", format="%.1f")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            with tab3:
                st.header("Bench Players")
                st.write(f"**Bench Value: £{bench_players['cost'].sum():.1f}m**")
                
                # Bench table
                st.dataframe(
                    bench_players[['name', 'position', 'team', 'cost', 'predicted_points', 'form']],
                    column_config={
                        "name": st.column_config.TextColumn("Player"),
                        "position": st.column_config.TextColumn("Position"), 
                        "team": st.column_config.TextColumn("Team"),
                        "cost": st.column_config.NumberColumn("Cost (£m)", format="%.1f"),
                        "predicted_points": st.column_config.NumberColumn("Predicted Points", format="%.1f"),
                        "form": st.column_config.NumberColumn("Form", format="%.1f")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            with tab4:
                st.header("Squad Statistics")
                
                # Position breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Position Breakdown")
                    position_df = pd.DataFrame(list(results['position_breakdown'].items()), 
                                             columns=['Position', 'Count'])
                    st.dataframe(position_df, hide_index=True, use_container_width=True)
                
                with col2:
                    st.subheader("Team Breakdown")
                    team_df = pd.DataFrame(list(results['team_breakdown'].items()), 
                                         columns=['Team', 'Players'])
                    team_df = team_df.sort_values('Players', ascending=False)
                    st.dataframe(team_df, hide_index=True, use_container_width=True)
            
            with tab5:
                st.header("Optimization Details")
                
                # Settings applied
                st.subheader("Settings Applied")
                settings_data = [
                    ['Budget', f'£{budget}m'],
                    ['Min Budget Usage', f'{min_budget_usage*100:.0f}%'],
                    ['FDR Enabled', 'Yes' if use_fdr else 'No'],
                    ['Team Requirements', str(team_reqs) if team_reqs else 'None'],
                    ['Max per Team', f'{3} players'],
                    ['Manual Selections', f'{len(st.session_state.manually_selected_players)} players' if st.session_state.manually_selected_players else 'None'],
                    ['Manual Exclusions', f'{len(st.session_state.manually_excluded_players)} players' if st.session_state.manually_excluded_players else 'None']
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
        else:
            st.error("❌ Optimization failed!")
            st.error(results.get('message', 'No feasible solution found'))
            
            # Display debug information
            st.subheader("Debug Information")
            st.write("**Applied Constraints:**")
            st.write(f"- Budget: £{budget}m")
            st.write(f"- Min Budget Usage: {min_budget_usage*100:.0f}%")
            st.write(f"- Excluded Teams: {excluded_teams}")
            if st.session_state.manually_selected_players:
                st.write(f"- Manual Selections: {len(st.session_state.manually_selected_players)} players")
            if st.session_state.manually_excluded_players:
                st.write(f"- Manual Exclusions: {len(st.session_state.manually_excluded_players)} players")
            if team_reqs:
                st.write(f"- Team Requirements: {team_reqs}")
            if team_pos_limits:
                st.write(f"- Team Position Limits: {len(team_pos_limits)} teams")
            
            st.info("💡 Try relaxing some constraints or increasing the budget.")

def optimize_squad_advanced(players_df, budget, constraints=None):
    """
    Advanced squad optimization with custom constraints
    
    Args:
        players_df: DataFrame containing player data
        budget: Maximum budget for the squad
        constraints: Dictionary of additional constraints
    
    Returns:
        Dictionary containing optimization results
    """
    try:
        optimizer = FPLOptimizer(budget=budget)
        
        # Apply any additional constraints if provided
        if constraints:
            if 'team_limits' in constraints:
                optimizer.set_team_requirements(constraints['team_limits'])
            if 'position_limits' in constraints:
                optimizer.set_team_position_limits(constraints['position_limits'])
        
        # Load model and predict points
        optimizer.load_model()
        predicted_df = optimizer.predict_points(players_df)
        
        # Run optimization
        results = optimizer.optimize_squad(predicted_df)
        
        return results
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Optimization failed: {str(e)}"
        }

def get_player_value_analysis(players_df):
    """
    Analyze player values and return insights for optimization
    
    Args:
        players_df: DataFrame containing player data
    
    Returns:
        Dictionary containing value analysis
    """
    try:
        # Calculate value metrics
        players_df['points_per_cost'] = players_df['total_points'] / players_df['cost']
        players_df['form_per_cost'] = players_df['form'] / players_df['cost']
        
        # Best value players by position
        value_analysis = {}
        for position in players_df['position'].unique():
            pos_players = players_df[players_df['position'] == position]
            
            # Top 5 by points per cost
            top_value = pos_players.nlargest(5, 'points_per_cost')[
                ['name', 'team', 'cost', 'total_points', 'points_per_cost']
            ]
            
            value_analysis[position] = {
                'best_value': top_value.to_dict('records'),
                'avg_cost': pos_players['cost'].mean(),
                'avg_points': pos_players['total_points'].mean()
            }
        
        return value_analysis
        
    except Exception as e:
        return {'error': f"Value analysis failed: {str(e)}"}

def validate_squad_constraints(selected_players):
    """
    Validate that a selected squad meets FPL constraints
    
    Args:
        selected_players: DataFrame or list of selected players
    
    Returns:
        Dictionary with validation results
    """
    if isinstance(selected_players, list):
        # Convert list to DataFrame if needed
        selected_players = pd.DataFrame(selected_players)
    
    validation = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check squad size
    if len(selected_players) != 15:
        validation['valid'] = False
        validation['errors'].append(f"Squad must have 15 players, got {len(selected_players)}")
    
    # Check position counts
    position_counts = selected_players['position'].value_counts()
    
    required_positions = {
        'Goalkeeper': 2,
        'Defender': 5,
        'Midfielder': 5,
        'Forward': 3
    }
    
    for position, required_count in required_positions.items():
        actual_count = position_counts.get(position, 0)
        if actual_count != required_count:
            validation['valid'] = False
            validation['errors'].append(
                f"Need {required_count} {position}s, got {actual_count}"
            )
    
    # Check team limits (max 3 players per team)
    team_counts = selected_players['team'].value_counts()
    for team, count in team_counts.items():
        if count > 3:
            validation['valid'] = False
            validation['errors'].append(f"Too many players from {team}: {count}/3")
    
    # Check budget (if cost column exists)
    if 'cost' in selected_players.columns:
        total_cost = selected_players['cost'].sum()
        if total_cost > 100.0:  # Standard FPL budget
            validation['valid'] = False
            validation['errors'].append(f"Squad cost £{total_cost:.1f}m exceeds £100.0m budget")
    
    return validation
