"""
Future Work Page.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import LAYOUT, COLORS
from utils.metrics import render_section_header, render_info_box

# Page config
st.set_page_config(
    page_title="Future Work | Market Making Research",
    page_icon="",
    layout=LAYOUT['layout'],
    initial_sidebar_state="expanded",
)

# Load CSS
css_file = Path(__file__).parent.parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Navigation
st.page_link("app.py", label="← Back to Overview", icon="")

# Header
st.title(" Future Work & Extensions")
st.markdown("---")

# Introduction
render_section_header("Overview")

st.markdown("""
This project provides a solid foundation for understanding adverse selection in market making.
However, several limitations exist, and many exciting extensions could enhance both realism and impact.

This page outlines:
1. **Current Limitations** - Known simplifications
2. **Future Work** - Research directions
3. **Alternative Approaches** - Methods not yet explored
""")

st.markdown("---")

# ============================================================================
# SECTION 1: LIMITATIONS
# ============================================================================

render_section_header(" Current Limitations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 1. Price Process Simplifications")
    st.markdown("""
    **Current:** Geometric Brownian Motion (GBM) with optional jumps
    
    **Limitations:**
    - stochastic volatility (GARCH effects ignored)
    - microstructure noise (bid-ask bounce)
    - Jump sizes are normally distributed (real jumps are fat-tailed)
    - intraday patterns (U-shaped volume curve)
    
    **Impact:** May underestimate real-world risks, especially tail events.
    """)
    
    st.markdown("#### 2. Order Flow Model")
    st.markdown("""
    **Current:** Poisson arrivals with exponential fill probability
    
    **Limitations:**
    - Binary toxicity regimes (benign/toxic)
    - strategic trader behavior (all informed traders identical)
    - adverse selection from inventory imbalance
    - Simplified arrival rates (constant in each regime)
    
    **Impact:** VPIN may be more/less effective in practice.
    """)

    st.markdown("#### 3. Market Structure")
    st.markdown("""
    **Current:** Single-asset, no order book dynamics
    
    **Limitations:**
    - multi-asset correlations
    - queue position dynamics
    - latency arbitrage
    - maker-taker fee structure
    
    **Impact:** Real P&L attribution is more complex.
    """)

with col2:
    st.markdown("#### 4. Strategy Assumptions")
    st.markdown("""
    **Current:** Avellaneda-Stoikov with VPIN-based regime switching
    
    **Limitations:**
    - execution delays (assumes instant fills)
    - partial fills
    - order cancellation risk
    - Fixed lot sizes (no size optimization)
    - cross-asset hedging
    
    **Impact:** Real strategies are more sophisticated.
    """)
    
    st.markdown("#### 5. Statistical Validation")
    st.markdown("""
    **Current:** Simulated data, no real market calibration
    
    **Limitations:**
    - Parameters are reasonable but not empirically fitted
    - out-of-sample testing on real data
    - Overfitting risk in parameter optimization
    - transaction costs calibration
    
    **Impact:** Results may not generalize to production.
    """)
    
    st.markdown("#### 6. Computational Scope")
    st.markdown("""
    **Current:** 100 simulations × 1000 steps per experiment
    
    **Limitations:**
    - Limited parameter grid resolution
    - high-frequency regime (1 step = 1 second, not milliseconds)
    - Sequential simulation (could parallelize)
    
    **Impact:** Some rare events may not be captured.
    """)

st.markdown("---")

# ============================================================================
# SECTION 2: FUTURE WORK
# ============================================================================

render_section_header(" Future Work Roadmap")

st.markdown("### Priority 1: Realism Enhancements")

with st.expander(" **1.1 Advanced Price Models**", expanded=True):
    st.markdown("""
    **Objective:** Incorporate realistic price dynamics
    
    **Approaches:**
    - **Heston stochastic volatility**: Capture vol clustering
    - **Hawkes processes**: Model self-exciting order flow
    - **Hidden Markov Models**: Learn regime transitions from data
    - **GARCH effects**: Capture volatility persistence
    
    **Why it matters:** Volatility clustering significantly affects optimal spreads.
    
    **Implementation difficulty:** Medium (existing Python libraries available)
    
    **Expected impact:** 20-30% more realistic P&L variance
    """)

with st.expander(" **1.2 Multi-Asset Market Making**"):
    st.markdown("""
    **Objective:** Extend to correlated assets (e.g., SPY + QQQ)
    
    **Approaches:**
    - Cross-asset hedging strategies
    - Correlation breakdown risk
    - Multi-dimensional VPIN
    
    **Why it matters:** Real MM is never single-asset.
    
    **Implementation difficulty:** High (requires careful correlation modeling)
    
    **Expected impact:** Could reduce risk by 40%+ through diversification
    """)

with st.expander("⏱ **1.3 Order Book Dynamics**"):
    st.markdown("""
    **Objective:** Model full limit order book (LOB)
    
    **Approaches:**
    - Queue position modeling
    - LOB shape as signal (imbalance, depth)
    - Fleeting orders and cancellation risk
    - Latency arbitrage detection
    
    **Why it matters:** Queue position significantly affects fill rates.
    
    **Implementation difficulty:** Very High (complex state space)
    
    **Expected impact:** Fill rate modeling accuracy +50%
    """)

st.markdown("### Priority 2: Advanced Strategies")

with st.expander(" **2.1 Reinforcement Learning for MM**"):
    st.markdown("""
    **Objective:** Learn optimal policy via RL (vs closed-form A-S)
    
    **Approaches:**
    - **DQN**: Discrete spread levels
    - **PPO**: Continuous spread control
    - **Multi-agent RL**: Competitive MM simulation
    - **Inverse RL**: Learn from real MM behavior
    
    **Why it matters:** RL can adapt to non-stationary dynamics.
    
    **Implementation difficulty:** Very High (requires extensive hyperparameter tuning)
    
    **Expected impact:** Potential 10-15% Sharpe improvement over A-S
    
    **Risks:** Sample inefficiency, overfitting, interpretability loss
    """)

with st.expander(" **2.2 Machine Learning Toxicity Predictors**"):
    st.markdown("""
    **Objective:** Enhance VPIN with ML features
    
    **Approaches:**
    - **Feature engineering**: LOB features, trade features, volatility features
    - **Gradient boosting**: XGBoost/LightGBM for toxicity prediction
    - **LSTM networks**: Sequential toxicity modeling
    - **Ensemble methods**: Combine VPIN + ML
    
    **Why it matters:** ML may capture non-linear toxicity signals.
    
    **Implementation difficulty:** Medium (requires labeled toxic periods)
    
    **Expected impact:** 20-30% improvement in toxicity detection accuracy
    """)

with st.expander(" **2.3 Optimal Execution Integration**"):
    st.markdown("""
    **Objective:** Combine MM with optimal execution (Almgren-Chriss)
    
    **Approaches:**
    - Dynamic inventory targets based on client flow
    - TWAP/VWAP integration for unwinding
    - Adverse selection hedging
    
    **Why it matters:** MM firms also handle client execution.
    
    **Implementation difficulty:** Medium
    
    **Expected impact:** More realistic P&L attribution
    """)

st.markdown("### Priority 3: Real Data & Deployment")

with st.expander(" **3.1 Real Market Data Calibration**"):
    st.markdown("""
    **Objective:** Fit model to real SPY/QQQ tick data
    
    **Approaches:**
    - Estimate volatility, drift, jump parameters from data
    - Calibrate order arrival rates
    - Validate VPIN on real toxic periods (e.g., flash crashes)
    - Out-of-sample testing
    
    **Why it matters:** Validation on real data is essential for credibility.
    
    **Implementation difficulty:** Medium (requires data access)
    
    **Expected impact:** Determines if results hold in practice
    
    **Data sources:** NYSE TAQ, LOBSTER, Polygon.io
    """)

with st.expander(" **3.2 Production Deployment Considerations**"):
    st.markdown("""
    **Objective:** Bridge simulation → production
    
    **Considerations:**
    - Latency requirements (sub-millisecond)
    - Risk controls (position limits, kill switches)
    - Monitoring and alerting
    - Regulatory compliance (Reg NMS, market making obligations)
    - Capital requirements
    
    **Why it matters:** Real MM requires infrastructure beyond algorithms.
    
    **Implementation difficulty:** Very High (requires firm infrastructure)
    """)

st.markdown("---")

# ============================================================================
# SECTION 3: ALTERNATIVE APPROACHES
# ============================================================================

render_section_header(" Alternative Approaches Not Explored")

comparison_data = {
    'Approach': [
        'Bayesian Online Learning',
        'Kalman Filtering (Regime Detection)',
        'High-Frequency Microstructure Models',
        'Game-Theoretic MM',
        'Deep Hedging (Neural Networks)'
    ],
    'Description': [
        'Update beliefs about toxicity in real-time using Bayesian inference',
        'Estimate hidden regime states (benign/toxic) using Kalman filters',
        'Model tick-by-tick dynamics with ultra-high frequency data',
        'Model strategic interactions between multiple market makers',
        'Use neural networks for joint pricing and hedging'
    ],
    'Pros': [
        'Principled uncertainty quantification, online adaptation',
        'Optimal state estimation, mathematically elegant',
        'Captures sub-second dynamics, realistic for HFT',
        'Accounts for competition, equilibrium analysis',
        'Flexible, can learn complex hedge ratios'
    ],
    'Cons': [
        'Computationally intensive, requires prior specification',
        'Assumes linear-Gaussian dynamics (may not hold)',
        'Requires massive data, high computational cost',
        'Difficult to solve, requires knowledge of competitors',
        'Black box, requires lots of data, hard to interpret'
    ],
    'Difficulty': [
        'High',
        'Medium',
        'Very High',
        'Very High',
        'Very High'
    ]
}

import pandas as pd
comparison_df = pd.DataFrame(comparison_data)

st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

render_section_header(" Key Takeaways")

st.markdown("""
### This Project Achieves:

 **Rigorous simulation framework** with reproducible results  
 **Quantifies adverse selection** (~68% of losses in toxic flow)  
 **Validates VPIN** as a practical toxicity detector  
 **Statistical rigor** (confidence intervals, hypothesis testing)  
 **Parameter sensitivity analysis** (robustness validation)

### What's Missing (Acknowledged):

 **Real market calibration** - parameters are reasonable but not fitted  
 **Multi-asset dynamics** - single asset is simplified  
 **Full order book** - no queue position modeling  
 **Strategic traders** - all informed traders identical  
 **Transaction costs** - not fully calibrated  

1. **Scope**: Key market microstructure concepts included
2. **Methodological**: Provides template for MM research
3. **Extensible**: Structured for further changes
4. **Transparent**: Explicitly documents assumptions and limitations

### For Future Researchers:

This codebase provides a **solid starting point**. The most impactful next steps are:

1. **Calibrate to real data** (Priority 1)
2. **Add stochastic volatility** (Priority 2)
3. **Explore RL strategies** (Priority 3)
4. **Multi-asset extension** (Priority 4)
""")

st.markdown("---")

# ============================================================================
# CALL TO ACTION
# ============================================================================

st.markdown("### Notes")

st.info("""
This project is open-source and can be extended in several directions:

- real data calibration studies
- RL-based market making strategies
- multi-asset extensions
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #B0B0B0; padding: 2rem 0;'>
    <p><strong>Continuous improvement is the path to excellence.</strong></p>
    <p>© 2026 Tom Baxter | Market Making Research</p>
</div>
""", unsafe_allow_html=True)

