# Quick Start Guide

## Install and Run (3 Steps)

```bash
# 1. Navigate to project
cd market-making-research

# 2. Run installation script
./install.sh

# 3. Activate environment and test
source venv/bin/activate
pytest
python examples/basic_simulation.py
```

## What You Get

✅ **Complete simulation engine** for market-making research  
✅ **20+ unit tests** - all passing  
✅ **Production-grade code** with type hints and docstrings  
✅ **Working example** that generates plots  
✅ **Reproducible results** with random seeds  

## Next Steps

1. **Run the example**: `python examples/basic_simulation.py`
2. **Read the code**: Start with `examples/basic_simulation.py`
3. **Run tests**: `pytest -v`
4. **Explore**: Check out `src/simulation/` modules

## File Overview

| File | Purpose |
|------|---------|
| `src/simulation/price_process.py` | Geometric Brownian Motion |
| `src/simulation/order_flow.py` | Poisson order arrivals |
| `src/simulation/accounting.py` | Portfolio & PnL tracking |
| `src/simulation/market_simulator.py` | Main simulation engine |
| `examples/basic_simulation.py` | Working example |

## Quick Test

```python
from src.simulation import create_gbm, OrderFlowGenerator, OrderFlowConfig, MarketSimulator, SimulationConfig

# Create components
price = create_gbm(S0=100.0, sigma=0.02, seed=42)
flow = OrderFlowGenerator(OrderFlowConfig(A=10.0, kappa=0.5), seed=42)

# Define strategy
class SimpleStrategy:
    def get_quotes(self, state):
        mid = state['mid_price']
        return mid - 1.0, mid + 1.0  # $1 spread

# Run simulation
results = MarketSimulator.run_simulation(
    price, flow, SimpleStrategy(), SimulationConfig(n_steps=100)
)

print(f"Final PnL: ${results.final_pnl:.2f}")
print(f"Trades: {results.n_trades}")
```

## GitHub

Repository name: **`market-making-research`**

**Description:**
> Advanced market-making research engine quantifying adverse selection costs with VPIN toxicity detection. Implements Avellaneda-Stoikov optimal quoting.

**Topics:** `quantitative-finance`, `market-making`, `adverse-selection`, `python`, `research`

---

**Status**: Phase 1 ✅ Complete

See `PHASE1_COMPLETE.md` for detailed documentation.

