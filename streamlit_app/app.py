"""
Market Making Research Dashboard
Main entry point - Overview page
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from streamlit_app.config import LAYOUT, COLORS
from streamlit_app.utils.metrics import render_kpi_row, render_section_header, render_info_box

# Page config
st.set_page_config(
    page_title=LAYOUT['page_title'],
    page_icon=LAYOUT['page_icon'],
    layout=LAYOUT['layout'],
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_file = Path(__file__).parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("#  MM Research")
    st.markdown("---")
    st.markdown("###  Research Project")
    st.markdown("""
    **Market Making Under Adverse Selection**
    
    *Quantifying toxicity costs and validating real-time detection.*
    """)
    st.markdown("---")
    st.markdown("###  Navigation")
    st.markdown("""
    - **Overview**: Executive summary
    - **PnL Decomposition**: Cost attribution
    - **VPIN Analysis**: Toxicity detection
    - **Regime Switching**: Adaptive strategy
    - **Failure Analysis**: Edge cases
    - **Live Simulator**: Interactive demo
    """)
    st.markdown("---")
    st.markdown("###  Author")
    st.markdown("""
    **Tom Baxter**  
    Cambridge Physics MPhil  
    [GitHub](https://github.com/tombaxter) • [LinkedIn](#)
    """)

# Main content
st.title(" Market Making Research")
st.markdown("### *Quantifying Adverse Selection Costs in Modern Market Making*")

#  BIG INTERACTIVE CTA - MAKE IT IMPOSSIBLE TO MISS
st.markdown("")
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #00FF41 0%, #00D9FF 100%); border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 16px rgba(0, 255, 65, 0.3);'>
        <h1 style='color: #0E1117; margin: 0; font-size: 2.5rem;'> Interactive Demo</h1>
        <p style='color: #0E1117; font-size: 1.2rem; margin: 15px 0; font-weight: 600;'>Adjust parameters and watch the market maker respond in real-time</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("▶  LAUNCH LIVE SIMULATOR", type="primary", use_container_width=True):
        st.switch_page("pages/6_🎮_Live_Simulator.py")
    
    st.markdown("<p style='text-align: center; margin-top: 10px;'> <strong>Start here</strong> - The most engaging part of this project!</p>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("---")

# Executive Summary
render_section_header(
    "Executive Summary",
    "Core findings from experimental analysis"
)

# Key Findings
st.markdown("###  Research Question")
st.markdown("""
> **"How much does adverse selection cost a market maker, and can you detect it in real-time?"**
""")

# KPI Cards
render_kpi_row({
    'Adverse Selection': {
        'value': '68%',
        'delta': 'of losses in toxic flow',
        'help': 'Percentage of total losses attributable to informed traders',
    },
    'VPIN Accuracy': {
        'value': '3.2x',
        'delta': 'loss increase when VPIN > 0.7',
        'help': 'Predictive power of VPIN toxicity detector',
    },
    'Drawdown Reduction': {
        'value': '-41%',
        'delta': 'with adaptive strategy',
        'delta_color': 'inverse',
        'help': 'Risk reduction from regime-switching spreads',
    },
    'Sharpe Improvement': {
        'value': '+18%',
        'delta': 'risk-adjusted returns',
        'help': 'Performance improvement in mixed regimes',
    },
})

st.markdown("---")

# Four Core Experiments
col1, col2 = st.columns(2)

with col1:
    with st.expander(" Experiment 1: PnL Decomposition", expanded=True):
        st.markdown("""
        **Objective:** Quantify adverse selection contribution to losses
        
        **Key Finding:**
        - Benign flow: 22% adverse selection
        - Toxic flow: **68% adverse selection**
        - Naive strategy most vulnerable
        
        **Conclusion:** Adverse selection is the dominant loss factor in toxic regimes.
        """)
    
    with st.expander(" Experiment 3: Regime Switching"):
        st.markdown("""
        **Objective:** Test adaptive spread widening strategy
        
        **Key Finding:**
        - **41% drawdown reduction**
        - **18% Sharpe improvement**
        - 5% PnL reduction (worth the risk trade-off)
        
        **Conclusion:** Adaptive strategy offers superior risk-adjusted returns.
        """)

with col2:
    with st.expander(" Experiment 2: VPIN Analysis"):
        st.markdown("""
        **Objective:** Validate VPIN as toxicity predictor
        
        **Key Finding:**
        - Strong correlation: r = 0.64
        - When VPIN > 0.7: **3.2x loss increase**
        - Lead time: 50-100 steps
        
        **Conclusion:** VPIN provides actionable early warning signal.
        """)
    
    with st.expander(" Experiment 4: Failure Analysis"):
        st.markdown("""
        **Objective:** Identify failure modes and edge cases
        
        **Key Findings:**
        - False positives: Low impact
        - Detection lag: Medium impact (50-100 steps)
        - Extreme jumps: High impact (unavoidable)
        - HF switches: Medium impact (reduced effectiveness)
        
        **Conclusion:** Strategy robust with proper risk management.
        """)

st.markdown("---")

# Research Impact
render_section_header("Research Impact")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("###  Quantitative")
    st.markdown("""
    - Adverse selection quantified (68%)
    - VPIN validated as detector
    - Regime-switching proven effective
    - Risk-adjusted returns improved 18%
    """)

with col2:
    st.markdown("###  Practical")
    st.markdown("""
    - Real-time toxicity monitoring
    - Dynamic spread adjustment
    - Risk management framework
    - Production-ready implementation
    """)

with col3:
    st.markdown("###  Academic")
    st.markdown("""
    - Extends Avellaneda-Stoikov (2008)
    - Validates Easley et al. VPIN (2012)
    - vel regime-switching application
    - Comprehensive failure analysis
    """)

st.markdown("---")

# Methodology
render_section_header("Methodology")

st.markdown("""
**Simulation Framework:**
- Geometric Brownian Motion with jump-diffusion
- Poisson order arrivals with exponential fill probability
- Two regimes: Benign (random) vs Toxic (informed)
- 100 simulations × 1000 steps per experiment

**Strategies Tested:**
1. Naive: Constant spread (baseline)
2. Inventory-Aware: Asymmetric quoting
3. Avellaneda-Stoikov: Optimal market making
4. Adaptive AS: Regime-switching spreads

**Metrics:**
- VPIN (Volume-Synchronized Probability of Informed Trading)
- PnL decomposition (spread capture, inventory timing, adverse selection)
- Risk-adjusted returns (Sharpe, Sortino, Calmar ratios)
- Drawdown analysis
""")

st.markdown("---")

# Navigation
render_section_header("Navigate Research")

st.markdown("""
Use the **sidebar** or links below to explore detailed experimental results:

1. ** PnL Decomposition** - Deep dive into cost attribution across strategies
2. ** VPIN Analysis** - Toxicity detection validation and correlation analysis
3. ** Regime Switching** - Adaptive strategy performance comparison
4. ** Failure Analysis** - Edge cases, limitations, and mitigation strategies
5. ** Live Simulator** - Interactive strategy testing with real-time visualization
""")

render_info_box(
    "then explore VPIN Analysis to see the solution.",
    box_type='info'
)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #B0B0B0; padding: 2rem 0;'>
    <p>Built with Python • Streamlit • Plotly</p>
    <p>© 2026 Tom Baxter | Market Making Research</p>
</div>
""", unsafe_allow_html=True)

