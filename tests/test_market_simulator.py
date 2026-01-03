"""Tests for market simulator."""

import pytest
from src.simulation import (
    create_gbm,
    OrderFlowGenerator,
    OrderFlowConfig,
    MarketSimulator,
    SimulationConfig
)


class DummyStrategy:
    """Simple constant-spread strategy for testing."""
    
    def __init__(self, spread: float = 2.0):
        self.spread = spread
    
    def get_quotes(self, state):
        mid = state['mid_price']
        return mid - self.spread/2, mid + self.spread/2


def test_simulation_runs():
    """Test basic simulation runs without errors."""
    price_process = create_gbm(S0=100.0, seed=42)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=42)
    strategy = DummyStrategy()
    config = SimulationConfig(n_steps=100, seed=42)
    
    results = MarketSimulator.run_simulation(
        price_process=price_process,
        order_flow=order_flow,
        strategy=strategy,
        config=config
    )
    
    assert len(results.prices) == 101
    assert len(results.inventories) == 101
    assert results.n_trades >= 0


def test_simulation_reproducibility():
    """Test simulation is reproducible."""
    def run_sim():
        price_process = create_gbm(S0=100.0, seed=42)
        order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
        order_flow = OrderFlowGenerator(order_flow_config, seed=42)
        strategy = DummyStrategy()
        config = SimulationConfig(n_steps=50, seed=42)
        
        return MarketSimulator.run_simulation(
            price_process, order_flow, strategy, config
        )
    
    results1 = run_sim()
    results2 = run_sim()
    
    assert results1.final_pnl == results2.final_pnl
    assert results1.n_trades == results2.n_trades


def test_simulation_collects_metrics():
    """Test that simulation collects all expected metrics."""
    price_process = create_gbm(S0=100.0, seed=42)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=42)
    strategy = DummyStrategy()
    config = SimulationConfig(n_steps=100, seed=42)
    
    results = MarketSimulator.run_simulation(
        price_process, order_flow, strategy, config
    )
    
    # Check all metrics are present
    assert hasattr(results, 'prices')
    assert hasattr(results, 'inventories')
    assert hasattr(results, 'pnl')
    assert hasattr(results, 'cash')
    assert hasattr(results, 'trades_df')
    assert hasattr(results, 'pnl_decomposition')
    assert hasattr(results, 'final_pnl')
    assert hasattr(results, 'n_trades')


def test_simulation_with_different_strategies():
    """Test simulation works with different spread widths."""
    price_process = create_gbm(S0=100.0, seed=42)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=42)
    
    # Narrow spread
    strategy_narrow = DummyStrategy(spread=0.5)
    config = SimulationConfig(n_steps=100, seed=42)
    
    results_narrow = MarketSimulator.run_simulation(
        price_process, order_flow, strategy_narrow, config
    )
    
    # Reset and run with wide spread
    price_process = create_gbm(S0=100.0, seed=42)
    order_flow = OrderFlowGenerator(order_flow_config, seed=42)
    strategy_wide = DummyStrategy(spread=5.0)
    
    results_wide = MarketSimulator.run_simulation(
        price_process, order_flow, strategy_wide, config
    )
    
    # Narrow spread should generate more trades
    assert results_narrow.n_trades >= results_wide.n_trades

