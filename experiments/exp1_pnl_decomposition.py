"""
Experiment 1: PnL Decomposition

Research Question:
    How much of market maker losses come from adverse selection vs other factors?

Hypothesis:
    In toxic flow regimes, adverse selection accounts for majority of losses.

Method:
    1. Run strategies in benign flow
    2. Run strategies in toxic flow
    3. Decompose PnL into components
    4. Compare adverse selection contribution

Expected Result:
    "Adverse selection accounts for 60-70% of losses in toxic regimes"
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List
from tqdm import tqdm

from src.simulation import (
    create_gbm,
    OrderFlowGenerator,
    OrderFlowConfig,
    FlowRegime,
    MarketSimulator,
    SimulationConfig
)
from src.strategies import (
    NaiveStrategy,
    InventoryAwareStrategy,
    AvellanedaStoikovStrategy
)

from .experiment_base import BaseExperiment
from .config import ExperimentConfig


class PnLDecompositionExperiment(BaseExperiment):
    """
    Experiment 1: Quantify adverse selection costs.
    
    Compares PnL decomposition across:
    - Three strategies (Naive, Inventory-Aware, AS)
    - Two regimes (Benign, Toxic)
    - Multiple runs for statistical significance
    """
    
    def __init__(self, config: ExperimentConfig):
        super().__init__(config, "Experiment_1_PnL_Decomposition")
    
    def run(self) -> Dict:
        """Run PnL decomposition experiment."""
        print(f"\n{'='*70}")
        print(f"RUNNING: {self.name}")
        print(f"{'='*70}\n")
        
        strategies = self._create_strategies()
        results = {
            'benign': {},
            'toxic': {},
            'comparison': {}
        }
        
        # Run benign flow
        print("Running benign flow simulations...")
        results['benign'] = self._run_regime(
            strategies,
            FlowRegime.BENIGN,
            toxicity_factor=0.0
        )
        
        # Run toxic flow
        print("\nRunning toxic flow simulations...")
        results['toxic'] = self._run_regime(
            strategies,
            FlowRegime.TOXIC,
            toxicity_factor=self.config.toxicity_factor
        )
        
        # Compare
        print("\nAnalyzing results...")
        results['comparison'] = self._compare_regimes(
            results['benign'],
            results['toxic']
        )
        
        # Visualize
        self._create_visualizations(results)
        
        # Save
        self.save_results(results)
        self.print_summary(results['comparison'])
        
        return results
    
    def _create_strategies(self):
        """Create strategy instances."""
        return {
            'Naive': NaiveStrategy(
                spread_width=self.config.naive_spread
            ),
            'Inventory-Aware': InventoryAwareStrategy(
                base_spread=self.config.inventory_spread,
                inventory_penalty=self.config.inventory_penalty
            ),
            'Avellaneda-Stoikov': AvellanedaStoikovStrategy(
                risk_aversion=self.config.as_risk_aversion,
                volatility=self.config.sigma,
                kappa=self.config.kappa
            )
        }
    
    def _run_regime(
        self,
        strategies: Dict,
        regime: FlowRegime,
        toxicity_factor: float
    ) -> Dict:
        """
        Run all strategies in a given regime.
        
        Args:
            strategies: Dictionary of strategies
            regime: Flow regime
            toxicity_factor: Toxicity parameter
            
        Returns:
            Results dictionary
        """
        results = {}
        
        for name, strategy in strategies.items():
            print(f"  Running {name}...")
            
            # Run multiple simulations
            pnl_decomps = []
            final_pnls = []
            
            for i in tqdm(range(self.config.n_simulations), desc=f"  {name}"):
                # Setup
                seed = self.config.seed_base + i
                price_process = create_gbm(
                    S0=self.config.S0,
                    sigma=self.config.sigma,
                    dt=self.config.dt,
                    seed=seed
                )
                
                order_flow_config = OrderFlowConfig(
                    A=self.config.A,
                    kappa=self.config.kappa,
                    toxicity_factor=toxicity_factor
                )
                order_flow = OrderFlowGenerator(order_flow_config, seed=seed)
                order_flow.set_regime(regime)
                
                sim_config = SimulationConfig(
                    n_steps=self.config.n_steps,
                    seed=seed
                )
                
                # Run
                result = MarketSimulator.run_simulation(
                    price_process,
                    order_flow,
                    strategy,
                    sim_config
                )
                
                # Store
                pnl_decomps.append(result.pnl_decomposition)
                final_pnls.append(result.final_pnl)
            
            # Aggregate
            results[name] = {
                'mean_pnl': np.mean(final_pnls),
                'std_pnl': np.std(final_pnls),
                'mean_spread_capture': np.mean([d['spread_capture'] for d in pnl_decomps]),
                'mean_adverse_selection': np.mean([d['adverse_selection'] for d in pnl_decomps]),
                'mean_inventory_timing': np.mean([d['inventory_timing'] for d in pnl_decomps]),
                'pct_adverse_of_total': self._calculate_adverse_pct(pnl_decomps)
            }
        
        return results
    
    def _calculate_adverse_pct(self, decomps: List[Dict]) -> float:
        """
        Calculate adverse selection as % of total losses.
        
        Args:
            decomps: List of PnL decompositions
            
        Returns:
            Percentage (0-100)
        """
        total_adverse = sum(d['adverse_selection'] for d in decomps)
        total_losses = sum(
            abs(d['adverse_selection']) + abs(d['inventory_timing'])
            for d in decomps
        )
        
        if total_losses == 0:
            return 0.0
        
        return 100 * abs(total_adverse) / total_losses
    
    def _compare_regimes(self, benign: Dict, toxic: Dict) -> Dict:
        """
        Compare benign vs toxic results.
        
        Args:
            benign: Benign regime results
            toxic: Toxic regime results
            
        Returns:
            Comparison metrics
        """
        comparison = {}
        
        for strategy_name in benign.keys():
            benign_data = benign[strategy_name]
            toxic_data = toxic[strategy_name]
            
            # PnL degradation
            pnl_loss = benign_data['mean_pnl'] - toxic_data['mean_pnl']
            pnl_loss_pct = 100 * pnl_loss / (abs(benign_data['mean_pnl']) + 1e-10)
            
            # Adverse selection increase
            adverse_increase = (
                toxic_data['mean_adverse_selection'] -
                benign_data['mean_adverse_selection']
            )
            
            comparison[strategy_name] = {
                'pnl_degradation': pnl_loss,
                'pnl_degradation_pct': pnl_loss_pct,
                'adverse_selection_increase': adverse_increase,
                'adverse_pct_benign': benign_data['pct_adverse_of_total'],
                'adverse_pct_toxic': toxic_data['pct_adverse_of_total']
            }
        
        # Key finding
        avg_adverse_pct_toxic = np.mean([
            comparison[s]['adverse_pct_toxic']
            for s in comparison.keys()
        ])
        
        comparison['key_finding'] = (
            f"Adverse selection accounts for {avg_adverse_pct_toxic:.1f}% "
            f"of losses in toxic regimes"
        )
        
        return comparison
    
    def _create_visualizations(self, results: Dict):
        """Create visualization plots."""
        
        # Plot 1: PnL Decomposition Comparison
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        for idx, regime in enumerate(['benign', 'toxic']):
            ax = axes[idx]
            regime_data = results[regime]
            
            strategies = list(regime_data.keys())
            x = np.arange(len(strategies))
            width = 0.25
            
            spread = [regime_data[s]['mean_spread_capture'] for s in strategies]
            adverse = [regime_data[s]['mean_adverse_selection'] for s in strategies]
            inventory = [regime_data[s]['mean_inventory_timing'] for s in strategies]
            
            ax.bar(x - width, spread, width, label='Spread Capture', alpha=0.8)
            ax.bar(x, adverse, width, label='Adverse Selection', alpha=0.8)
            ax.bar(x + width, inventory, width, label='Inventory Timing', alpha=0.8)
            
            ax.set_title(f'{regime.capitalize()} Flow', fontweight='bold', fontsize=12)
            ax.set_ylabel('PnL ($)')
            ax.set_xticks(x)
            ax.set_xticklabels(strategies, rotation=15, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig(
            self.config.figures_dir / 'exp1_pnl_decomposition.png',
            dpi=150,
            bbox_inches='tight'
        )
        plt.close()
        
        # Plot 2: Adverse Selection Contribution
        fig, ax = plt.subplots(figsize=(10, 6))
        
        strategies = list(results['benign'].keys())
        benign_pct = [results['benign'][s]['pct_adverse_of_total'] for s in strategies]
        toxic_pct = [results['toxic'][s]['pct_adverse_of_total'] for s in strategies]
        
        x = np.arange(len(strategies))
        width = 0.35
        
        ax.bar(x - width/2, benign_pct, width, label='Benign', alpha=0.7)
        ax.bar(x + width/2, toxic_pct, width, label='Toxic', alpha=0.7)
        
        ax.set_title(
            'Adverse Selection as % of Total Losses',
            fontweight='bold',
            fontsize=14
        )
        ax.set_ylabel('Percentage (%)')
        ax.set_xticks(x)
        ax.set_xticklabels(strategies, rotation=15, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(
            self.config.figures_dir / 'exp1_adverse_contribution.png',
            dpi=150,
            bbox_inches='tight'
        )
        plt.close()
        
        print(f"\nVisualizations saved to {self.config.figures_dir}/")

