"""
Base strategy class and market state definition.

All strategies must inherit from BaseStrategy.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class MarketState:
    """
    Current market state passed to strategy.
    
    Attributes:
        mid_price: Current mid price
        inventory: Current inventory position (positive = long)
        time: Current time step
        time_remaining: Steps until end (for finite horizon)
        realized_volatility: Recent realized volatility (optional)
    """
    
    mid_price: float
    inventory: int
    time: int
    time_remaining: int
    realized_volatility: Optional[float] = None


class BaseStrategy(ABC):
    """
    Abstract base class for market-making strategies.
    
    All strategies must implement get_quotes() which returns
    bid and ask prices given current market state.
    """
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name for identification
        """
        self.name = name
        self._quote_history = []
    
    @abstractmethod
    def get_quotes(self, state: dict) -> Tuple[float, float]:
        """
        Generate bid and ask quotes.
        
        Args:
            state: Dictionary containing market state:
                - mid_price: Current mid price
                - inventory: Current inventory
                - time: Current time step
                - time_remaining: Steps remaining
                - realized_volatility: Optional recent vol
        
        Returns:
            (bid, ask): Tuple of bid and ask prices
        """
        pass
    
    def _validate_quotes(
        self, 
        bid: float, 
        ask: float, 
        mid_price: float
    ) -> Tuple[float, float]:
        """
        Validate and sanitize quotes.
        
        Ensures:
        - bid < ask
        - Both positive
        - Both within reasonable distance of mid
        
        Args:
            bid: Proposed bid price
            ask: Proposed ask price
            mid_price: Current mid price
            
        Returns:
            (bid, ask): Validated quotes
        """
        # Ensure positive
        bid = max(bid, 0.01)
        ask = max(ask, 0.01)
        
        # Ensure bid < ask
        if bid >= ask:
            spread = 0.01
            bid = mid_price - spread / 2
            ask = mid_price + spread / 2
        
        # Ensure reasonable distance from mid (max 50%)
        max_distance = mid_price * 0.5
        if abs(bid - mid_price) > max_distance:
            bid = mid_price - max_distance
        if abs(ask - mid_price) > max_distance:
            ask = mid_price + max_distance
        
        return bid, ask
    
    def _record_quotes(self, time: int, bid: float, ask: float, mid: float):
        """Record quotes for analysis."""
        self._quote_history.append({
            'time': time,
            'bid': bid,
            'ask': ask,
            'mid': mid,
            'spread': ask - bid
        })
    
    def get_quote_history(self):
        """Return quote history."""
        return self._quote_history
    
    def reset(self):
        """Reset strategy state."""
        self._quote_history = []

