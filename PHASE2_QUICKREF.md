# Phase 2 Quick Reference

## Strategy API

### Import

```python
from src.strategies import (
    NaiveStrategy,
    InventoryAwareStrategy,
    AvellanedaStoikovStrategy
)
```

### Usage Pattern

All strategies follow the same interface:

```python
# Create strategy
strategy = SomeStrategy(param1=value1, param2=value2)

# Define market state
state = {
    'mid_price': 100.0,
    'inventory': 50,
    'time': 10,
    'time_remaining': 90
}

# Get quotes
bid, ask = strategy.get_quotes(state)
```

## Strategy Comparison Table

| Strategy | Parameters | Inventory Control | Complexity | Best For |
|----------|-----------|-------------------|------------|----------|
| **Naive** | `spread_width` | None | Low | Baseline |
| **Inventory-Aware** | `base_spread`, `inventory_penalty` | Linear skewing | Medium | Practical use |
| **Avellaneda-Stoikov** | `risk_aversion`, `volatility`, `kappa` | Optimal (theory) | High | Research/sophisticated |

## Parameter Guides

### Naive Strategy

```python
NaiveStrategy(
    spread_width=1.0    # Bid-ask spread in dollars
)
```

**Typical values:** 0.5 - 3.0

### Inventory-Aware Strategy

```python
InventoryAwareStrategy(
    base_spread=1.0,           # Base spread when inventory = 0
    inventory_penalty=0.02,     # Skew per unit inventory
    target_inventory=0          # Target position
)
```

**Typical values:**
-`base_spread`: 0.5 - 2.0
-`inventory_penalty`: 0.001 - 0.05
-Higher penalty = more aggressive mean reversion

### Avellaneda-Stoikov Strategy

```python
AvellanedaStoikovStrategy(
    risk_aversion=0.1,     # Risk aversion coefficient γ
    volatility=0.02,       # Price volatility σ
    A=10.0,                # Order arrival intensity
    kappa=0.5,             # Liquidity parameter κ
    T=1000                 # Time horizon (optional)
)
```

**Typical values:**
-`risk_aversion`: 0.01 - 1.0 (higher = more conservative)
-`volatility`: Match your price process (e.g., 0.02 = 2%)
-`kappa`: Match your order flow (e.g., 0.5)
-`T`: Total simulation steps (None = infinite horizon)

## Running Tests

```bash
# All tests
pytest -v

# Only strategy tests
pytest tests/test_strategies.py -v

# Only integration tests
pytest tests/test_strategy_comparison.py -v

# Specific test
pytest tests/test_strategies.py::test_avellaneda_stoikov_reservation_price -v

# With coverage
pytest --cov=src.strategies tests/test_strategies.py
```

## Running Examples

```bash
# Basic simulation (Phase 1)
python examples/basic_simulation.py

# Strategy comparison (Phase 2)
python examples/strategy_comparison.py
```

## Key Formulas

### Inventory-Aware

```
skew = inventory * inventory_penalty
bid = mid - base_spread/2 - skew
ask = mid + base_spread/2 - skew
```

### Avellaneda-Stoikov

**Reservation Price:**
```
r = S - q * γ * σ * τ
```

**Optimal Spread:**
```
δ = (1/γ) * log(1 + γ/κ)
```

**Quotes:**
```
bid = r - δ
ask = r + δ
```

## Common Patterns

### Compare Multiple Strategies

```python
from src.simulation import create_gbm, OrderFlowGenerator, MarketSimulator, SimulationConfig
from src.simulation.order_flow import OrderFlowConfig
from src.strategies import NaiveStrategy, InventoryAwareStrategy, AvellanedaStoikovStrategy

strategies = {
    'Naive': NaiveStrategy(spread_width=1.0),
    'Inv-Aware': InventoryAwareStrategy(base_spread=1.0, inventory_penalty=0.02),
    'AS': AvellanedaStoikovStrategy(risk_aversion=0.1, volatility=0.02, kappa=0.5)
}

results = {}
for name, strategy in strategies.items():
    price = create_gbm(S0=100.0, sigma=0.02, seed=42)
    flow = OrderFlowGenerator(OrderFlowConfig(A=10.0, kappa=0.5), seed=42)
    config = SimulationConfig(n_steps=1000)
    
    results[name] = MarketSimulator.run_simulation(price, flow, strategy, config)
    print(f"{name}: PnL = ${results[name].final_pnl:.2f}")
```

### Analyze Quote Behavior

```python
strategy = AvellanedaStoikovStrategy(risk_aversion=0.1, volatility=0.02, kappa=0.5)

# Run simulation
results = run_simulation(strategy)

# Get quote history
quotes = strategy.get_quote_history()

# Extract data
spreads = [q['spread'] for q in quotes]
bids = [q['bid'] for q in quotes]
asks = [q['ask'] for q in quotes]

# Analyze
print(f"Average spread: ${np.mean(spreads):.3f}")
print(f"Spread std dev: ${np.std(spreads):.3f}")
```

### Parameter Sensitivity

```python
risk_aversions = [0.01, 0.05, 0.1, 0.5, 1.0]
results = []

for gamma in risk_aversions:
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=gamma,
        volatility=0.02,
        kappa=0.5
    )
    
    result = run_simulation(strategy)
    results.append({
        'gamma': gamma,
        'pnl': result.final_pnl,
        'trades': result.n_trades,
        'avg_inv': np.mean(np.abs(result.inventories))
    })

df = pd.DataFrame(results)
print(df)
```

## Troubleshooting

### Import Errors

```python
# If you get import errors, make sure package is installed
pip install -e .

# Or add to sys.path manually
import sys
sys.path.insert(0, '.')
from src.strategies import NaiveStrategy
```

### Validation Errors

```python
# All strategies validate parameters
try:
    strategy = NaiveStrategy(spread_width=-1.0)
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

### Quote Issues

If quotes seem unreasonable, check:
1. `mid_price` is positive
2. `inventory` is reasonable scale
3. Strategy parameters are appropriate

```python
# Strategies automatically validate quotes
bid, ask = strategy.get_quotes(state)
assert bid > 0
assert ask > 0
assert bid < ask
```

## Performance Tips

1. **Naive**: Start here for baseline
2. **Inventory-Aware**: Tune `inventory_penalty` based on your risk tolerance
3. **AS**: Calibrate parameters to match your market model

**Rule of thumb:**
-High volatility → wider spreads needed
-High liquidity (low kappa) → can quote tighter
-High risk aversion → wider spreads, less trading

## Next Steps

After Phase 2, you can:
1.  Compare strategy performance in different market conditions
2.  Tune parameters for your specific use case
3. ⏭ Add VPIN toxicity detection (Phase 3)
4. ⏭ Run parameter sensitivity experiments (Phase 4)
5. ⏭ Build interactive dashboard (Phase 5)

## References

-Avellaneda & Stoikov (2008): Original AS paper
-Cartea et al. (2015): Inventory management approaches
-Phase 2 tests: See `tests/test_strategies.py` for usage examples

