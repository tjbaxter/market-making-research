"""
Strategy comparison example.

Compares performance of all three strategies in benign flow.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src.simulation import (
    create_gbm,
    OrderFlowGenerator,
    OrderFlowConfig,
    MarketSimulator,
    SimulationConfig,
    FlowRegime
)
from src.strategies import (
    NaiveStrategy,
    InventoryAwareStrategy,
    AvellanedaStoikovStrategy
)


def run_strategy(strategy, seed=42, n_steps=1000):
    """Run simulation with given strategy."""
    # Setup
    price_process = create_gbm(S0=100.0, sigma=0.02, seed=seed)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=seed)
    
    # Configure for benign flow
    order_flow.set_regime(FlowRegime.BENIGN)
    
    config = SimulationConfig(n_steps=n_steps, seed=seed)
    
    # Run
    return MarketSimulator.run_simulation(
        price_process=price_process,
        order_flow=order_flow,
        strategy=strategy,
        config=config
    )


def main():
    """Compare all three strategies."""
    print("Comparing Market-Making Strategies")
    print("=" * 60)
    
    # Create strategies
    strategies = {
        'Naive': NaiveStrategy(spread_width=1.0),
        'Inventory-Aware': InventoryAwareStrategy(
            base_spread=1.0,
            inventory_penalty=0.02
        ),
        'Avellaneda-Stoikov': AvellanedaStoikovStrategy(
            risk_aversion=0.1,
            volatility=0.02,
            kappa=0.5
        )
    }
    
    # Run simulations
    results = {}
    for name, strategy in strategies.items():
        print(f"\nRunning {name} strategy...")
        results[name] = run_strategy(strategy, seed=42, n_steps=1000)
    
    # Print comparison
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    comparison_data = []
    
    for name, result in results.items():
        decomp = result.pnl_decomposition
        
        comparison_data.append({
            'Strategy': name,
            'Final PnL': result.final_pnl,
            'Spread Capture': decomp['spread_capture'],
            'Adverse Selection': decomp['adverse_selection'],
            'Num Trades': result.n_trades,
            'Avg Abs Inventory': np.mean(np.abs(result.inventories)),
            'Max Abs Inventory': np.max(np.abs(result.inventories)),
            'PnL Std Dev': np.std(result.pnl)
        })
    
    df = pd.DataFrame(comparison_data)
    print("\n", df.to_string(index=False))
    
    # Plot comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # PnL evolution
    ax = axes[0, 0]
    for name, result in results.items():
        ax.plot(result.pnl, label=name, linewidth=2)
    ax.set_title('PnL Evolution', fontsize=12, fontweight='bold')
    ax.set_xlabel('Time Step')
    ax.set_ylabel('PnL ($)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Inventory evolution
    ax = axes[0, 1]
    for name, result in results.items():
        ax.plot(result.inventories, label=name, linewidth=2, alpha=0.7)
    ax.set_title('Inventory Evolution', fontsize=12, fontweight='bold')
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Inventory (shares)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    # PnL decomposition
    ax = axes[1, 0]
    strategies_list = list(results.keys())
    spread_capture = [results[s].pnl_decomposition['spread_capture'] for s in strategies_list]
    adverse_sel = [results[s].pnl_decomposition['adverse_selection'] for s in strategies_list]
    
    x = np.arange(len(strategies_list))
    width = 0.35
    
    ax.bar(x - width/2, spread_capture, width, label='Spread Capture', color='green', alpha=0.7)
    ax.bar(x + width/2, adverse_sel, width, label='Adverse Selection', color='red', alpha=0.7)
    
    ax.set_title('PnL Decomposition', fontsize=12, fontweight='bold')
    ax.set_ylabel('PnL ($)')
    ax.set_xticks(x)
    ax.set_xticklabels(strategies_list, rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    # Final metrics comparison
    ax = axes[1, 1]
    metrics = ['Final PnL', 'Num Trades', 'Avg Abs Inv']
    
    # Normalize for visualization
    final_pnls = [results[s].final_pnl for s in strategies_list]
    num_trades = [results[s].n_trades for s in strategies_list]
    avg_invs = [np.mean(np.abs(results[s].inventories)) for s in strategies_list]
    
    # Plot as grouped bars
    x = np.arange(len(strategies_list))
    
    norm_pnl = np.array(final_pnls) / max(final_pnls) if max(final_pnls) > 0 else final_pnls
    norm_trades = np.array(num_trades) / max(num_trades) if max(num_trades) > 0 else num_trades
    norm_inv = np.array(avg_invs) / max(avg_invs) if max(avg_invs) > 0 else avg_invs
    
    width = 0.25
    ax.bar(x - width, norm_pnl, width, label='Final PnL (norm)', alpha=0.7)
    ax.bar(x, norm_trades, width, label='Trades (norm)', alpha=0.7)
    ax.bar(x + width, 1 - norm_inv, width, label='Inv Control (norm)', alpha=0.7)
    
    ax.set_title('Normalized Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Value')
    ax.set_xticks(x)
    ax.set_xticklabels(strategies_list, rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('strategy_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to strategy_comparison.png")
    plt.show()
    
    # Print winner
    print("\n" + "=" * 60)
    best_strategy = max(results.items(), key=lambda x: x[1].final_pnl)
    print(f"Best Strategy: {best_strategy[0]}")
    print(f"Final PnL: ${best_strategy[1].final_pnl:.2f}")
    print("=" * 60)


if __name__ == '__main__':
    main()

