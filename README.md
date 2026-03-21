# Market-Making Research Project

Advanced market-making research engine for quantifying adverse selection costs and developing detection mechanisms.

## Project Overview

This project simulates a market maker's operations and answers the research question:

**"How much does adverse selection cost a market maker, and can you detect it in real-time?"**

### Key Features

**Phase 1 - Core Simulation:**
-Geometric Brownian Motion price simulation (with optional jumps)
-Poisson order flow with exponential fill probability
-Market simulator orchestrating all components

**Phase 2 - Trading Strategies:**
-Naive (constant spread baseline)
-Inventory-Aware (asymmetric position-based quoting)
-Avellaneda-Stoikov (optimal risk-aware market-making)

**Coming Soon:**
-VPIN toxicity detection (Phase 3)
-Research experiments (Phase 4)
-Interactive dashboard (Phase 5)

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Quick Start

```python
from src.simulation import create_gbm, OrderFlowGenerator, MarketSimulator, SimulationConfig
from src.simulation.order_flow import OrderFlowConfig
from src.strategies import AvellanedaStoikovStrategy

# Create price process
price_process = create_gbm(S0=100.0, sigma=0.02, seed=42)

# Create order flow
order_flow_config = OrderFlowConfig(A=10.0, kappa=0.5)
order_flow = OrderFlowGenerator(order_flow_config, seed=42)

# Create strategy
strategy = AvellanedaStoikovStrategy(
    risk_aversion=0.1,
    volatility=0.02,
    kappa=0.5
)

# Run simulation
config = SimulationConfig(n_steps=1000)
results = MarketSimulator.run_simulation(
    price_process=price_process,
    order_flow=order_flow,
    strategy=strategy,
    config=config
)

print(f"Final PnL: ${results.final_pnl:.2f}")
print(f"Trades: {results.n_trades}")
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_price_process.py -v
```

## Project Structure

-`src/simulation/` - Core simulation components (Phase 1)
-`src/strategies/` - Trading strategies (Phase 2)
-`tests/` - Comprehensive test suite
-`examples/` - Usage examples and comparisons
-`experiments/` - Research experiments (Phase 4 - Coming Soon)
-`streamlit_app/` - Interactive dashboard (Phase 5 - Coming Soon)

## References

-Avellaneda, M., & Stoikov, S. (2008). High-frequency trading in a limit order book. *Quantitative Finance*, 8(3), 217-224.
-Easley, D., López de Prado, M. M., & O'Hara, M. (2012). Flow toxicity and liquidity in a high-frequency world. *The Review of Financial Studies*, 25(5), 1457-1493.

## License

MIT License - see LICENSE file for details.

