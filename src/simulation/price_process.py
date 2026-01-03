"""
Price process simulation module.

Implements Geometric Brownian Motion with optional jump-diffusion.
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class PriceProcessConfig:
    """Configuration for price process simulation."""
    
    S0: float = 100.0          # Initial price
    mu: float = 0.0            # Drift (typically 0 for martingale)
    sigma: float = 0.02        # Volatility (2% daily vol)
    dt: float = 1.0/252.0      # Time step (daily)
    
    # Jump-diffusion parameters
    lambda_jump: float = 0.0   # Jump intensity (0 = no jumps)
    mu_jump: float = 0.0       # Mean jump size
    sigma_jump: float = 0.01   # Jump size std dev


class GeometricBrownianMotion:
    """
    Geometric Brownian Motion price simulator.
    
    Models price evolution as:
        dS_t = μ S_t dt + σ S_t dW_t
    
    In discrete time:
        S_{t+1} = S_t * exp((μ - σ²/2)dt + σ√dt * Z_t)
    
    where Z_t ~ N(0,1)
    
    References:
        Hull, J. C. (2018). Options, Futures, and Other Derivatives (10th ed.)
    """
    
    def __init__(self, config: PriceProcessConfig, seed: Optional[int] = None):
        """
        Initialize GBM price process.
        
        Args:
            config: Price process configuration
            seed: Random seed for reproducibility
        """
        self.config = config
        self.current_price = config.S0
        self.time = 0.0
        self.price_history = [config.S0]
        
        # Set random seed
        self.rng = np.random.RandomState(seed)
    
    def step(self) -> float:
        """
        Generate next price using GBM.
        
        Returns:
            Next price
        """
        dt = self.config.dt
        
        # Standard GBM step using log-normal formulation
        drift = (self.config.mu - 0.5 * self.config.sigma ** 2) * dt
        diffusion = self.config.sigma * np.sqrt(dt) * self.rng.normal(0, 1)
        
        # Jump component (if enabled)
        jump = 0.0
        if self.config.lambda_jump > 0:
            # Poisson arrivals
            n_jumps = self.rng.poisson(self.config.lambda_jump * dt)
            if n_jumps > 0:
                jump = self.rng.normal(
                    self.config.mu_jump, 
                    self.config.sigma_jump
                ) * n_jumps
        
        # Update price (ensures positive prices via exp)
        self.current_price *= np.exp(drift + diffusion + jump)
        
        # Record
        self.price_history.append(self.current_price)
        self.time += dt
        
        return self.current_price
    
    def generate_path(self, n_steps: int) -> np.ndarray:
        """
        Generate a complete price path.
        
        Args:
            n_steps: Number of time steps
            
        Returns:
            Array of prices
        """
        prices = np.zeros(n_steps + 1)
        prices[0] = self.current_price
        
        for i in range(n_steps):
            prices[i + 1] = self.step()
        
        return prices
    
    def reset(self):
        """Reset to initial state."""
        self.current_price = self.config.S0
        self.time = 0.0
        self.price_history = [self.config.S0]
    
    def get_realized_volatility(self, window: int = 50) -> float:
        """
        Calculate realized volatility from recent price history.
        
        Args:
            window: Number of periods to use
            
        Returns:
            Annualized realized volatility
        """
        if len(self.price_history) < window + 1:
            return self.config.sigma
        
        recent_prices = np.array(self.price_history[-window-1:])
        log_returns = np.diff(np.log(recent_prices))
        
        # Annualize
        return np.std(log_returns) * np.sqrt(1.0 / self.config.dt)


def create_gbm(
    S0: float = 100.0,
    sigma: float = 0.02,
    dt: float = 1.0/252.0,
    with_jumps: bool = False,
    seed: Optional[int] = None
) -> GeometricBrownianMotion:
    """
    Factory function to create GBM price process.
    
    Args:
        S0: Initial price
        sigma: Volatility
        dt: Time step
        with_jumps: Whether to include jumps
        seed: Random seed
        
    Returns:
        Configured GBM instance
    """
    config = PriceProcessConfig(
        S0=S0,
        mu=0.0,  # Always use martingale for market-making
        sigma=sigma,
        dt=dt,
        lambda_jump=0.1 if with_jumps else 0.0,
        mu_jump=0.0,
        sigma_jump=0.01
    )
    
    return GeometricBrownianMotion(config, seed=seed)

