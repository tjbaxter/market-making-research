"""
Naive market-making strategy.

Posts constant spread around mid price with no inventory management.
"""

from typing import Tuple
from .base_strategy import BaseStrategy


class NaiveStrategy(BaseStrategy):
    """
    Naive constant-spread strategy.
    
    Simply quotes bid/ask at fixed distance from mid price:
        bid = mid - spread/2
        ask = mid + spread/2
    
    No inventory management - will accumulate large positions.
    Serves as baseline for comparison.
    
    Parameters:
        spread_width: Fixed spread width in dollars
    """
    
    def __init__(self, spread_width: float = 1.0):
        """
        Initialize naive strategy.
        
        Args:
            spread_width: Bid-ask spread width (default: $1.00)
        """
        super().__init__(name="Naive")
        self.spread_width = spread_width
        
        if spread_width <= 0:
            raise ValueError("Spread width must be positive")
    
    def get_quotes(self, state: dict) -> Tuple[float, float]:
        """
        Generate symmetric quotes around mid.
        
        Args:
            state: Market state dictionary
            
        Returns:
            (bid, ask): Symmetric quotes
        """
        mid_price = state['mid_price']
        time = state.get('time', 0)
        
        # Simple symmetric quotes
        half_spread = self.spread_width / 2
        bid = mid_price - half_spread
        ask = mid_price + half_spread
        
        # Validate
        bid, ask = self._validate_quotes(bid, ask, mid_price)
        
        # Record
        self._record_quotes(time, bid, ask, mid_price)
        
        return bid, ask
    
    def __repr__(self):
        return f"NaiveStrategy(spread_width={self.spread_width})"

