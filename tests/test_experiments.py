"""Tests for experiments."""
import pytest
from experiments.config import ExperimentConfig
from experiments.exp1_pnl_decomposition import PnLDecompositionExperiment

def test_experiment_config():
    config = ExperimentConfig()
    assert config.n_simulations > 0
    assert config.n_steps > 0

def test_pnl_experiment_runs():
    config = ExperimentConfig(n_simulations=2, n_steps=100)
    experiment = PnLDecompositionExperiment(config)
    results = experiment.run()
    assert 'benign' in results
    assert 'toxic' in results

def test_experiment_creates_outputs():
    config = ExperimentConfig(n_simulations=2, n_steps=100)
    experiment = PnLDecompositionExperiment(config)
    experiment.run()
    assert (config.results_dir / f"{experiment.name}_summary.json").exists()
