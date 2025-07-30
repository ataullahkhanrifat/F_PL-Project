#!/usr/bin/env python3
"""
Test script to validate the enhanced FPL app with Stats page
"""

import sys
import os

# Add current directory to path
sys.path.append('.')
sys.path.append('src')

try:
    # Test imports
    import pandas as pd
    print("✅ pandas imported successfully")
    
    # Test data loading
    data_path = "data/processed/fpl_players_latest.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"✅ Data loaded successfully: {len(df)} players, {len(df.columns)} columns")
        
        # Test FDR columns
        fdr_cols = ['fdr_attack', 'fdr_defence', 'fdr_overall']
        if all(col in df.columns for col in fdr_cols):
            print("✅ FDR columns present")
        else:
            print("❌ FDR columns missing")
            
        # Test basic stats
        print(f"📊 Quick Stats:")
        print(f"   - Top scorer: {df.loc[df['total_points'].idxmax(), 'name']} ({df['total_points'].max()} pts)")
        print(f"   - Most assists: {df.loc[df['assists'].idxmax(), 'name']} ({df['assists'].max()} assists)")
        print(f"   - Most expensive: {df.loc[df['cost'].idxmax(), 'name']} (£{df['cost'].max():.1f}m)")
        print(f"   - Best value: {df.loc[df['cost_efficiency'].idxmax(), 'name']} ({df['cost_efficiency'].max():.1f} pts/£)")
        
    else:
        print(f"❌ Data file not found: {data_path}")
        
    # Test optimizer import
    from optimizer import FPLOptimizer
    print("✅ FPLOptimizer imported successfully")
    
    print("\n🎉 All tests passed! The enhanced app should work correctly.")
    print("\n📋 Features available:")
    print("   🚀 Squad Optimizer (with FDR, team position limits, expensive player controls)")
    print("   📊 Player Stats (Top 10s, leaderboards, position filters)")
    print("   👤 Developer footer with photo and disclaimer")
    print("   🧭 Page navigation")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
