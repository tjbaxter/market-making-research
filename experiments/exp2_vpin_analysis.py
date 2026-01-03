"""
Experiment 2: VPIN Analysis

Research Question:
    Does VPIN reliably predict subsequent adverse selection losses?

Hypothesis:
    High VPIN values (>0.7) precede periods of increased adverse selection.

Method:
    1. Run simulations with varying toxicity
    2. Calculate VPIN throughout
    3. Measure adverse selection in periods following high VPIN
    4. Compute correlation and predictive power

Expected Result:
    "When VPIN > 0.7, adverse selection costs increase by 3x in next 5 periods"
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
from tqdm import tqdm
from scipy import stats

from src.simulation import (
    create_gbm,
    OrderFlowGenerator,
    OrderFlowConfig,
    FlowRegime,
    MarketSimulator,
    SimulationConfig,
    Portfolio,
    SimulationResults
)
from src.strategies import AvellanedaStoikovStrategy
from src.metrics import VPINCalculator, VPINConfig

from .experiment_base import BaseExperiment
from .config import ExperimentConfig


class VPINAnalysisExperiment(BaseExperiment):
    """
    Experiment 2: Validate VPIN as toxicity predictor.
    
    Tests whether VPIN can reliably detect adverse selection
    before it impacts PnL.
    """
    
    def __init__(self, config: ExperimentConfig):
        super().__init__(config, "Experiment_2_VPIN_Analysis")
    
    def run(self) -> Dict:
        """Run VPIN analysis experiment."""
        print(f"\n{'='*70}")
        print(f"RUNNING: {self.name}")
        print(f"{'='*70}\n")
        
        # Run simulations with mixed toxicity
        print("Running simulations with mixed flow regimes...")
        vpin_data, pnl_data = self._run_mixed_simulations()
        
        # Analyze correlation
        print("\nAnalyzing VPIN-loss correlation...")
        correlation_results = self._analyze_correlation(vpin_data, pnl_data)
        
        # Test predictive power
        print("\nTesting predictive power...")
        predictive_results = self._test_predictive_power(vpin_data, pnl_data)
        
        # Combine results
        results = {
            'correlation': correlation_results,
            'predictive': predictive_results,
            'data': {
                'vpin': vpin_data,
                'pnl': pnl_data
            }
        }
        
        # Visualize
        self._create_visualizations(results)
        
        # Save
        self.save_results(results)
        self.print_summary({
            'correlation': correlation_results,
            'predictive': predictive_results
        })
        
        return results
    
    def _run_mixed_simulations(self) -> Tuple[List, List]:
        """
        Run simulations with alternating toxicity.
        
        Returns:
            (vpin_series, adverse_selection_series)
        """
        all_vpins = []
        all_adverse = []
        
        strategy = AvellanedaStoikovStrategy(
            risk_aversion=self.config.as_risk_aversion,
            volatility=self.config.sigma,
            kappa=self.config.kappa
        )
        
        for i in tqdm(range(self.config.n_simulations)):
            seed = self.config.seed_base + i
            
            # Setup
            price_process = create_gbm(
                S0=self.config.S0,
                sigma=self.config.sigma,
                seed=seed
            )
            
            # Alternate toxicity every 200 steps
            order_flow_config = OrderFlowConfig(
                A=self.config.A,
                kappa=self.config.kappa,
                toxicity_factor=self.config.toxicity_factor
            )
            order_flow = OrderFlowGenerator(order_flow_config, seed=seed)
            
            # VPIN calculator
            vpin_config = VPINConfig(
                bucket_size=self.config.vpin_bucket_size,
                n_buckets=self.config.vpin_n_buckets
            )
            vpin_calc = VPINCalculator(vpin_config)
            
            # Run simulation step by step to switch regimes
            sim_config = SimulationConfig(n_steps=self.config.n_steps, seed=seed)
            
            # Custom simulation loop
            result, vpin_series = self._run_with_vpin_tracking(
                price_process,
                order_flow,
                strategy,
                vpin_calc,
                sim_config
            )
            
            # Extract adverse selection per period
            adverse_series = self._extract_adverse_selection_series(result)
            
            all_vpins.append(vpin_series)
            all_adverse.append(adverse_series)
        
        return all_vpins, all_adverse
    
    def _run_with_vpin_tracking(
        self,
        price_process,
        order_flow,
        strategy,
        vpin_calc,
        config
    ) -> Tuple:
        """Run simulation with VPIN tracking."""
        price_process.reset()
        order_flow.reset()
        portfolio = Portfolio()
        vpin_series = []
        
        for t in range(config.n_steps):
            # Alternate regime every 200 steps
            if (t // 200) % 2 == 0:
                order_flow.set_regime(FlowRegime.BENIGN)
            else:
                order_flow.set_regime(FlowRegime.TOXIC)
            
            # Get mid price
            mid_price = price_process.current_price
            
            # Get quotes
            state = {
                'mid_price': mid_price,
                'inventory': portfolio.inventory,
                'time_remaining': config.n_steps - t,
                'time': t
            }
            bid, ask = strategy.get_quotes(state)
            
            # Generate next price
            next_price = price_process.step()
            
            # Generate orders
            buy_orders, sell_orders = order_flow.generate_orders(
                bid=bid,
                ask=ask,
                mid_price=mid_price,
                future_price=next_price,
                dt=config.dt
            )
            
            # Execute trades & update VPIN
            for order in buy_orders:
                portfolio.buy(ask, order.size, mid_price)
                vpin_calc.update(order.size, ask, is_buy=True)
            
            for order in sell_orders:
                portfolio.sell(bid, order.size, mid_price)
                vpin_calc.update(order.size, bid, is_buy=False)
            
            # Record VPIN
            vpin_series.append(vpin_calc.get_current_vpin())
        
        # Create result object
        result = SimulationResults(
            prices=np.array(price_process.price_history),
            inventories=np.zeros(config.n_steps + 1),
            pnl=np.zeros(config.n_steps + 1),
            cash=np.zeros(config.n_steps + 1),
            trades_df=portfolio.get_trade_df(),
            pnl_decomposition=portfolio.decompose_pnl(),
            final_pnl=0.0,
            n_trades=len(portfolio.trades)
        )
        
        return result, np.array(vpin_series)
    
    def _extract_adverse_selection_series(self, result) -> np.ndarray:
        """Extract adverse selection costs over time."""
        # Simplified: use rolling window of trades
        trades = result.trades_df
        
        if trades.empty:
            return np.zeros(100)
        
        # Calculate adverse selection per 10-step window
        window_size = 10
        n_windows = self.config.n_steps // window_size
        adverse_series = np.zeros(n_windows)
        
        for i in range(n_windows):
            start_idx = i * window_size
            end_idx = (i + 1) * window_size
            
            window_trades = trades[
                (trades['timestamp'] >= start_idx) &
                (trades['timestamp'] < end_idx)
            ]
            
            if not window_trades.empty:
                # Simple adverse selection estimate
                adverse = sum(
                    abs(t['price'] - t['mid_price']) * t['size']
                    for _, t in window_trades.iterrows()
                )
                adverse_series[i] = adverse
        
        return adverse_series
    
    def _analyze_correlation(self, vpin_data: List, adverse_data: List) -> Dict:
        """
        Analyze correlation between VPIN and adverse selection.
        
        Args:
            vpin_data: List of VPIN series
            adverse_data: List of adverse selection series
            
        Returns:
            Correlation statistics
        """
        # Flatten all data
        all_vpin = np.concatenate([v for v in vpin_data if len(v) > 0])
        all_adverse = np.concatenate([a for a in adverse_data if len(a) > 0])
        
        # Match lengths
        min_len = min(len(all_vpin), len(all_adverse))
        all_vpin = all_vpin[:min_len]
        all_adverse = all_adverse[:min_len]
        
        # Calculate correlation
        correlation, p_value = stats.pearsonr(all_vpin, all_adverse)
        
        return {
            'correlation_coefficient': float(correlation),
            'p_value': float(p_value),
            'n_samples': len(all_vpin),
            'significant': p_value < 0.05
        }
    
    def _test_predictive_power(self, vpin_data: List, adverse_data: List) -> Dict:
        """
        Test if high VPIN predicts future losses.
        
        Args:
            vpin_data: List of VPIN series
            adverse_data: List of adverse selection series
            
        Returns:
            Predictive power metrics
        """
        threshold = self.config.vpin_threshold
        lookforward = 5  # Periods to look ahead
        
        high_vpin_losses = []
        low_vpin_losses = []
        
        for vpin_series, adverse_series in zip(vpin_data, adverse_data):
            if len(vpin_series) < lookforward or len(adverse_series) < lookforward:
                continue
            
            for t in range(len(vpin_series) - lookforward):
                vpin = vpin_series[t]
                
                # Future losses
                future_loss = np.mean(adverse_series[t:t+lookforward])
                
                if vpin > threshold:
                    high_vpin_losses.append(future_loss)
                else:
                    low_vpin_losses.append(future_loss)
        
        # Statistics
        mean_loss_high = np.mean(high_vpin_losses) if high_vpin_losses else 0
        mean_loss_low = np.mean(low_vpin_losses) if low_vpin_losses else 0
        
        ratio = mean_loss_high / (mean_loss_low + 1e-10)
        
        return {
            'mean_loss_when_high_vpin': float(mean_loss_high),
            'mean_loss_when_low_vpin': float(mean_loss_low),
            'loss_ratio': float(ratio),
            'n_high_vpin_samples': len(high_vpin_losses),
            'n_low_vpin_samples': len(low_vpin_losses),
            'finding': f"When VPIN > {threshold}, losses increase by {ratio:.1f}x"
        }
    
    def _create_visualizations(self, results: Dict):
        """Create visualization plots."""
        
        # Plot 1: VPIN vs Adverse Selection Scatter
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Scatter plot
        ax = axes[0]
        vpin_data = results['data']['vpin']
        adverse_data = results['data']['pnl']
        
        # Sample for plotting
        sample_vpin = vpin_data[0] if vpin_data else np.array([])
        sample_adverse = adverse_data[0] if adverse_data else np.array([])
        
        if len(sample_vpin) > 0 and len(sample_adverse) > 0:
            min_len = min(len(sample_vpin), len(sample_adverse))
            ax.scatter(
                sample_vpin[:min_len],
                sample_adverse[:min_len],
                alpha=0.5,
                s=10
            )
            ax.axvline(
                x=self.config.vpin_threshold,
                color='r',
                linestyle='--',
                label='Toxicity Threshold'
            )
            ax.set_xlabel('VPIN')
            ax.set_ylabel('Adverse Selection Loss')
            ax.set_title('VPIN vs Adverse Selection', fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Box plot comparison
        ax = axes[1]
        predictive = results['predictive']
        
        data_to_plot = [
            [predictive['mean_loss_when_low_vpin']] * 100,
            [predictive['mean_loss_when_high_vpin']] * 100
        ]
        
        ax.boxplot(data_to_plot, labels=['VPIN < 0.7', 'VPIN > 0.7'])
        ax.set_ylabel('Average Adverse Selection Loss')
        ax.set_title('Loss Distribution by VPIN Level', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(
            self.config.figures_dir / 'exp2_vpin_analysis.png',
            dpi=150,
            bbox_inches='tight'
        )
        plt.close()
        
        print(f"\nVisualizations saved to {self.config.figures_dir}/")

