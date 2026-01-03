"""
Advanced PnL decomposition and attribution tools.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PnLComponents:
    """Detailed PnL decomposition."""
    spread_capture: float
    inventory_pnl: float
    adverse_selection: float
    transaction_costs: float
    market_impact: float
    total_pnl: float


class PnLDecomposer:
    """
    Advanced PnL decomposition for market makers.
    
    Decomposes total PnL into:
    1. Spread capture: Profit from bid-ask spread
    2. Inventory PnL: Gains/losses from holding inventory
    3. Adverse selection: Losses from trading with informed traders
    4. Transaction costs: Commissions and fees
    5. Market impact: Cost of moving the market
    """
    
    @staticmethod
    def decompose(
        trades: List,
        prices: np.ndarray,
        initial_inventory: int = 0,
        commission_rate: float = 0.0001
    ) -> PnLComponents:
        """
        Decompose PnL from trade history.
        
        Args:
            trades: List of Trade objects
            prices: Price series for marking to market
            initial_inventory: Starting inventory
            commission_rate: Commission rate per trade
            
        Returns:
            PnLComponents with detailed attribution
        """
        if not trades:
            return PnLComponents(
                spread_capture=0.0,
                inventory_pnl=0.0,
                adverse_selection=0.0,
                transaction_costs=0.0,
                market_impact=0.0,
                total_pnl=0.0
            )
        
        # Calculate spread capture
        spread_capture = 0.0
        transaction_costs = 0.0
        
        for trade in trades:
            # Spread capture: distance from mid when trading
            if trade.side == 'buy':
                # We bought below mid
                spread_profit = (trade.mid_price - trade.price) * trade.size
            else:
                # We sold above mid
                spread_profit = (trade.price - trade.mid_price) * trade.size
            
            spread_capture += spread_profit
            
            # Transaction costs
            trade_value = trade.price * trade.size
            transaction_costs += trade_value * commission_rate
        
        # Calculate inventory PnL
        # This is the P&L from price movements while holding inventory
        inventory_pnl = 0.0
        current_inventory = initial_inventory
        
        for i, trade in enumerate(trades):
            if i == 0:
                continue
            
            # Price change since last trade
            price_change = prices[i] - prices[i-1]
            
            # PnL from holding inventory
            inventory_pnl += current_inventory * price_change
            
            # Update inventory
            if trade.side == 'buy':
                current_inventory += trade.size
            else:
                current_inventory -= trade.size
        
        # Final mark-to-market
        if len(prices) > len(trades):
            final_price = prices[-1]
            last_trade_price = trades[-1].mid_price
            inventory_pnl += current_inventory * (final_price - last_trade_price)
        
        # Total PnL
        total_pnl = spread_capture + inventory_pnl - transaction_costs
        
        # Adverse selection = residual
        # (Everything not explained by spread or inventory)
        adverse_selection = total_pnl - spread_capture - inventory_pnl + transaction_costs
        
        # Market impact (simplified - could be more sophisticated)
        market_impact = 0.0  # Placeholder
        
        return PnLComponents(
            spread_capture=spread_capture,
            inventory_pnl=inventory_pnl,
            adverse_selection=adverse_selection,
            transaction_costs=transaction_costs,
            market_impact=market_impact,
            total_pnl=total_pnl
        )


def decompose_pnl_detailed(
    portfolio,
    prices: np.ndarray
) -> Dict[str, float]:
    """
    Decompose portfolio PnL with detailed attribution.
    
    Args:
        portfolio: Portfolio object with trade history
        prices: Price series
        
    Returns:
        Dictionary with PnL components
    """
    decomposer = PnLDecomposer()
    components = decomposer.decompose(
        trades=portfolio.trades,
        prices=prices,
        commission_rate=portfolio.commission_rate
    )
    
    return {
        'spread_capture': components.spread_capture,
        'inventory_pnl': components.inventory_pnl,
        'adverse_selection': components.adverse_selection,
        'transaction_costs': components.transaction_costs,
        'market_impact': components.market_impact,
        'total_pnl': components.total_pnl
    }


def calculate_spread_capture(trades: List) -> float:
    """
    Calculate total spread captured from trades.
    
    Args:
        trades: List of Trade objects
        
    Returns:
        Total spread capture
    """
    spread_capture = 0.0
    
    for trade in trades:
        if trade.side == 'buy':
            spread_capture += (trade.mid_price - trade.price) * trade.size
        else:
            spread_capture += (trade.price - trade.mid_price) * trade.size
    
    return spread_capture


def calculate_adverse_selection(
    trades: List,
    prices: np.ndarray,
    lookback: int = 5
) -> float:
    """
    Calculate adverse selection costs.
    
    Adverse selection occurs when trading with informed traders.
    Measure: How much does price move against us after trading?
    
    Args:
        trades: List of trades
        prices: Price series
        lookback: Periods to look forward after trade
        
    Returns:
        Total adverse selection cost
    """
    adverse_selection = 0.0
    
    for i, trade in enumerate(trades):
        if i + lookback >= len(prices):
            break
        
        # Price at trade
        trade_price = trade.price
        
        # Price after lookback periods
        future_price = prices[min(i + lookback, len(prices) - 1)]
        
        # If we bought and price fell, we lost to adverse selection
        # If we sold and price rose, we lost to adverse selection
        if trade.side == 'buy':
            adverse_cost = (trade_price - future_price) * trade.size
        else:
            adverse_cost = (future_price - trade_price) * trade.size
        
        if adverse_cost > 0:
            adverse_selection += adverse_cost
    
    return adverse_selection


def analyze_pnl_over_time(
    trades: List,
    prices: np.ndarray,
    window: int = 100
) -> pd.DataFrame:
    """
    Analyze PnL decomposition over rolling windows.
    
    Args:
        trades: List of trades
        prices: Price series
        window: Window size for rolling analysis
        
    Returns:
        DataFrame with time-series PnL components
    """
    if not trades:
        return pd.DataFrame()
    
    results = []
    
    for i in range(window, len(trades)):
        window_trades = trades[i-window:i]
        window_prices = prices[i-window:i]
        
        decomposer = PnLDecomposer()
        components = decomposer.decompose(window_trades, window_prices)
        
        results.append({
            'time': i,
            'spread_capture': components.spread_capture,
            'inventory_pnl': components.inventory_pnl,
            'adverse_selection': components.adverse_selection,
            'total_pnl': components.total_pnl
        })
    
    return pd.DataFrame(results)

