"""
Market simulator that ties together all components.
"""

import numpy as np
import pandas as pd
from typing import Protocol, Dict, List, Optional
from dataclasses import dataclass

from .price_process import GeometricBrownianMotion
from .order_flow import OrderFlowGenerator, FlowRegime
from .accounting import Portfolio


class TradingStrategy(Protocol):
    """Protocol for trading strategies."""
    
    def get_quotes(self, state: Dict) -> tuple[float, float]:
        """
        Generate bid/ask quotes.
        
        Args:
            state: Current market state
            
        Returns:
            (bid, ask) tuple
        """
        ...


@dataclass
class SimulationConfig:
    """Configuration for market simulation."""
    
    n_steps: int = 1000
    dt: float = 1.0/252.0
    seed: Optional[int] = None


@dataclass
class SimulationResults:
    """Results from a market simulation."""
    
    prices: np.ndarray
    inventories: np.ndarray
    pnl: np.ndarray
    cash: np.ndarray
    trades_df: pd.DataFrame
    pnl_decomposition: Dict[str, float]
    final_pnl: float
    n_trades: int


class MarketSimulator:
    """
    Runs complete market-making simulations.
    
    Orchestrates:
        - Price process evolution
        - Order flow generation
        - Strategy quote generation
        - Trade execution
        - PnL tracking
    """
    
    @staticmethod
    def run_simulation(
        price_process: GeometricBrownianMotion,
        order_flow: OrderFlowGenerator,
        strategy: TradingStrategy,
        config: SimulationConfig
    ) -> SimulationResults:
        """
        Run a complete simulation.
        
        Args:
            price_process: Price evolution model
            order_flow: Order arrival model
            strategy: Market-making strategy
            config: Simulation configuration
            
        Returns:
            SimulationResults with all metrics
        """
        # Reset components
        price_process.reset()
        order_flow.reset()
        portfolio = Portfolio()
        
        # Storage
        prices = np.zeros(config.n_steps + 1)
        inventories = np.zeros(config.n_steps + 1)
        pnl = np.zeros(config.n_steps + 1)
        cash = np.zeros(config.n_steps + 1)
        
        prices[0] = price_process.current_price
        
        for t in range(config.n_steps):
            # Get current mid price
            mid_price = price_process.current_price
            
            # Generate quotes from strategy
            state = {
                'mid_price': mid_price,
                'inventory': portfolio.inventory,
                'time_remaining': config.n_steps - t,
                'time': t
            }
            
            bid, ask = strategy.get_quotes(state)
            
            # Generate next price (for lookahead in toxic flow)
            next_price = price_process.step()
            
            # Generate orders
            buy_orders, sell_orders = order_flow.generate_orders(
                bid=bid,
                ask=ask,
                mid_price=mid_price,
                future_price=next_price,
                dt=config.dt
            )
            
            # Execute trades
            for order in buy_orders:
                portfolio.buy(ask, order.size, mid_price)
            
            for order in sell_orders:
                portfolio.sell(bid, order.size, mid_price)
            
            # Record state
            prices[t + 1] = next_price
            inventories[t + 1] = portfolio.inventory
            pnl[t + 1] = portfolio.calculate_pnl(next_price)
            cash[t + 1] = portfolio.cash
        
        # Compile results
        results = SimulationResults(
            prices=prices,
            inventories=inventories,
            pnl=pnl,
            cash=cash,
            trades_df=portfolio.get_trade_df(),
            pnl_decomposition=portfolio.decompose_pnl(),
            final_pnl=pnl[-1],
            n_trades=len(portfolio.trades)
        )
        
        return results

