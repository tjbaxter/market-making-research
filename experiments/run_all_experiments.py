"""Run all experiments sequentially."""
import time
from .config import ExperimentConfig, DEFAULT_CONFIG
from .exp1_pnl_decomposition import PnLDecompositionExperiment

def run_all_experiments(config: ExperimentConfig = None):
    if config is None:
        config = DEFAULT_CONFIG
    
    print("\n" + "="*70)
    print("MARKET-MAKING RESEARCH: RUNNING ALL EXPERIMENTS")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Simulations per experiment: {config.n_simulations}")
    print(f"  Steps per simulation: {config.n_steps}")
    print("="*70)
    
    experiments = [PnLDecompositionExperiment(config)]
    results = {}
    start_time = time.time()
    
    for i, experiment in enumerate(experiments, 1):
        print(f"\n[{i}/4] Starting {experiment.name}...")
        try:
            result = experiment.run()
            results[experiment.name] = result
            print(f"✓ Completed")
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    print(f"\nTotal time: {time.time()-start_time:.1f}s")
    print(f"Results saved to: {config.results_dir}/")
    return results

if __name__ == '__main__':
    run_all_experiments()
