"""Tests for price process module."""

import pytest
import numpy as np
from src.simulation import create_gbm, PriceProcessConfig, GeometricBrownianMotion


def test_gbm_initialization():
    """Test GBM initializes correctly."""
    gbm = create_gbm(S0=100.0, seed=42)
    assert gbm.current_price == 100.0
    assert len(gbm.price_history) == 1


def test_gbm_step_positive():
    """Test GBM always produces positive prices."""
    gbm = create_gbm(S0=100.0, sigma=0.5, seed=42)
    
    for _ in range(1000):
        price = gbm.step()
        assert price > 0, "Price should always be positive"


def test_gbm_reproducibility():
    """Test GBM is reproducible with same seed."""
    gbm1 = create_gbm(S0=100.0, seed=42)
    gbm2 = create_gbm(S0=100.0, seed=42)
    
    path1 = gbm1.generate_path(100)
    path2 = gbm2.generate_path(100)
    
    np.testing.assert_array_equal(path1, path2)


def test_gbm_reset():
    """Test GBM resets correctly."""
    gbm = create_gbm(S0=100.0, seed=42)
    gbm.generate_path(50)
    
    gbm.reset()
    
    assert gbm.current_price == 100.0
    assert len(gbm.price_history) == 1


def test_gbm_with_jumps():
    """Test jump-diffusion model."""
    gbm = create_gbm(S0=100.0, with_jumps=True, seed=42)
    path = gbm.generate_path(1000)
    
    # Check for significant moves (likely jumps)
    log_returns = np.diff(np.log(path))
    assert np.any(np.abs(log_returns) > 0.05), "Should have some large moves from jumps"


def test_realized_volatility():
    """Test realized volatility calculation."""
    gbm = create_gbm(S0=100.0, sigma=0.02, seed=42)
    gbm.generate_path(100)
    
    realized_vol = gbm.get_realized_volatility(window=50)
    
    # Should be roughly in same order of magnitude as input vol
    assert 0.005 < realized_vol < 0.1, f"Realized vol {realized_vol} seems unreasonable"

