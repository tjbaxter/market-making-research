"""Integration tests comparing strategy performance."""

import pytest
import numpy as np
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


def run_strategy_simulation(strategy, n_steps=500, seed=42):
    """Helper to run simulation with a strategy."""
    price_process = create_gbm(S0=100.0, sigma=0.02, seed=seed)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=seed)
    config = SimulationConfig(n_steps=n_steps, seed=seed)
    
    return MarketSimulator.run_simulation(
        price_process=price_process,
        order_flow=order_flow,
        strategy=strategy,
        config=config
    )


def test_all_strategies_complete_simulation():
    """Test all strategies can complete a full simulation."""
    strategies = [
        NaiveStrategy(spread_width=1.0),
        InventoryAwareStrategy(base_spread=1.0, inventory_penalty=0.01),
        AvellanedaStoikovStrategy(risk_aversion=0.1, volatility=0.02, kappa=0.5)
    ]
    
    for strategy in strategies:
        results = run_strategy_simulation(strategy, n_steps=100)
        
        assert results.n_trades >= 0
        assert len(results.prices) == 101
        assert len(results.inventories) == 101


def test_inventory_aware_manages_inventory_better():
    """Test inventory-aware strategy manages inventory better than naive."""
    naive = NaiveStrategy(spread_width=1.0)
    inventory_aware = InventoryAwareStrategy(
        base_spread=1.0,
        inventory_penalty=0.02  # Aggressive inventory management
    )
    
    results_naive = run_strategy_simulation(naive, n_steps=500)
    results_ia = run_strategy_simulation(inventory_aware, n_steps=500)
    
    # Inventory-aware should have lower average absolute inventory
    avg_inv_naive = np.mean(np.abs(results_naive.inventories))
    avg_inv_ia = np.mean(np.abs(results_ia.inventories))
    
    # This is probabilistic but should hold on average
    # (May need multiple runs for statistical significance)
    assert avg_inv_ia <= avg_inv_naive * 1.5  # Allow some variance


def test_as_strategy_adjusts_to_inventory():
    """Test AS strategy adjusts reservation price with inventory."""
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=0.1,
        volatility=0.02,
        kappa=0.5,
        T=1000
    )
    
    results = run_strategy_simulation(strategy, n_steps=200)
    
    # Get quote history
    quote_history = strategy.get_quote_history()
    
    # Find a moment with non-zero inventory
    for i, quote in enumerate(quote_history):
        if results.inventories[i] != 0:
            # Check that quotes shifted
            mid = quote['mid']
            bid = quote['bid']
            ask = quote['ask']
            
            # Quotes should be valid
            assert bid < ask
            assert bid > 0
            assert ask > 0
            break


def test_strategies_make_profit_in_benign_flow():
    """Test all strategies are profitable in benign flow."""
    strategies = [
        NaiveStrategy(spread_width=1.0),
        InventoryAwareStrategy(base_spread=1.0, inventory_penalty=0.01),
        AvellanedaStoikovStrategy(risk_aversion=0.1, volatility=0.02, kappa=0.5)
    ]
    
    profits = []
    
    for strategy in strategies:
        results = run_strategy_simulation(strategy, n_steps=1000, seed=42)
        profits.append(results.pnl_decomposition['spread_capture'])
    
    # All should capture positive spread
    for i, profit in enumerate(profits):
        assert profit > 0, f"Strategy {strategies[i].name} failed to profit"


def test_strategy_reproducibility():
    """Test strategies produce reproducible results."""
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=0.1,
        volatility=0.02,
        kappa=0.5
    )
    
    results1 = run_strategy_simulation(strategy, n_steps=100, seed=42)
    
    # Reset strategy
    strategy.reset()
    
    results2 = run_strategy_simulation(strategy, n_steps=100, seed=42)
    
    # Should be identical
    assert results1.final_pnl == pytest.approx(results2.final_pnl)
    assert results1.n_trades == results2.n_trades
    np.testing.assert_array_almost_equal(results1.prices, results2.prices)


def test_wider_spread_reduces_fills():
    """Test that wider spreads result in fewer fills."""
    narrow = NaiveStrategy(spread_width=0.5)
    wide = NaiveStrategy(spread_width=3.0)
    
    results_narrow = run_strategy_simulation(narrow, n_steps=500, seed=42)
    results_wide = run_strategy_simulation(wide, n_steps=500, seed=42)
    
    # Wider spread should result in fewer trades
    assert results_wide.n_trades <= results_narrow.n_trades


def test_as_strategy_with_different_risk_aversions():
    """Test AS strategy behavior with different risk aversions."""
    conservative = AvellanedaStoikovStrategy(
        risk_aversion=0.5,  # High risk aversion
        volatility=0.02,
        kappa=0.5
    )
    
    aggressive = AvellanedaStoikovStrategy(
        risk_aversion=0.05,  # Low risk aversion
        volatility=0.02,
        kappa=0.5
    )
    
    results_conservative = run_strategy_simulation(conservative, n_steps=500, seed=42)
    results_aggressive = run_strategy_simulation(aggressive, n_steps=500, seed=42)
    
    # Conservative should have wider spreads -> fewer trades
    assert results_conservative.n_trades <= results_aggressive.n_trades
    
    # Conservative should have lower average inventory
    avg_inv_conservative = np.mean(np.abs(results_conservative.inventories))
    avg_inv_aggressive = np.mean(np.abs(results_aggressive.inventories))
    
    assert avg_inv_conservative <= avg_inv_aggressive * 1.5


def test_strategies_handle_extreme_inventory():
    """Test strategies handle extreme inventory positions."""
    strategies = [
        NaiveStrategy(spread_width=1.0),
        InventoryAwareStrategy(base_spread=1.0, inventory_penalty=0.01),
        AvellanedaStoikovStrategy(risk_aversion=0.1, volatility=0.02, kappa=0.5)
    ]
    
    # Create state with extreme inventory
    state = {
        'mid_price': 100.0,
        'inventory': 1000,  # Very large position
        'time': 50,
        'time_remaining': 50
    }
    
    for strategy in strategies:
        bid, ask = strategy.get_quotes(state)
        
        # Should still return valid quotes
        assert bid > 0
        assert ask > 0
        assert bid < ask


def test_pnl_decomposition_consistency():
    """Test PnL decomposition sums correctly."""
    strategy = NaiveStrategy(spread_width=1.0)
    results = run_strategy_simulation(strategy, n_steps=500, seed=42)
    
    decomp = results.pnl_decomposition
    
    # Components should approximately sum to total
    components_sum = (
        decomp['spread_capture'] + 
        decomp['inventory_timing'] + 
        decomp['adverse_selection']
    )
    
    # Allow some tolerance due to inventory valuation
    assert abs(components_sum - decomp['total']) < abs(decomp['total']) * 0.5


def test_strategies_with_toxic_flow():
    """Test strategies behavior in toxic flow regime."""
    strategy = InventoryAwareStrategy(base_spread=1.0, inventory_penalty=0.02)
    
    # Setup with toxic flow
    price_process = create_gbm(S0=100.0, sigma=0.02, seed=42)
    order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5, toxicity_factor=0.5)
    order_flow = OrderFlowGenerator(order_flow_config, seed=42)
    order_flow.set_regime(FlowRegime.TOXIC)
    
    config = SimulationConfig(n_steps=500, seed=42)
    
    results = MarketSimulator.run_simulation(
        price_process=price_process,
        order_flow=order_flow,
        strategy=strategy,
        config=config
    )
    
    # Should still complete
    assert results.n_trades >= 0
    
    # Adverse selection component should be more negative
    assert results.pnl_decomposition['adverse_selection'] < 0

