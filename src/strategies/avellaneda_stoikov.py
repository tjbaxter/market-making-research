"""
Avellaneda-Stoikov optimal market-making strategy.

Implements the closed-form solution from:
Avellaneda, M., & Stoikov, S. (2008). High-frequency trading in a limit order book.
Quantitative Finance, 8(3), 217-224.
"""

import numpy as np
from typing import Tuple, Optional
from scipy.optimize import brentq
from .base_strategy import BaseStrategy


class AvellanedaStoikovStrategy(BaseStrategy):
    """
    Avellaneda-Stoikov optimal market-making strategy.
    
    Derives optimal bid/ask quotes by maximizing expected utility
    while accounting for:
    - Inventory risk
    - Time to horizon
    - Risk aversion
    - Market liquidity
    
    Key formulas:
    
    1. Reservation price:
        r = S - q * γ * σ² * (T - t)
    
    2. Optimal spread δ solves:
        γ / κ = exp(γ * δ) - 1
    
    3. Quotes:
        bid = r - δ
        ask = r + δ
    
    Where:
        S = mid price
        q = inventory
        γ = risk aversion parameter
        σ = volatility
        T - t = time remaining
        κ = liquidity parameter (from order flow model)
    
    Parameters:
        risk_aversion: Risk aversion coefficient γ (higher = more conservative)
        volatility: Price volatility σ
        A: Order flow baseline intensity
        kappa: Order flow liquidity parameter κ
        T: Total time horizon (for finite horizon)
    
    References:
        Avellaneda & Stoikov (2008), "High-frequency trading in a limit order book"
    """
    
    def __init__(
        self,
        risk_aversion: float = 0.1,
        volatility: float = 0.02,
        A: float = 10.0,
        kappa: float = 0.5,
        T: Optional[int] = None
    ):
        """
        Initialize Avellaneda-Stoikov strategy.
        
        Args:
            risk_aversion: Risk aversion γ (typical: 0.01-1.0)
            volatility: Price volatility σ (annual)
            A: Order arrival rate intensity
            kappa: Liquidity parameter (spread sensitivity)
            T: Time horizon (None = infinite horizon)
        """
        super().__init__(name="AvellanedaStoikov")
        
        self.gamma = risk_aversion
        self.sigma = volatility
        self.A = A
        self.kappa = kappa
        self.T = T
        
        # Validate parameters
        if risk_aversion <= 0:
            raise ValueError("Risk aversion must be positive")
        if volatility <= 0:
            raise ValueError("Volatility must be positive")
        if A <= 0:
            raise ValueError("Order arrival rate must be positive")
        if kappa <= 0:
            raise ValueError("Kappa must be positive")
        
        # Pre-compute optimal spread (time-independent component)
        self.optimal_spread = self._compute_optimal_spread()
    
    def _compute_optimal_spread(self) -> float:
        """
        Solve for optimal spread δ.
        
        Solves the implicit equation:
            γ / κ = exp(γ * δ) - 1
        
        Equivalently:
            δ = (1/γ) * log(1 + γ/κ)
        
        Returns:
            Optimal half-spread δ
        """
        # Closed-form approximation (valid for small γ/κ)
        if self.gamma / self.kappa < 0.1:
            # Linear approximation: δ ≈ 1/κ
            return 1.0 / self.kappa
        
        # Exact solution
        ratio = self.gamma / self.kappa
        
        # Solve: exp(γ*δ) - 1 - γ/κ = 0
        def equation(delta):
            return np.exp(self.gamma * delta) - 1 - ratio
        
        # Bracket the root
        delta_min = 0.0001
        delta_max = 10.0 / self.gamma
        
        try:
            optimal_delta = brentq(equation, delta_min, delta_max)
        except ValueError:
            # Fallback to approximation
            optimal_delta = np.log(1 + ratio) / self.gamma
        
        return optimal_delta
    
    def _compute_reservation_price(
        self,
        mid_price: float,
        inventory: int,
        time_remaining: int
    ) -> float:
        """
        Calculate reservation price r.
        
        Formula:
            r = S - q * γ * σ² * τ
        
        Where τ = T - t (time remaining)
        
        Args:
            mid_price: Current mid price S
            inventory: Current inventory q
            time_remaining: Steps to horizon
            
        Returns:
            Reservation price r
        """
        if self.T is None or time_remaining is None:
            # Infinite horizon: no time decay
            time_factor = 1.0
        else:
            # Finite horizon: scale by remaining time
            # Note: Using σ not σ² (common correction in practice)
            time_factor = time_remaining / self.T if self.T > 0 else 0
        
        # Reservation price
        reservation = mid_price - inventory * self.gamma * self.sigma * time_factor
        
        return reservation
    
    def get_quotes(self, state: dict) -> Tuple[float, float]:
        """
        Generate optimal AS quotes.
        
        Args:
            state: Market state dictionary containing:
                - mid_price: Current mid price
                - inventory: Current inventory
                - time_remaining: Optional steps remaining
                
        Returns:
            (bid, ask): Optimal quotes
        """
        mid_price = state['mid_price']
        inventory = state['inventory']
        time_remaining = state.get('time_remaining', None)
        time = state.get('time', 0)
        
        # Use realized volatility if available
        if 'realized_volatility' in state and state['realized_volatility'] is not None:
            current_vol = state['realized_volatility']
        else:
            current_vol = self.sigma
        
        # 1. Calculate reservation price
        reservation = self._compute_reservation_price(
            mid_price, inventory, time_remaining
        )
        
        # 2. Calculate optimal spread
        # (Could adjust based on current volatility)
        delta = self.optimal_spread
        
        # Adjust spread by volatility ratio if different from calibration
        vol_adjustment = current_vol / self.sigma if self.sigma > 0 else 1.0
        adjusted_delta = delta * vol_adjustment
        
        # 3. Place quotes symmetrically around reservation price
        bid = reservation - adjusted_delta
        ask = reservation + adjusted_delta
        
        # Validate
        bid, ask = self._validate_quotes(bid, ask, mid_price)
        
        # Record
        self._record_quotes(time, bid, ask, mid_price)
        
        return bid, ask
    
    def get_reservation_price(self, state: dict) -> float:
        """
        Get reservation price for analysis.
        
        Args:
            state: Market state dictionary
            
        Returns:
            Reservation price
        """
        return self._compute_reservation_price(
            state['mid_price'],
            state['inventory'],
            state.get('time_remaining', None)
        )
    
    def __repr__(self):
        return (
            f"AvellanedaStoikovStrategy("
            f"gamma={self.gamma}, "
            f"sigma={self.sigma}, "
            f"kappa={self.kappa})"
        )


# Convenience function
def create_as_strategy(
    risk_aversion: float = 0.1,
    volatility: float = 0.02,
    **kwargs
) -> AvellanedaStoikovStrategy:
    """
    Factory function to create AS strategy with sensible defaults.
    
    Args:
        risk_aversion: Risk aversion γ
        volatility: Price volatility σ
        **kwargs: Additional parameters
        
    Returns:
        Configured AS strategy
    """
    return AvellanedaStoikovStrategy(
        risk_aversion=risk_aversion,
        volatility=volatility,
        **kwargs
    )

