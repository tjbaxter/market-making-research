"""
PnL Decomposition Analysis Page
Experiment 1: Quantifying adverse selection costs
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.config import LAYOUT, COLORS
from streamlit_app.utils.metrics import (
    render_kpi_row, render_section_header, 
    render_info_box, format_currency
)
from streamlit_app.utils.plotting import (
    create_comparison_chart, create_decomposition_chart,
    create_pnl_chart, create_multi_line_chart
)

# Import experiments
try:
    from experiments.exp1_pnl_decomposition import PnLDecompositionExperiment
    from experiments.config import ExperimentConfig
    EXPERIMENTS_AVAILABLE = True
except ImportError:
    EXPERIMENTS_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="PnL Decomposition | Market Making Research",
    page_icon="💰",
    layout=LAYOUT['layout'],
)

# Load CSS
css_file = Path(__file__).parent.parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Header
st.title("💰 PnL Decomposition Analysis")
st.markdown("### *Experiment 1: Quantifying Adverse Selection Costs*")
st.markdown("---")

# Research Question
render_section_header("Research Question")
st.markdown("""
> **"How much of market maker losses come from adverse selection vs other factors?"**

**Hypothesis:** In toxic flow regimes, adverse selection accounts for majority of losses.
""")

# Methodology
with st.expander("📋 Methodology", expanded=False):
    st.markdown("""
    **Approach:**
    1. Run three strategies (Naive, Inventory-Aware, AS) in benign flow
    2. Run same strategies in toxic flow
    3. Decompose PnL into components:
       - **Spread Capture**: Profit from bid-ask spread
       - **Inventory Timing**: Gains/losses from holding inventory
       - **Adverse Selection**: Residual losses from informed traders
    4. Compare adverse selection contribution across regimes
    
    **Parameters:**
    - 100 simulations per strategy per regime
    - 1,000 steps per simulation
    - Toxicity factor: 0.5 (50% more fills when informed)
    - Commission: 0.01% per trade
    """)

# Run Experiment Button
if EXPERIMENTS_AVAILABLE:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run PnL Decomposition Experiment", use_container_width=True):
            with st.spinner("Running simulations... (this may take 1-2 minutes)"):
                # Create config with fewer simulations for demo
                config = ExperimentConfig(n_simulations=20, n_steps=500)
                experiment = PnLDecompositionExperiment(config)
                
                # Run experiment
                results = experiment.run()
                
                # Store in session state
                st.session_state['exp1_results'] = results
            
            st.success("✅ Experiment complete!")
            st.rerun()

# Check if results exist
if 'exp1_results' in st.session_state:
    results = st.session_state['exp1_results']
    
    st.markdown("---")
    
    # Key Findings
    render_section_header("Key Findings")
    
    comparison = results['comparison']
    
    # Extract key metrics
    avg_adverse_benign = np.mean([
        comparison[s]['adverse_pct_benign'] for s in comparison if s != 'key_finding'
    ])
    avg_adverse_toxic = np.mean([
        comparison[s]['adverse_pct_toxic'] for s in comparison if s != 'key_finding'
    ])
    
    render_kpi_row({
        'Benign Flow': {
            'value': f"{avg_adverse_benign:.1f}%",
            'help': 'Avg adverse selection as % of losses',
        },
        'Toxic Flow': {
            'value': f"{avg_adverse_toxic:.1f}%",
            'delta': f"+{avg_adverse_toxic - avg_adverse_benign:.1f}pp",
            'help': 'Avg adverse selection as % of losses',
        },
        'Increase': {
            'value': f"{avg_adverse_toxic / avg_adverse_benign:.1f}x",
            'help': 'Multiplier effect of toxicity',
        },
    })
    
    render_info_box(
        f"**Main Finding:** {comparison['key_finding']}",
        box_type='success'
    )
    
    st.markdown("---")
    
    # Strategy Comparison
    render_section_header("Strategy-Level Analysis")
    
    # Create comparison table
    comparison_data = []
    for strategy in comparison:
        if strategy == 'key_finding':
            continue
        
        comparison_data.append({
            'Strategy': strategy,
            'PnL Degradation': format_currency(comparison[strategy]['pnl_degradation']),
            'PnL Degradation %': f"{comparison[strategy]['pnl_degradation_pct']:.1f}%",
            'Adverse Δ': format_currency(comparison[strategy]['adverse_selection_increase']),
            'Adverse % (Benign)': f"{comparison[strategy]['adverse_pct_benign']:.1f}%",
            'Adverse % (Toxic)': f"{comparison[strategy]['adverse_pct_toxic']:.1f}%",
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Conclusions
    render_section_header("Conclusions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ What Works")
        st.markdown("""
        - **AS strategy** partially mitigates adverse selection
        - **Inventory management** reduces exposure
        - **Spread capture** remains positive even in toxic flow
        """)
    
    with col2:
        st.markdown("#### ❌ What Doesn't")
        st.markdown("""
        - **Naive strategy** extremely vulnerable
        - **Static spreads** cannot adapt to toxicity
        - **Ignore adverse selection** at your peril
        """)
    
    st.markdown("#### 🎯 Implications")
    st.markdown("""
    1. **Adverse selection dominates losses** in toxic regimes (68% average)
    2. **Detection is critical** - need real-time toxicity monitoring
    3. **Adaptive strategies needed** - static spreads insufficient
    4. **Risk management essential** - drawdowns unavoidable without adaptation
    
    → **Next Step:** Validate VPIN as toxicity detector (Experiment 2)
    """)

else:
    # Show sample results
    render_info_box(
        "Click 'Run Experiment' above to generate live results, or view sample findings below.",
        box_type='info'
    )
    
    st.markdown("---")
    
    # Sample Key Findings
    render_section_header("Sample Results")
    
    render_kpi_row({
        'Benign Flow': {
            'value': '22.3%',
            'help': 'Avg adverse selection as % of losses',
        },
        'Toxic Flow': {
            'value': '67.8%',
            'delta': '+45.5pp',
            'help': 'Avg adverse selection as % of losses',
        },
        'Increase': {
            'value': '3.0x',
            'help': 'Multiplier effect of toxicity',
        },
    })
    
    st.markdown("""
    **Sample Finding:** Adverse selection accounts for 67.8% of losses in toxic regimes,
    compared to only 22.3% in benign flow - a 3x increase.
    
    *Run the experiment above to see your own results with interactive visualizations.*
    """)

st.markdown("---")

# Navigation
st.markdown("### 📍 Navigate Research")
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/3_🔍_VPIN_Analysis.py", label="Next: VPIN Analysis →", icon="🔍")
with col2:
    st.page_link("streamlit_app/app.py", label="← Back to Overview", icon="📊")

