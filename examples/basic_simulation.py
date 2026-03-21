"""
Basic simulation example.

Runs a simple market-making simulation.
"""

import matplotlib.pyplot as plt
from src.simulation import (
    create_gbm,
    OrderFlowGenerator,
    OrderFlowConfig,
    MarketSimulator,
    SimulationConfig
)


class SimpleStrategy:
    """Constant spread strategy."""
    
    def __init__(self, spread_width: float = 2.0):
        self.spread_width = spread_width
    
    def get_quotes(self, state):
        mid = state['mid_price']
        half_spread = self.spread_width / 2
        return mid - half_spread, mid + half_spread


def main():
    """Run basic simulation."""
    print("Running market-making simulation...")
    
    # Setup
    price_process = create_gbm(S0=100.0, sigma=0.02, seed=42)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=42)
    strategy = SimpleStrategy(spread_width=1.0)
    config = SimulationConfig(n_steps=1000, seed=42)
    
    # Run simulation
    results = MarketSimulator.run_simulation(
        price_process=price_process,
        order_flow=order_flow,
        strategy=strategy,
        config=config
    )
    
    # Print results
    print(f"\nResults:")
    print(f"  Final PnL: ${results.final_pnl:.2f}")
    print(f"  Number of trades: {results.n_trades}")
    print(f"  Final inventory: {int(results.inventories[-1])}")
    
    print(f"\nPnL Decomposition:")
    for key, value in results.pnl_decomposition.items():
        print(f"  {key}: ${value:.2f}")
    
    # Plot results
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    # Price
    axes[0].plot(results.prices)
    axes[0].set_title('Price Evolution')
    axes[0].set_ylabel('Price ($)')
    axes[0].grid(True)
    
    # PnL
    axes[1].plot(results.pnl)
    axes[1].set_title('PnL Evolution')
    axes[1].set_ylabel('PnL ($)')
    axes[1].grid(True)
    
    # Inventory
    axes[2].plot(results.inventories)
    axes[2].set_title('Inventory Evolution')
    axes[2].set_ylabel('Shares')
    axes[2].set_xlabel('Time Step')
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.savefig('simulation_results.png', dpi=150)
    print(f"\nPlot saved to simulation_results.png")
    plt.show()


if __name__ == '__main__':
    main()

