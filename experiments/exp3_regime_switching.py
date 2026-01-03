"""
Experiment 3: Regime-Switching Strategy

Research Question:
    Does adaptive spread widening improve performance when VPIN detects toxicity?

Hypothesis:
    Widening spreads when VPIN > threshold reduces drawdowns while
    maintaining profitability.

Method:
    1. Implement adaptive strategy that widens spreads based on VPIN
    2. Compare to static AS strategy
    3. Measure: PnL, drawdown, Sharpe ratio, fill rates

Expected Result:
    "Adaptive strategy: 40% drawdown reduction, 18% Sharpe improvement"
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Tuple
from tqdm import tqdm
from dataclasses import dataclass

from src.simulation import (
    create_gbm,
    OrderFlowGenerator,
    OrderFlowConfig,
    FlowRegime,
    MarketSimulator,
    SimulationConfig,
    Portfolio
)
from src.strategies import AvellanedaStoikovStrategy
from src.metrics import VPINCalculator, VPINConfig, calculate_max_drawdown, calculate_sharpe_ratio

from .experiment_base import BaseExperiment
from .config import ExperimentConfig


class AdaptiveASStrategy:
    """
    Adaptive Avellaneda-Stoikov strategy.
    
    Widens spreads when VPIN exceeds threshold.
    """
    
    def __init__(
        self,
        base_strategy: AvellanedaStoikovStrategy,
        vpin_threshold: float = 0.7,
        spread_multiplier: float = 1.5
    ):
        """
        Initialize adaptive strategy.
        
        Args:
            base_strategy: Base AS strategy
            vpin_threshold: VPIN threshold for spread widening
            spread_multiplier: How much to widen (1.5 = 50% wider)
        """
        self.base_strategy = base_strategy
        self.vpin_threshold = vpin_threshold
        self.spread_multiplier = spread_multiplier
        self.current_vpin = 0.0
        self.name = "Adaptive-AS"
    
    def set_vpin(self, vpin: float):
        """Update current VPIN value."""
        self.current_vpin = vpin
    
    def get_quotes(self, state: dict) -> Tuple[float, float]:
        """Generate quotes with adaptive spreading."""
        # Get base quotes
        bid, ask = self.base_strategy.get_quotes(state)
        mid = state['mid_price']
        
        # If toxic, widen spread
        if self.current_vpin > self.vpin_threshold:
            # Calculate current spread
            spread = ask - bid
            
            # Widen spread symmetrically around mid
            new_spread = spread * self.spread_multiplier
            bid = mid - new_spread / 2
            ask = mid + new_spread / 2
        
        return bid, ask
    
    def reset(self):
        """Reset strategy."""
        self.base_strategy.reset()
        self.current_vpin = 0.0


class RegimeSwitchingExperiment(BaseExperiment):
    """
    Experiment 3: Test adaptive regime-switching strategy.
    
    Compares static vs adaptive AS strategy across metrics.
    """
    
    def __init__(self, config: ExperimentConfig):
        super().__init__(config, "Experiment_3_Regime_Switching")
    
    def run(self) -> Dict:
        """Run regime-switching experiment."""
        print(f"\n{'='*70}")
        print(f"RUNNING: {self.name}")
        print(f"{'='*70}\n")
        
        # Run static strategy
        print("Running static AS strategy...")
        static_results = self._run_strategy_batch(adaptive=False)
        
        # Run adaptive strategy
        print("\nRunning adaptive AS strategy...")
        adaptive_results = self._run_strategy_batch(adaptive=True)
        
        # Compare
        print("\nComparing strategies...")
        comparison = self._compare_strategies(static_results, adaptive_results)
        
        results = {
            'static': static_results,
            'adaptive': adaptive_results,
            'comparison': comparison
        }
        
        # Visualize
        self._create_visualizations(results)
        
        # Save
        self.save_results(results)
        self.print_summary(comparison)
        
        return results
    
    def _run_strategy_batch(self, adaptive: bool) -> Dict:
        """
        Run batch of simulations.
        
        Args:
            adaptive: Whether to use adaptive strategy
            
        Returns:
            Aggregated results
        """
        all_pnls = []
        all_drawdowns = []
        all_sharpes = []
        all_fill_rates = []
        all_inventories = []
        
        for i in tqdm(range(self.config.n_simulations)):
            seed = self.config.seed_base + i
            
            result = self._run_single_simulation(seed, adaptive)
            
            all_pnls.append(result['final_pnl'])
            all_drawdowns.append(result['max_drawdown'])
            all_sharpes.append(result['sharpe'])
            all_fill_rates.append(result['fill_rate'])
            all_inventories.append(result['avg_abs_inventory'])
        
        return {
            'mean_pnl': np.mean(all_pnls),
            'std_pnl': np.std(all_pnls),
            'mean_drawdown': np.mean(all_drawdowns),
            'std_drawdown': np.std(all_drawdowns),
            'mean_sharpe': np.mean(all_sharpes),
            'std_sharpe': np.std(all_sharpes),
            'mean_fill_rate': np.mean(all_fill_rates),
            'mean_inventory': np.mean(all_inventories),
            'all_pnls': all_pnls,
            'all_drawdowns': all_drawdowns,
            'all_sharpes': all_sharpes
        }
    
    def _run_single_simulation(self, seed: int, adaptive: bool) -> Dict:
        """Run single simulation with VPIN tracking."""
        # Setup
        price_process = create_gbm(
            S0=self.config.S0,
            sigma=self.config.sigma,
            seed=seed
        )
        
        order_flow_config = OrderFlowConfig(
            A=self.config.A,
            kappa=self.config.kappa,
            toxicity_factor=self.config.toxicity_factor
        )
        order_flow = OrderFlowGenerator(order_flow_config, seed=seed)
        
        # Strategy
        base_strategy = AvellanedaStoikovStrategy(
            risk_aversion=self.config.as_risk_aversion,
            volatility=self.config.sigma,
            kappa=self.config.kappa
        )
        
        if adaptive:
            strategy = AdaptiveASStrategy(
                base_strategy=base_strategy,
                vpin_threshold=self.config.vpin_threshold,
                spread_multiplier=1.5
            )
        else:
            strategy = base_strategy
        
        # VPIN
        vpin_config = VPINConfig(
            bucket_size=self.config.vpin_bucket_size,
            n_buckets=self.config.vpin_n_buckets
        )
        vpin_calc = VPINCalculator(vpin_config)
        
        # Run with regime switching
        portfolio = Portfolio()
        pnl_series = []
        fill_count = 0
        total_opportunities = 0
        
        for t in range(self.config.n_steps):
            # Switch regime every 200 steps
            if (t // 200) % 2 == 0:
                order_flow.set_regime(FlowRegime.BENIGN)
            else:
                order_flow.set_regime(FlowRegime.TOXIC)
            
            # Get price
            mid_price = price_process.current_price
            
            # Update VPIN in adaptive strategy
            if adaptive:
                strategy.set_vpin(vpin_calc.get_current_vpin())
            
            # Get quotes
            state = {
                'mid_price': mid_price,
                'inventory': portfolio.inventory,
                'time_remaining': self.config.n_steps - t,
                'time': t
            }
            bid, ask = strategy.get_quotes(state)
            
            # Step price
            next_price = price_process.step()
            
            # Generate orders
            buy_orders, sell_orders = order_flow.generate_orders(
                bid, ask, mid_price, next_price, self.config.dt
            )
            
            total_opportunities += 1
            
            # Execute
            for order in buy_orders:
                portfolio.buy(ask, order.size, mid_price)
                vpin_calc.update(order.size, ask, is_buy=True)
                fill_count += 1
            
            for order in sell_orders:
                portfolio.sell(bid, order.size, mid_price)
                vpin_calc.update(order.size, bid, is_buy=False)
                fill_count += 1
            
            # Record PnL
            pnl_series.append(portfolio.calculate_pnl(next_price))
        
        # Calculate metrics
        pnl_array = np.array(pnl_series)
        returns = np.diff(pnl_array)
        
        return {
            'final_pnl': pnl_array[-1],
            'max_drawdown': calculate_max_drawdown(pnl_array),
            'sharpe': calculate_sharpe_ratio(returns) if len(returns) > 0 else 0,
            'fill_rate': fill_count / max(total_opportunities, 1),
            'avg_abs_inventory': np.mean(np.abs([portfolio.inventory]))
        }
    
    def _compare_strategies(self, static: Dict, adaptive: Dict) -> Dict:
        """Compare static vs adaptive strategies."""
        
        # Percentage improvements
        pnl_change = ((adaptive['mean_pnl'] - static['mean_pnl']) / 
                      abs(static['mean_pnl'] + 1e-10)) * 100
        
        drawdown_reduction = ((static['mean_drawdown'] - adaptive['mean_drawdown']) / 
                              (static['mean_drawdown'] + 1e-10)) * 100
        
        sharpe_improvement = ((adaptive['mean_sharpe'] - static['mean_sharpe']) / 
                              abs(static['mean_sharpe'] + 1e-10)) * 100
        
        return {
            'static_mean_pnl': static['mean_pnl'],
            'adaptive_mean_pnl': adaptive['mean_pnl'],
            'pnl_change_pct': pnl_change,
            
            'static_mean_drawdown': static['mean_drawdown'],
            'adaptive_mean_drawdown': adaptive['mean_drawdown'],
            'drawdown_reduction_pct': drawdown_reduction,
            
            'static_mean_sharpe': static['mean_sharpe'],
            'adaptive_mean_sharpe': adaptive['mean_sharpe'],
            'sharpe_improvement_pct': sharpe_improvement,
            
            'static_fill_rate': static['mean_fill_rate'],
            'adaptive_fill_rate': adaptive['mean_fill_rate'],
            
            'key_finding': (
                f"{drawdown_reduction:.1f}% drawdown reduction, "
                f"{sharpe_improvement:.1f}% Sharpe improvement"
            )
        }
    
    def _create_visualizations(self, results: Dict):
        """Create visualization plots."""
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: PnL Distribution
        ax = axes[0, 0]
        ax.hist(results['static']['all_pnls'], bins=30, alpha=0.5, label='Static', density=True)
        ax.hist(results['adaptive']['all_pnls'], bins=30, alpha=0.5, label='Adaptive', density=True)
        ax.set_title('PnL Distribution', fontweight='bold')
        ax.set_xlabel('Final PnL ($)')
        ax.set_ylabel('Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Drawdown Distribution
        ax = axes[0, 1]
        ax.hist(results['static']['all_drawdowns'], bins=30, alpha=0.5, label='Static', density=True)
        ax.hist(results['adaptive']['all_drawdowns'], bins=30, alpha=0.5, label='Adaptive', density=True)
        ax.set_title('Drawdown Distribution', fontweight='bold')
        ax.set_xlabel('Max Drawdown')
        ax.set_ylabel('Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Sharpe Distribution
        ax = axes[1, 0]
        ax.hist(results['static']['all_sharpes'], bins=30, alpha=0.5, label='Static', density=True)
        ax.hist(results['adaptive']['all_sharpes'], bins=30, alpha=0.5, label='Adaptive', density=True)
        ax.set_title('Sharpe Ratio Distribution', fontweight='bold')
        ax.set_xlabel('Sharpe Ratio')
        ax.set_ylabel('Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Metric Comparison
        ax = axes[1, 1]
        comparison = results['comparison']
        
        metrics = ['PnL\nChange', 'Drawdown\nReduction', 'Sharpe\nImprovement']
        values = [
            comparison['pnl_change_pct'],
            comparison['drawdown_reduction_pct'],
            comparison['sharpe_improvement_pct']
        ]
        
        colors = ['green' if v > 0 else 'red' for v in values]
        ax.bar(metrics, values, color=colors, alpha=0.7)
        ax.set_title('Performance Improvements (%)', fontweight='bold')
        ax.set_ylabel('Percentage Change')
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(
            self.config.figures_dir / 'exp3_regime_switching.png',
            dpi=150,
            bbox_inches='tight'
        )
        plt.close()
        
        print(f"\nVisualizations saved to {self.config.figures_dir}/")

