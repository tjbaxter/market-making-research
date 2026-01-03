"""Market-making research project."""

__version__ = "0.2.0"  # Phase 2: Trading Strategies

# Export strategies for convenience
from .strategies import (
    NaiveStrategy,
    InventoryAwareStrategy,
    AvellanedaStoikovStrategy,
    BaseStrategy,
    MarketState
)

__all__ = [
    'NaiveStrategy',
    'InventoryAwareStrategy',
    'AvellanedaStoikovStrategy',
    'BaseStrategy',
    'MarketState',
]

