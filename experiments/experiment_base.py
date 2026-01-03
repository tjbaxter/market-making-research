"""Base class for experiments with common utilities."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import json

from .config import ExperimentConfig


class BaseExperiment(ABC):
    """Abstract base class for experiments."""
    
    def __init__(self, config: ExperimentConfig, name: str):
        self.config = config
        self.name = name
        self.results = {}
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """Run the experiment."""
        pass
    
    def save_results(self, results: Dict[str, Any]):
        """Save results to disk."""
        self.results = results
        
        summary_path = self.config.results_dir / f"{self.name}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(self._make_json_serializable(results), f, indent=2)
        
        print(f"Results saved to {summary_path}")
    
    def _make_json_serializable(self, obj):
        """Convert numpy/pandas to JSON-serializable types."""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        else:
            return obj
    
    def print_summary(self, results: Dict[str, Any]):
        """Print experiment summary."""
        print("\n" + "=" * 70)
        print(f"{self.name.upper()} - RESULTS SUMMARY")
        print("=" * 70)
        
        for key, value in results.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            elif isinstance(value, (int, float)):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        
        print("=" * 70)

