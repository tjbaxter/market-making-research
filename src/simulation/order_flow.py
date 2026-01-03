"""
Order flow simulation module.

Models market order arrivals using Poisson process with exponential fill probability.
"""

import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class FlowRegime(Enum):
    """Order flow toxicity regimes."""
    BENIGN = "benign"
    TOXIC = "toxic"


@dataclass
class OrderFlowConfig:
    """Configuration for order flow simulation."""
    
    A: float = 10.0              # Baseline arrival rate
    kappa: float = 0.5           # Liquidity parameter (spread sensitivity)
    toxicity_factor: float = 0.0 # How much informed trading increases fills
    min_tick: float = 0.01       # Minimum tick size


@dataclass
class Order:
    """Represents a market order."""
    
    side: str              # 'buy' or 'sell'
    size: int              # Number of shares
    timestamp: float       # When order arrived
    filled_price: float    # Price at which order filled


class OrderFlowGenerator:
    """
    Generates market orders using Poisson arrival process.
    
    Fill probability follows exponential model:
        λ_bid = A * exp(-κ * δ_bid)
        λ_ask = A * exp(-κ * δ_ask)
    
    References:
        Avellaneda & Stoikov (2008), "High-frequency trading in a limit order book"
    """
    
    def __init__(self, config: OrderFlowConfig, seed: Optional[int] = None):
        """
        Initialize order flow generator.
        
        Args:
            config: Order flow configuration
            seed: Random seed for reproducibility
        """
        self.config = config
        self.regime = FlowRegime.BENIGN
        self.rng = np.random.RandomState(seed)
        self.order_history: List[Order] = []
        self.time = 0.0
    
    def set_regime(self, regime: FlowRegime):
        """Set the current order flow regime."""
        self.regime = regime
    
    def calculate_fill_intensity(
        self, 
        bid: float, 
        ask: float, 
        mid_price: float
    ) -> Tuple[float, float]:
        """
        Calculate Poisson intensities for bid/ask fills.
        
        Args:
            bid: Bid quote price
            ask: Ask quote price
            mid_price: Current mid price
            
        Returns:
            Tuple of (lambda_bid, lambda_ask) intensities
        """
        delta_bid = max(mid_price - bid, 0.0)
        delta_ask = max(ask - mid_price, 0.0)
        
        lambda_bid = self.config.A * np.exp(-self.config.kappa * delta_bid)
        lambda_ask = self.config.A * np.exp(-self.config.kappa * delta_ask)
        
        return lambda_bid, lambda_ask
    
    def generate_orders(
        self,
        bid: float,
        ask: float,
        mid_price: float,
        future_price: Optional[float] = None,
        dt: float = 1.0/252.0
    ) -> Tuple[List[Order], List[Order]]:
        """
        Generate market orders for one time step.
        
        Args:
            bid: Current bid quote
            ask: Current ask quote
            mid_price: Current mid price
            future_price: Future price (for toxic flow)
            dt: Time step
            
        Returns:
            Tuple of (buy_orders, sell_orders)
        """
        lambda_bid, lambda_ask = self.calculate_fill_intensity(bid, ask, mid_price)
        
        # Toxic flow: informed traders predict price moves
        if self.regime == FlowRegime.TOXIC and future_price is not None:
            if future_price > mid_price:
                lambda_ask *= (1 + self.config.toxicity_factor)
            else:
                lambda_bid *= (1 + self.config.toxicity_factor)
        
        # Generate via Poisson
        n_buy_orders = self.rng.poisson(lambda_ask * dt)
        n_sell_orders = self.rng.poisson(lambda_bid * dt)
        
        buy_orders = [
            Order('buy', 100, self.time, ask)
            for _ in range(n_buy_orders)
        ]
        
        sell_orders = [
            Order('sell', 100, self.time, bid)
            for _ in range(n_sell_orders)
        ]
        
        self.order_history.extend(buy_orders + sell_orders)
        self.time += dt
        
        return buy_orders, sell_orders
    
    def get_recent_volume(self, window: int = 50) -> Tuple[float, float]:
        """
        Get recent buy/sell volume.
        
        Args:
            window: Number of recent orders to consider
            
        Returns:
            Tuple of (buy_volume, sell_volume)
        """
        recent = self.order_history[-window:] if len(self.order_history) > window else self.order_history
        
        buy_volume = sum(o.size for o in recent if o.side == 'buy')
        sell_volume = sum(o.size for o in recent if o.side == 'sell')
        
        return buy_volume, sell_volume
    
    def reset(self):
        """Reset order history."""
        self.order_history = []
        self.time = 0.0

