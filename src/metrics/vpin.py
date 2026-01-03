"""
VPIN (Volume-Synchronized Probability of Informed Trading) implementation.

Based on:
Easley, D., López de Prado, M. M., & O'Hara, M. (2012).
Flow toxicity and liquidity in a high-frequency world.
The Review of Financial Studies, 25(5), 1457-1493.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class VPINConfig:
    """
    Configuration for VPIN calculation.
    
    Attributes:
        bucket_size: Target volume per bucket (e.g., 10000 shares)
        n_buckets: Number of buckets to use in VPIN calculation (e.g., 50)
        classification_method: Method to classify buy/sell volume
            - 'bulk': Bulk Volume Classification (recommended)
            - 'tick': Tick rule (simpler, less accurate)
    """
    bucket_size: int = 10000
    n_buckets: int = 50
    classification_method: str = 'bulk'


class BulkVolumeClassifier:
    """
    Bulk Volume Classification for VPIN.
    
    Classifies volume within a bucket as buy or sell based on
    price movements. More accurate than tick rule for VPIN.
    
    Algorithm:
        V_buy = V * (ΔP / |ΔP|) * 0.5 * (1 + ΔP / |ΔP|)
        V_sell = V - V_buy
    
    Where:
        V = total volume in bucket
        ΔP = price change over bucket
    
    References:
        Easley, López de Prado & O'Hara (2012), Section 2.2
    """
    
    @staticmethod
    def classify(
        volume: float,
        price_start: float,
        price_end: float
    ) -> Tuple[float, float]:
        """
        Classify volume as buy/sell using bulk classification.
        
        Args:
            volume: Total volume in bucket
            price_start: Price at bucket start
            price_end: Price at bucket end
            
        Returns:
            (buy_volume, sell_volume)
        """
        if volume == 0:
            return 0.0, 0.0
        
        price_change = price_end - price_start
        
        if abs(price_change) < 1e-10:
            # No price movement -> split evenly
            return volume / 2, volume / 2
        
        # Bulk volume classification formula
        # If price increased: more buy volume
        # If price decreased: more sell volume
        if price_change > 0:
            buy_fraction = 0.5 + 0.5 * (price_change / abs(price_change))
        else:
            buy_fraction = 0.5 - 0.5 * (abs(price_change) / abs(price_change))
        
        buy_volume = volume * buy_fraction
        sell_volume = volume - buy_volume
        
        return buy_volume, sell_volume


class TickRuleClassifier:
    """
    Simple tick rule classifier.
    
    If price increased: classify as buy
    If price decreased: classify as sell
    If unchanged: use previous classification
    """
    
    @staticmethod
    def classify(
        volume: float,
        price_start: float,
        price_end: float,
        last_classification: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Classify volume using tick rule.
        
        Args:
            volume: Total volume
            price_start: Previous price
            price_end: Current price
            last_classification: Previous classification if unchanged
            
        Returns:
            (buy_volume, sell_volume)
        """
        if volume == 0:
            return 0.0, 0.0
        
        price_change = price_end - price_start
        
        if price_change > 0:
            return volume, 0.0
        elif price_change < 0:
            return 0.0, volume
        else:
            # Unchanged - split evenly or use last
            return volume / 2, volume / 2


class VPINCalculator:
    """
    Calculate VPIN (Volume-Synchronized Probability of Informed Trading).
    
    VPIN measures order flow toxicity by:
    1. Bucketing trades by volume (not time)
    2. Classifying each bucket's volume as buy/sell
    3. Computing volume imbalance over rolling window
    
    Formula:
        VPIN = (1/n) * Σ |V_buy - V_sell| / V_total
    
    Where summation is over n most recent buckets.
    
    High VPIN → High probability of informed trading (toxic flow)
    Low VPIN → Benign, uninformed flow
    
    Typical threshold: VPIN > 0.7 indicates high toxicity
    
    References:
        Easley, López de Prado & O'Hara (2012)
    """
    
    def __init__(self, config: VPINConfig):
        """
        Initialize VPIN calculator.
        
        Args:
            config: VPIN configuration
        """
        self.config = config
        
        # Storage for buckets
        self.buckets: deque = deque(maxlen=config.n_buckets)
        
        # Current bucket being filled
        self.current_bucket = {
            'volume': 0.0,
            'buy_volume': 0.0,
            'sell_volume': 0.0,
            'price_start': None,
            'price_end': None
        }
        
        # Classifier
        if config.classification_method == 'bulk':
            self.classifier = BulkVolumeClassifier()
        else:
            self.classifier = TickRuleClassifier()
        
        # VPIN history
        self.vpin_history = []
    
    def update(
        self,
        volume: float,
        price: float,
        is_buy: Optional[bool] = None
    ):
        """
        Update VPIN with new trade.
        
        Args:
            volume: Trade volume
            price: Trade price
            is_buy: Optional direct classification (if known)
        """
        # Initialize bucket price if first trade
        if self.current_bucket['price_start'] is None:
            self.current_bucket['price_start'] = price
        
        # Update current bucket
        self.current_bucket['volume'] += volume
        self.current_bucket['price_end'] = price
        
        # If we know classification, use it
        if is_buy is not None:
            if is_buy:
                self.current_bucket['buy_volume'] += volume
            else:
                self.current_bucket['sell_volume'] += volume
        
        # Check if bucket is full
        if self.current_bucket['volume'] >= self.config.bucket_size:
            self._finalize_bucket()
    
    def _finalize_bucket(self):
        """Complete current bucket and start new one."""
        # Classify volume if not already done
        if (self.current_bucket['buy_volume'] == 0 and 
            self.current_bucket['sell_volume'] == 0):
            
            buy_vol, sell_vol = self.classifier.classify(
                self.current_bucket['volume'],
                self.current_bucket['price_start'],
                self.current_bucket['price_end']
            )
            
            self.current_bucket['buy_volume'] = buy_vol
            self.current_bucket['sell_volume'] = sell_vol
        
        # Store bucket
        self.buckets.append({
            'volume': self.current_bucket['volume'],
            'buy_volume': self.current_bucket['buy_volume'],
            'sell_volume': self.current_bucket['sell_volume']
        })
        
        # Calculate VPIN if we have enough buckets
        if len(self.buckets) >= self.config.n_buckets:
            vpin = self._calculate_vpin()
            self.vpin_history.append(vpin)
        
        # Reset current bucket
        self.current_bucket = {
            'volume': 0.0,
            'buy_volume': 0.0,
            'sell_volume': 0.0,
            'price_start': None,
            'price_end': None
        }
    
    def _calculate_vpin(self) -> float:
        """
        Calculate VPIN from recent buckets.
        
        Returns:
            VPIN value (0 to 1)
        """
        if len(self.buckets) < self.config.n_buckets:
            return 0.0
        
        # Sum over n most recent buckets
        total_volume = 0.0
        total_imbalance = 0.0
        
        for bucket in list(self.buckets)[-self.config.n_buckets:]:
            volume = bucket['volume']
            imbalance = abs(bucket['buy_volume'] - bucket['sell_volume'])
            
            total_volume += volume
            total_imbalance += imbalance
        
        if total_volume == 0:
            return 0.0
        
        # VPIN = average imbalance / average volume
        vpin = total_imbalance / total_volume
        
        return vpin
    
    def get_current_vpin(self) -> float:
        """
        Get most recent VPIN value.
        
        Returns:
            Current VPIN (0 if not enough data)
        """
        if len(self.vpin_history) == 0:
            return 0.0
        return self.vpin_history[-1]
    
    def get_vpin_series(self) -> np.ndarray:
        """
        Get complete VPIN time series.
        
        Returns:
            Array of VPIN values
        """
        return np.array(self.vpin_history)
    
    def is_toxic(self, threshold: float = 0.7) -> bool:
        """
        Check if current flow is toxic.
        
        Args:
            threshold: VPIN threshold for toxicity
            
        Returns:
            True if VPIN exceeds threshold
        """
        current_vpin = self.get_current_vpin()
        return current_vpin > threshold
    
    def reset(self):
        """Reset calculator state."""
        self.buckets.clear()
        self.vpin_history = []
        self.current_bucket = {
            'volume': 0.0,
            'buy_volume': 0.0,
            'sell_volume': 0.0,
            'price_start': None,
            'price_end': None
        }


def calculate_vpin_from_trades(
    trades_df: pd.DataFrame,
    bucket_size: int = 10000,
    n_buckets: int = 50
) -> np.ndarray:
    """
    Calculate VPIN from a DataFrame of trades.
    
    Args:
        trades_df: DataFrame with columns ['volume', 'price', 'is_buy']
        bucket_size: Target volume per bucket
        n_buckets: Number of buckets for VPIN calculation
        
    Returns:
        Array of VPIN values
    """
    config = VPINConfig(
        bucket_size=bucket_size,
        n_buckets=n_buckets,
        classification_method='bulk'
    )
    
    calculator = VPINCalculator(config)
    
    for _, trade in trades_df.iterrows():
        volume = trade['volume']
        price = trade['price']
        is_buy = trade.get('is_buy', None)
        
        calculator.update(volume, price, is_buy)
    
    return calculator.get_vpin_series()


def calculate_vpin_from_order_flow(
    buy_orders: List,
    sell_orders: List,
    prices: np.ndarray,
    bucket_size: int = 10000,
    n_buckets: int = 50
) -> np.ndarray:
    """
    Calculate VPIN from order flow simulation.
    
    Args:
        buy_orders: List of buy orders (per time step)
        sell_orders: List of sell orders (per time step)
        prices: Price series
        bucket_size: Target volume per bucket
        n_buckets: Number of buckets
        
    Returns:
        Array of VPIN values
    """
    config = VPINConfig(
        bucket_size=bucket_size,
        n_buckets=n_buckets
    )
    
    calculator = VPINCalculator(config)
    
    for t in range(len(buy_orders)):
        price = prices[t]
        
        # Process buy orders
        for order in buy_orders[t]:
            calculator.update(order.size, price, is_buy=True)
        
        # Process sell orders
        for order in sell_orders[t]:
            calculator.update(order.size, price, is_buy=False)
    
    return calculator.get_vpin_series()

