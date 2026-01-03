"""
Portfolio accounting and PnL tracking module.
"""

import numpy as np
import pandas as pd
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class Trade:
    """Represents a completed trade."""
    
    timestamp: float
    side: str           # 'buy' or 'sell'
    price: float
    size: int
    mid_price: float
    inventory_before: int


@dataclass
class Portfolio:
    """Tracks market maker portfolio state."""
    
    initial_cash: float = 0.0
    commission_rate: float = 0.0001
    
    cash: float = field(default=0.0, init=False)
    inventory: int = field(default=0, init=False)
    trades: List[Trade] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Initialize cash to initial value."""
        self.cash = self.initial_cash
    
    def buy(self, price: float, size: int, mid_price: float):
        """
        Execute buy order (market maker sells to incoming market order).
        
        Args:
            price: Execution price
            size: Order size
            mid_price: Current mid price
        """
        gross = price * size
        commission = gross * self.commission_rate
        net = gross - commission
        
        self.cash += net
        self.inventory -= size
        
        trade = Trade(
            timestamp=len(self.trades),
            side='sell',
            price=price,
            size=size,
            mid_price=mid_price,
            inventory_before=self.inventory + size
        )
        self.trades.append(trade)
    
    def sell(self, price: float, size: int, mid_price: float):
        """
        Execute sell order (market maker buys from incoming market order).
        
        Args:
            price: Execution price
            size: Order size
            mid_price: Current mid price
        """
        gross = price * size
        commission = gross * self.commission_rate
        total_cost = gross + commission
        
        self.cash -= total_cost
        self.inventory += size
        
        trade = Trade(
            timestamp=len(self.trades),
            side='buy',
            price=price,
            size=size,
            mid_price=mid_price,
            inventory_before=self.inventory - size
        )
        self.trades.append(trade)
    
    def calculate_pnl(self, current_price: float) -> float:
        """
        Calculate total PnL (realized + unrealized).
        
        Args:
            current_price: Current market price
            
        Returns:
            Total PnL
        """
        realized_pnl = self.cash - self.initial_cash
        unrealized_pnl = self.inventory * current_price
        return realized_pnl + unrealized_pnl
    
    def decompose_pnl(self) -> Dict[str, float]:
        """
        Decompose PnL into:
        1. Spread capture
        2. Inventory timing
        3. Adverse selection
        
        Returns:
            Dictionary with PnL components
        """
        if not self.trades:
            return {
                'spread_capture': 0.0,
                'inventory_timing': 0.0,
                'adverse_selection': 0.0,
                'total': 0.0
            }
        
        spread_capture = 0.0
        
        for trade in self.trades:
            if trade.side == 'buy':
                # Bought below mid
                spread_capture += (trade.mid_price - trade.price) * trade.size
            else:
                # Sold above mid
                spread_capture += (trade.price - trade.mid_price) * trade.size
        
        final_price = self.trades[-1].mid_price
        total_pnl = self.calculate_pnl(final_price)
        
        # Simplified decomposition
        inventory_pnl = 0.0
        adverse_selection = total_pnl - spread_capture - inventory_pnl
        
        return {
            'spread_capture': spread_capture,
            'inventory_timing': inventory_pnl,
            'adverse_selection': adverse_selection,
            'total': total_pnl
        }
    
    def get_trade_df(self) -> pd.DataFrame:
        """
        Export trades as DataFrame.
        
        Returns:
            DataFrame with trade history
        """
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame([
            {
                'timestamp': t.timestamp,
                'side': t.side,
                'price': t.price,
                'size': t.size,
                'mid_price': t.mid_price,
                'inventory_before': t.inventory_before
            }
            for t in self.trades
        ])
    
    def reset(self):
        """Reset portfolio to initial state."""
        self.cash = self.initial_cash
        self.inventory = 0
        self.trades = []

