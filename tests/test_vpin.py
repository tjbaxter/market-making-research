"""Tests for VPIN calculator."""

import pytest
import numpy as np
from src.metrics import VPINCalculator, VPINConfig, BulkVolumeClassifier


def test_vpin_initialization():
    """Test VPIN calculator initializes correctly."""
    config = VPINConfig(bucket_size=10000, n_buckets=50)
    calculator = VPINCalculator(config)
    
    assert calculator.get_current_vpin() == 0.0
    assert len(calculator.vpin_history) == 0


def test_bulk_volume_classifier_price_increase():
    """Test bulk classifier with price increase."""
    buy_vol, sell_vol = BulkVolumeClassifier.classify(
        volume=1000,
        price_start=100.0,
        price_end=101.0  # Price increased
    )
    
    # Should classify more as buy
    assert buy_vol > sell_vol
    assert buy_vol + sell_vol == pytest.approx(1000)


def test_bulk_volume_classifier_price_decrease():
    """Test bulk classifier with price decrease."""
    buy_vol, sell_vol = BulkVolumeClassifier.classify(
        volume=1000,
        price_start=100.0,
        price_end=99.0  # Price decreased
    )
    
    # Should classify more as sell
    assert sell_vol > buy_vol
    assert buy_vol + sell_vol == pytest.approx(1000)


def test_bulk_volume_classifier_no_change():
    """Test bulk classifier with no price change."""
    buy_vol, sell_vol = BulkVolumeClassifier.classify(
        volume=1000,
        price_start=100.0,
        price_end=100.0  # No change
    )
    
    # Should split evenly
    assert buy_vol == pytest.approx(500)
    assert sell_vol == pytest.approx(500)


def test_vpin_bucket_filling():
    """Test VPIN bucket filling mechanism."""
    config = VPINConfig(bucket_size=1000, n_buckets=5)
    calculator = VPINCalculator(config)
    
    # Fill first bucket
    for _ in range(10):
        calculator.update(volume=100, price=100.0)
    
    # Should have completed one bucket
    assert len(calculator.buckets) == 1


def test_vpin_calculation_balanced_flow():
    """Test VPIN with balanced buy/sell flow."""
    config = VPINConfig(bucket_size=1000, n_buckets=5)
    calculator = VPINCalculator(config)
    
    # Alternate buy/sell with balanced volumes
    for i in range(60):
        is_buy = (i % 2 == 0)
        calculator.update(volume=100, price=100.0, is_buy=is_buy)
    
    # VPIN should be low (balanced flow)
    vpin = calculator.get_current_vpin()
    assert vpin < 0.3


def test_vpin_calculation_imbalanced_flow():
    """Test VPIN with imbalanced buy flow."""
    config = VPINConfig(bucket_size=1000, n_buckets=5)
    calculator = VPINCalculator(config)
    
    # Mostly buys
    for i in range(60):
        is_buy = (i % 5 != 0)  # 80% buys
        calculator.update(volume=100, price=100.0, is_buy=is_buy)
    
    # VPIN should be high (imbalanced flow)
    vpin = calculator.get_current_vpin()
    assert vpin > 0.5


def test_vpin_toxicity_detection():
    """Test VPIN toxicity threshold."""
    config = VPINConfig(bucket_size=1000, n_buckets=5)
    calculator = VPINCalculator(config)
    
    # Create very imbalanced flow
    for i in range(60):
        calculator.update(volume=100, price=100.0, is_buy=True)
    
    # Should be flagged as toxic
    assert calculator.is_toxic(threshold=0.7)


def test_vpin_reset():
    """Test VPIN calculator reset."""
    config = VPINConfig(bucket_size=1000, n_buckets=5)
    calculator = VPINCalculator(config)
    
    # Fill some buckets
    for i in range(60):
        calculator.update(volume=100, price=100.0)
    
    calculator.reset()
    
    assert len(calculator.buckets) == 0
    assert len(calculator.vpin_history) == 0
    assert calculator.get_current_vpin() == 0.0


def test_vpin_series():
    """Test VPIN time series generation."""
    config = VPINConfig(bucket_size=1000, n_buckets=5)
    calculator = VPINCalculator(config)
    
    # Generate enough data for multiple VPIN calculations
    for i in range(100):
        calculator.update(volume=100, price=100.0 + i * 0.01, is_buy=(i % 2 == 0))
    
    series = calculator.get_vpin_series()
    
    # Should have multiple VPIN values
    assert len(series) > 0
    
    # All values should be between 0 and 1
    assert np.all(series >= 0)
    assert np.all(series <= 1)

