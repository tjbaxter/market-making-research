"""
Inventory-aware market-making strategy.

Adjusts quotes asymmetrically based on inventory position.
"""

import numpy as np
from typing import Tuple
from .base_strategy import BaseStrategy


class InventoryAwareStrategy(BaseStrategy):
    """
    Inventory-aware strategy with position skewing.
    
    Adjusts quotes to push inventory back to target:
        - If long (inventory > 0): lower ask to encourage selling
        - If short (inventory < 0): raise bid to encourage buying
    
    Quote skew is linear in inventory:
        skew = inventory * inventory_penalty
        bid = mid - base_spread/2 - skew
        ask = mid + base_spread/2 - skew
    
    Parameters:
        base_spread: Base spread width
        inventory_penalty: How aggressively to skew per unit inventory
        target_inventory: Target inventory level (default: 0)
    
    References:
        - Cartea, Á., Jaimungal, S., & Penalva, J. (2015).
          Algorithmic and high-frequency trading. Cambridge University Press.
    """
    
    def __init__(
        self, 
        base_spread: float = 1.0,
        inventory_penalty: float = 0.01,
        target_inventory: int = 0
    ):
        """
        Initialize inventory-aware strategy.
        
        Args:
            base_spread: Base bid-ask spread
            inventory_penalty: Penalty per unit inventory deviation
            target_inventory: Target inventory level
        """
        super().__init__(name="InventoryAware")
        
        self.base_spread = base_spread
        self.inventory_penalty = inventory_penalty
        self.target_inventory = target_inventory
        
        if base_spread <= 0:
            raise ValueError("Base spread must be positive")
        if inventory_penalty < 0:
            raise ValueError("Inventory penalty must be non-negative")
    
    def get_quotes(self, state: dict) -> Tuple[float, float]:
        """
        Generate inventory-skewed quotes.
        
        Args:
            state: Market state dictionary
            
        Returns:
            (bid, ask): Asymmetric quotes skewed by inventory
        """
        mid_price = state['mid_price']
        inventory = state['inventory']
        time = state.get('time', 0)
        
        # Calculate inventory deviation
        inventory_deviation = inventory - self.target_inventory
        
        # Calculate skew
        # Positive inventory -> negative skew (lower both quotes)
        # Negative inventory -> positive skew (raise both quotes)
        skew = inventory_deviation * self.inventory_penalty
        
        # Apply skew
        half_spread = self.base_spread / 2
        bid = mid_price - half_spread - skew
        ask = mid_price + half_spread - skew
        
        # Validate
        bid, ask = self._validate_quotes(bid, ask, mid_price)
        
        # Record
        self._record_quotes(time, bid, ask, mid_price)
        
        return bid, ask
    
    def __repr__(self):
        return (
            f"InventoryAwareStrategy("
            f"base_spread={self.base_spread}, "
            f"inventory_penalty={self.inventory_penalty})"
        )

