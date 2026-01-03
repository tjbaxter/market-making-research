"""Shared configuration for all experiments."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Global configuration for experiments."""
    
    # Simulation parameters
    n_simulations: int = 100
    n_steps: int = 1000
    seed_base: int = 42
    
    # Price process
    S0: float = 100.0
    sigma: float = 0.02
    dt: float = 1.0 / 252.0
    
    # Order flow
    A: float = 10.0
    kappa: float = 0.5
    
    # Strategy parameters
    naive_spread: float = 1.0
    inventory_spread: float = 1.0
    inventory_penalty: float = 0.02
    as_risk_aversion: float = 0.1
    
    # Toxicity
    toxicity_factor: float = 0.5
    
    # VPIN
    vpin_bucket_size: int = 5000
    vpin_n_buckets: int = 50
    vpin_threshold: float = 0.7
    
    # Output paths
    results_dir: Path = Path("results")
    figures_dir: Path = Path("results/figures")
    
    def __post_init__(self):
        """Create output directories."""
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)


# Default configuration
DEFAULT_CONFIG = ExperimentConfig()

