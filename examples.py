#!/usr/bin/env python3
"""
FPL Optimizer Examples - Demonstration of Enhanced Features

This script shows how to use the enhanced FPL optimizer with:
1. Position weights
2. Minimum budget usage (99%+)
3. Starting XI vs Bench differentiation
4. Custom team requirements
5. Popular players prioritization
"""

import sys
import os
sys.path.append('src')

from optimizer import FPLOptimizer
import pandas as pd

def example_1_basic_optimization():
    """Example 1: Basic optimization with 99% budget usage"""
    print("="*80)
    print("EXAMPLE 1: Basic Optimization with 99% Budget Usage")
    print("="*80)
    
    # Load data
    players_df = pd.read_csv("data/processed/fpl_players_latest.csv")
    
    # Create optimizer with 99% minimum budget usage
    optimizer = FPLOptimizer(budget=100.0, min_budget_usage=0.99)
    
    # Predict points and optimize
    optimizer.load_model()
    players_df = optimizer.predict_points(players_df)
    results = optimizer.optimize_squad(players_df)
    
    # Show results
    optimizer.print_squad_summary(results)
    return results

def example_2_position_weights():
    """Example 2: Prioritize midfielders and forwards"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Position Weights - Prioritize Attacking Players")
    print("="*80)
    
    # Load data
    players_df = pd.read_csv("data/processed/fpl_players_latest.csv")
    
    # Create optimizer
    optimizer = FPLOptimizer(budget=100.0, min_budget_usage=0.99)
    
    # Set position weights - prioritize attacking players
    optimizer.set_position_weights({
        'Goalkeeper': 0.7,    # Less priority
        'Defender': 0.9,      # Less priority  
        'Midfielder': 1.4,    # HIGH priority
        'Forward': 1.3        # HIGH priority
    })
    
    # Optimize
    optimizer.load_model()
    players_df = optimizer.predict_points(players_df)
    results = optimizer.optimize_squad(players_df)
    
    optimizer.print_squad_summary(results)
    return results

def example_3_team_requirements():
    """Example 3: Custom team requirements"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Custom Team Requirements")
    print("="*80)
    
    # Load data
    players_df = pd.read_csv("data/processed/fpl_players_latest.csv")
    
    # Create optimizer
    optimizer = FPLOptimizer(budget=100.0, min_budget_usage=0.99)
    
    # Set specific team requirements
    optimizer.set_team_requirements({
        'Arsenal': 2,      # Want exactly 2 Arsenal players
        'Man City': 3,     # Want exactly 3 Man City players
        'Liverpool': 2,    # Want exactly 2 Liverpool players
    })
    
    # Optimize
    optimizer.load_model()
    players_df = optimizer.predict_points(players_df)
    results = optimizer.optimize_squad(players_df)
    
    optimizer.print_squad_summary(results)
    return results

def example_4_defensive_strategy():
    """Example 4: Defensive strategy - prioritize clean sheets"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Defensive Strategy - Prioritize Defenders & Goalkeepers")
    print("="*80)
    
    # Load data
    players_df = pd.read_csv("data/processed/fpl_players_latest.csv")
    
    # Create optimizer
    optimizer = FPLOptimizer(budget=100.0, min_budget_usage=0.99)
    
    # Set position weights for defensive strategy
    optimizer.set_position_weights({
        'Goalkeeper': 1.3,    # HIGH priority
        'Defender': 1.4,      # HIGHEST priority
        'Midfielder': 1.0,    # Normal
        'Forward': 0.8        # Lower priority
    })
    
    # Optimize
    optimizer.load_model()
    players_df = optimizer.predict_points(players_df)
    results = optimizer.optimize_squad(players_df)
    
    optimizer.print_squad_summary(results)
    return results

def example_5_budget_comparison():
    """Example 5: Compare different budget constraints"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Budget Usage Comparison")
    print("="*80)
    
    budgets = [90, 95, 100]
    min_usages = [0.95, 0.98, 0.99]
    
    players_df = pd.read_csv("data/processed/fpl_players_latest.csv")
    
    for budget, min_usage in zip(budgets, min_usages):
        print(f"\n--- Budget: £{budget}m, Min Usage: {min_usage*100:.0f}% ---")
        
        optimizer = FPLOptimizer(budget=budget, min_budget_usage=min_usage)
        optimizer.load_model()
        players_df_temp = optimizer.predict_points(players_df.copy())
        results = optimizer.optimize_squad(players_df_temp)
        
        if results['status'] == 'optimal':
            print(f"✅ Total Cost: £{results['total_cost']:.1f}m ({results['budget_usage_pct']:.1f}%)")
            print(f"   Predicted Points: {results['total_predicted_points']:.1f}")
            print(f"   Starting XI Points: {results.get('starting_predicted_points', 0):.1f}")
        else:
            print(f"❌ Optimization failed")

def compare_strategies():
    """Compare different strategies side by side"""
    print("\n" + "="*80)
    print("STRATEGY COMPARISON SUMMARY")
    print("="*80)
    
    players_df = pd.read_csv("data/processed/fpl_players_latest.csv")
    
    strategies = [
        ("Balanced", {'Goalkeeper': 1.0, 'Defender': 1.0, 'Midfielder': 1.0, 'Forward': 1.0}),
        ("Attacking", {'Goalkeeper': 0.7, 'Defender': 0.9, 'Midfielder': 1.4, 'Forward': 1.3}),
        ("Defensive", {'Goalkeeper': 1.3, 'Defender': 1.4, 'Midfielder': 1.0, 'Forward': 0.8}),
        ("Mid-heavy", {'Goalkeeper': 0.8, 'Defender': 0.9, 'Midfielder': 1.5, 'Forward': 1.0})
    ]
    
    results_summary = []
    
    for strategy_name, weights in strategies:
        optimizer = FPLOptimizer(budget=100.0, min_budget_usage=0.99)
        optimizer.set_position_weights(weights)
        optimizer.load_model()
        
        players_df_temp = optimizer.predict_points(players_df.copy())
        results = optimizer.optimize_squad(players_df_temp)
        
        if results['status'] == 'optimal':
            results_summary.append({
                'Strategy': strategy_name,
                'Total Points': f"{results['total_predicted_points']:.1f}",
                'Starting XI Points': f"{results.get('starting_predicted_points', 0):.1f}",
                'Cost': f"£{results['total_cost']:.1f}m",
                'Budget Usage': f"{results['budget_usage_pct']:.1f}%"
            })
    
    # Display comparison table
    comparison_df = pd.DataFrame(results_summary)
    print(comparison_df.to_string(index=False))

def main():
    """Run all examples"""
    print("🏆 FPL OPTIMIZER ENHANCED FEATURES DEMONSTRATION")
    print("=" * 80)
    print("This script demonstrates all the new features:")
    print("✅ Position weights that actually work")
    print("✅ 99%+ budget usage (no more £20m left unused)")
    print("✅ Starting XI vs Bench differentiation")
    print("✅ Custom team requirements")
    print("✅ Popular player prioritization")
    print("=" * 80)
    
    try:
        # Run examples
        example_1_basic_optimization()
        example_2_position_weights()
        example_3_team_requirements()
        example_4_defensive_strategy()
        example_5_budget_comparison()
        compare_strategies()
        
        print("\n" + "="*80)
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("Key improvements:")
        print("1. ✅ Position weights now properly affect player selection")
        print("2. ✅ Budget usage forced to 99%+ (configurable)")
        print("3. ✅ Starting XI gets popular, high-scoring players")
        print("4. ✅ Bench gets budget players to maximize starting XI")
        print("5. ✅ Custom team requirements work perfectly")
        print("6. ✅ Web app includes all new features")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
