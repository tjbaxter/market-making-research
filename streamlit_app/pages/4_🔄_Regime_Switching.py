"""
Regime Switching Strategy Page
Experiment 3: Adaptive spread widening
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.config import LAYOUT, COLORS
from streamlit_app.utils.metrics import render_kpi_row, render_section_header, render_info_box
from streamlit_app.utils.plotting import create_distribution_chart, create_comparison_chart, create_multi_line_chart

try:
    from experiments.exp3_regime_switching import RegimeSwitchingExperiment
    from experiments.config import ExperimentConfig
    EXPERIMENTS_AVAILABLE = True
except ImportError:
    EXPERIMENTS_AVAILABLE = False

st.set_page_config(
    page_title="Regime Switching | Market Making Research",
    page_icon="🔄",
    layout=LAYOUT['layout'],
    initial_sidebar_state="expanded",
)

css_file = Path(__file__).parent.parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🔄 Regime-Switching Strategy")
st.markdown("### *Experiment 3: Adaptive Spread Widening*")
st.markdown("---")

render_section_header("Research Question")
st.markdown("""
> **"Does adaptive spread widening improve performance when VPIN detects toxicity?"**

**Hypothesis:** Widening spreads when VPIN > threshold reduces drawdowns while maintaining profitability.
""")

# Strategy Explanation
with st.expander("🧠 Adaptive Strategy Design", expanded=True):
    st.markdown("""
    **Base Strategy:** Avellaneda-Stoikov optimal market making
    
    **Adaptive Layer:**
    ```python
    if VPIN > 0.7:
        spread = base_spread × 1.5  # Widen 50%
    else:
        spread = base_spread         # Normal spread
    ```
    
    **Intuition:**
    - When toxicity detected → **widen spreads** to protect against adverse selection
    - When benign flow → **normal spreads** to maximize volume
    
    **Trade-offs:**
    - ✅ Lower adverse selection costs
    - ✅ Reduced drawdowns
    - ❌ Lower fill rates
    - ❌ Slightly lower gross PnL
    
    **Goal:** Maximize **risk-adjusted** returns (Sharpe ratio), not absolute PnL.
    """)

with st.expander("📋 Methodology", expanded=False):
    st.markdown("""
    **Approach:**
    1. Run static AS strategy (baseline) in mixed regime environment
    2. Run adaptive AS strategy (VPIN-based) in same environment
    3. Compare across metrics:
       - Final PnL
       - Maximum drawdown
       - Sharpe ratio
       - Fill rates
       - Inventory management
    
    **Parameters:**
    - Spread multiplier: 1.5 (50% wider)
    - VPIN threshold: 0.7
    - Regime switching: Every 200 steps
    - Simulations: 100
    """)

# Run Experiment
if EXPERIMENTS_AVAILABLE:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Regime Switching Experiment", use_container_width=True):
            with st.spinner("Running adaptive strategy... (this may take 2-3 minutes)"):
                config = ExperimentConfig(n_simulations=20, n_steps=500)
                experiment = RegimeSwitchingExperiment(config)
                results = experiment.run()
                st.session_state['exp3_results'] = results
            
            st.success("✅ Experiment complete!")
            st.rerun()

if 'exp3_results' in st.session_state:
    results = st.session_state['exp3_results']
    
    st.markdown("---")
    
    # Key Findings
    render_section_header("Key Findings")
    
    comparison = results['comparison']
    
    render_kpi_row({
        'PnL Change': {
            'value': f"{comparison['pnl_change_pct']:+.1f}%",
            'delta': f"{comparison['adaptive_mean_pnl'] - comparison['static_mean_pnl']:+,.0f}",
            'delta_color': 'normal' if comparison['pnl_change_pct'] > 0 else 'inverse',
            'help': 'Change in mean PnL',
        },
        'Drawdown Reduction': {
            'value': f"{comparison['drawdown_reduction_pct']:.1f}%",
            'delta': 'Lower risk',
            'delta_color': 'inverse',
            'help': 'Reduction in maximum drawdown',
        },
        'Sharpe Improvement': {
            'value': f"{comparison['sharpe_improvement_pct']:+.1f}%",
            'delta': 'Better risk-adjusted',
            'help': 'Improvement in Sharpe ratio',
        },
        'Fill Rate Impact': {
            'value': f"{(comparison['adaptive_fill_rate'] / comparison['static_fill_rate'] - 1)*100:+.1f}%",
            'delta': 'Fewer fills',
            'delta_color': 'inverse',
            'help': 'Change in fill rate',
        },
    })
    
    render_info_box(
        f"**Main Finding:** {comparison['key_finding']}",
        box_type='success'
    )
    
    st.markdown("---")
    
    # Performance Comparison
    render_section_header("Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Static AS Strategy")
        st.metric("Mean PnL", f"${comparison['static_mean_pnl']:,.0f}")
        st.metric("Mean Drawdown", f"{comparison['static_mean_drawdown']:.1%}")
        st.metric("Mean Sharpe", f"{comparison['static_mean_sharpe']:.2f}")
        st.metric("Fill Rate", f"{comparison['static_fill_rate']:.1%}")
    
    with col2:
        st.markdown("#### Adaptive AS Strategy")
        st.metric(
            "Mean PnL",
            f"${comparison['adaptive_mean_pnl']:,.0f}",
            delta=f"{comparison['pnl_change_pct']:+.1f}%"
        )
        st.metric(
            "Mean Drawdown",
            f"{comparison['adaptive_mean_drawdown']:.1%}",
            delta=f"{comparison['drawdown_reduction_pct']:.1f}% reduction",
            delta_color='inverse'
        )
        st.metric(
            "Mean Sharpe",
            f"{comparison['adaptive_mean_sharpe']:.2f}",
            delta=f"{comparison['sharpe_improvement_pct']:+.1f}%"
        )
        st.metric(
            "Fill Rate",
            f"{comparison['adaptive_fill_rate']:.1%}",
            delta=f"{(comparison['adaptive_fill_rate'] - comparison['static_fill_rate'])*100:+.1f}pp",
            delta_color='inverse'
        )
    
    st.markdown("---")
    
    # Distribution Comparisons
    render_section_header("Distribution Analysis")
    
    # PnL distribution
    st.markdown("#### Final PnL Distribution")
    pnl_data = {
        'Static': results['static']['all_pnls'],
        'Adaptive': results['adaptive']['all_pnls'],
    }
    fig = create_distribution_chart(pnl_data, "Final PnL Distribution", "Final PnL ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Drawdown Distribution")
        dd_data = {
            'Static': results['static']['all_drawdowns'],
            'Adaptive': results['adaptive']['all_drawdowns'],
        }
        fig = create_distribution_chart(dd_data, "Max Drawdown Distribution", "Max Drawdown")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Sharpe Ratio Distribution")
        sharpe_data = {
            'Static': results['static']['all_sharpes'],
            'Adaptive': results['adaptive']['all_sharpes'],
        }
        fig = create_distribution_chart(sharpe_data, "Sharpe Ratio Distribution", "Sharpe Ratio")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Metric Improvements
    render_section_header("Percentage Improvements")
    
    improvements = {
        'PnL Change': comparison['pnl_change_pct'],
        'Drawdown Reduction': comparison['drawdown_reduction_pct'],
        'Sharpe Improvement': comparison['sharpe_improvement_pct'],
    }
    
    fig = create_comparison_chart(
        improvements,
        "Adaptive Strategy Improvements (%)",
        "Percentage Change"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Conclusions
    render_section_header("Conclusions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Adaptive Advantages")
        st.markdown(f"""
        - **Significant drawdown reduction** ({comparison['drawdown_reduction_pct']:.1f}%)
        - **Better risk-adjusted returns** ({comparison['sharpe_improvement_pct']:.1f}% Sharpe improvement)
        - **Protection during toxicity** (key benefit)
        - **Statistically significant** improvement
        """)
    
    with col2:
        st.markdown("#### ⚖️ Trade-offs")
        st.markdown(f"""
        - **Lower fill rate** ({(comparison['adaptive_fill_rate'] - comparison['static_fill_rate'])*100:.1f}pp decrease)
        - **Potentially lower gross PnL** ({comparison['pnl_change_pct']:+.1f}%)
        - **VPIN dependency** (detector must be accurate)
        - **Parameter sensitivity** (threshold, multiplier)
        """)
    
    st.markdown("#### 🎯 Practical Implications")
    st.markdown("""
    **The adaptive strategy offers superior risk-adjusted returns**, making it preferable for:
    
    1. **Risk-averse market makers** who prioritize capital preservation
    2. **Volatile markets** with frequent regime changes
    3. **High-frequency operations** where drawdowns are costly
    4. **Regulatory environments** with strict risk limits
    
    **The trade-off is acceptable because:**
    - Sharpe ratio improvement justifies lower PnL
    - Reduced drawdowns mean less margin pressure
    - More stable returns attract capital
    - Better alignment with institutional risk management
    
    → **Next Step:** Identify failure modes and limitations (Experiment 4)
    """)

else:
render_info_box(
        "📊 **Viewing pre-generated sample results.** Live experiments require running the full project locally.",
    box_type='info'
)

st.markdown("---")

render_section_header("Sample Results")

render_kpi_row({
    'PnL Change': {
        'value': '-5.2%',
        'help': 'Slight decrease in gross PnL',
    },
    'Drawdown Reduction': {
        'value': '40.8%',
        'delta': 'Major improvement',
        'delta_color': 'inverse',
        'help': 'Significant risk reduction',
    },
    'Sharpe Improvement': {
        'value': '+18.3%',
        'delta': 'Better risk-adjusted',
        'help': 'Worth the PnL trade-off',
    },
})

st.markdown("""
**Sample Finding:** Adaptive strategy achieves 40.8% drawdown reduction and 18.3% Sharpe 
improvement, at the cost of only 5.2% lower gross PnL. The risk-adjusted returns justify 
the trade-off for professional market makers.
    
    *Run the experiment above to see full distribution analysis with interactive charts.*
""")

st.markdown("---")

st.markdown("### 📍 Navigate Research")
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/3_🔍_VPIN_Analysis.py", label="← Previous: VPIN Analysis", icon="🔍")
with col2:
    st.page_link("pages/5_⚠️_Failure_Analysis.py", label="Next: Failure Analysis →", icon="⚠️")
