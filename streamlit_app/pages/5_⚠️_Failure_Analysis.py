"""
Failure Analysis Page
Experiment 4: Edge cases and limitations
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
from streamlit_app.utils.plotting import create_comparison_chart

try:
    from experiments.exp4_failure_analysis import FailureAnalysisExperiment
    from experiments.config import ExperimentConfig
    EXPERIMENTS_AVAILABLE = True
except ImportError:
    EXPERIMENTS_AVAILABLE = False

st.set_page_config(
    page_title="Failure Analysis | Market Making Research",
    page_icon="⚠️",
    layout=LAYOUT['layout'],
    initial_sidebar_state="expanded",
)

css_file = Path(__file__).parent.parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("⚠️ Failure Analysis")
st.markdown("### *Experiment 4: Edge Cases & Limitations*")
st.markdown("---")

render_section_header("Research Question")
st.markdown("""
> **"Under what conditions does the adaptive strategy fail?"**

**Goal:** Document failure modes, quantify impact, and propose mitigation strategies.
""")

# Failure Modes Overview
with st.expander("🔍 Failure Modes Overview", expanded=True):
    st.markdown("""
    We test four critical edge cases:
    
    | Failure Mode | Description | Expected Impact |
    |--------------|-------------|-----------------|
    | **False Positives** | VPIN spike without actual toxicity (volume surge) | Low - reduces fills but minimal losses |
    | **Detection Lag** | Toxicity starts before VPIN reacts | Medium - initial losses before detection |
    | **Extreme Jumps** | Large price jumps that overwhelm any strategy | High - unavoidable inventory losses |
    | **HF Switches** | Very rapid regime changes (every 20 steps) | Medium - reduced effectiveness |
    
    **Testing Approach:**
    - Isolate each failure mode
    - Measure impact on PnL
    - Compare to baseline performance
    - Document mitigation strategies
    """)

with st.expander("📋 Test Scenarios", expanded=False):
    st.markdown("""
    **1. False Positives Test:**
    - Environment: Benign flow with 3x normal volume
    - Expectation: VPIN spikes but no actual toxicity
    - Measure: Opportunity cost from wider spreads
    
    **2. Detection Lag Test:**
    - Environment: Sudden switch from benign → toxic at step 500
    - Expectation: Losses before VPIN reacts
    - Measure: Losses in first 50-100 steps after switch
    
    **3. Extreme Jumps Test:**
    - Environment: GBM with jump-diffusion (rare large moves)
    - Expectation: Inventory losses regardless of strategy
    - Measure: PnL with jumps vs without jumps
    
    **4. High Frequency Switches Test:**
    - Environment: Regime changes every 20 steps (very fast)
    - Expectation: VPIN can't track accurately
    - Measure: Performance degradation vs baseline
    """)

# Run Experiment
if EXPERIMENTS_AVAILABLE:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Failure Analysis", use_container_width=True):
            with st.spinner("Testing failure modes... (this may take 2-3 minutes)"):
                config = ExperimentConfig(n_simulations=20, n_steps=500)
                experiment = FailureAnalysisExperiment(config)
                results = experiment.run()
                st.session_state['exp4_results'] = results
            
            st.success("✅ Analysis complete!")
            st.rerun()

if 'exp4_results' in st.session_state:
    results = st.session_state['exp4_results']
    
    st.markdown("---")
    
    # Impact Summary
    render_section_header("Failure Mode Impact")
    
    fp_pnl = results['false_positives']['mean_pnl']
    lag_pnl = results['detection_lag']['mean_lag_loss']
    jump_pnl = results['extreme_jumps']['mean_pnl_with_jumps']
    hf_pnl = results['high_frequency_switches']['mean_pnl_hf_switches']
    
    # Create severity classification
    def classify_severity(pnl):
        if pnl > 1000:
            return "🟢 Low"
        elif pnl > -1000:
            return "🟡 Medium"
        else:
            return "🔴 High"
    
    render_kpi_row({
        'False Positives': {
            'value': f"${fp_pnl:,.0f}",
            'delta': classify_severity(fp_pnl),
            'help': 'PnL under false positive conditions',
        },
        'Detection Lag': {
            'value': f"${lag_pnl:,.0f}",
            'delta': classify_severity(lag_pnl),
            'help': 'Losses before detection kicks in',
        },
        'Extreme Jumps': {
            'value': f"${jump_pnl:,.0f}",
            'delta': classify_severity(jump_pnl),
            'help': 'PnL with jump-diffusion',
        },
        'HF Switches': {
            'value': f"${hf_pnl:,.0f}",
            'delta': classify_severity(hf_pnl),
            'help': 'PnL with rapid regime changes',
        },
    })
    
    st.markdown("---")
    
    # Detailed Analysis
    render_section_header("Detailed Failure Mode Analysis")
    
    # Test 1: False Positives
    with st.expander("🟡 Test 1: False Positives", expanded=True):
        st.markdown("#### Scenario")
        st.markdown("""
        **Setup:** Benign flow but with **3x normal volume** (simulates temporary liquidity surge)
        
        **Expected:** VPIN spikes due to volume, but no actual informed trading
        
        **Result:** Adaptive strategy widens spreads unnecessarily, reducing fills
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Impact")
            st.metric("Mean PnL", f"${results['false_positives']['mean_pnl']:,.0f}")
            st.metric("Std Dev", f"${results['false_positives']['std_pnl']:,.0f}")
        
        with col2:
            st.markdown("#### Severity")
            st.markdown(f"""
            **{classify_severity(fp_pnl)} Impact**
            
            {results['false_positives']['finding']}
            """)
        
        st.markdown("#### 🛡️ Mitigation")
        st.info(results['false_positives']['mitigation'], icon="💡")
    
    # Test 2: Detection Lag
    with st.expander("🟡 Test 2: Detection Lag", expanded=False):
        st.markdown("#### Scenario")
        st.markdown("""
        **Setup:** Sudden regime switch from benign → toxic at step 500
        
        **Expected:** VPIN requires 50-100 steps to detect change
        
        **Result:** Losses incurred before adaptive strategy reacts
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Impact")
            st.metric("Mean Lag Loss", f"${results['detection_lag']['mean_lag_loss']:,.0f}")
            st.metric("Std Dev", f"${results['detection_lag']['std_lag_loss']:,.0f}")
        
        with col2:
            st.markdown("#### Severity")
            st.markdown(f"""
            **{classify_severity(lag_pnl)} Impact**
            
            {results['detection_lag']['finding']}
            """)
        
        st.markdown("#### 🛡️ Mitigation")
        st.info(results['detection_lag']['mitigation'], icon="💡")
    
    # Test 3: Extreme Jumps
    with st.expander("🔴 Test 3: Extreme Jumps", expanded=False):
        st.markdown("#### Scenario")
        st.markdown("""
        **Setup:** GBM with jump-diffusion (rare but large price moves)
        
        **Expected:** Inventory losses regardless of spread adjustments
        
        **Result:** No strategy can fully protect against extreme jumps
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Impact")
            st.metric("Mean PnL with Jumps", f"${results['extreme_jumps']['mean_pnl_with_jumps']:,.0f}")
            st.metric("Std Dev", f"${results['extreme_jumps']['std_pnl_with_jumps']:,.0f}")
        
        with col2:
            st.markdown("#### Severity")
            st.markdown(f"""
            **{classify_severity(jump_pnl)} Impact**
            
            {results['extreme_jumps']['finding']}
            """)
        
        st.markdown("#### 🛡️ Mitigation")
        st.info(results['extreme_jumps']['mitigation'], icon="💡")
    
    # Test 4: High Frequency Switches
    with st.expander("🟡 Test 4: High Frequency Switches", expanded=False):
        st.markdown("#### Scenario")
        st.markdown("""
        **Setup:** Regime changes every 20 steps (very rapid alternation)
        
        **Expected:** VPIN cannot track accurately, frequent false signals
        
        **Result:** Reduced effectiveness compared to slower regime changes
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Impact")
            st.metric("Mean PnL (HF)", f"${results['high_frequency_switches']['mean_pnl_hf_switches']:,.0f}")
            st.metric("Std Dev", f"${results['high_frequency_switches']['std_pnl_hf_switches']:,.0f}")
        
        with col2:
            st.markdown("#### Severity")
            st.markdown(f"""
            **{classify_severity(hf_pnl)} Impact**
            
            {results['high_frequency_switches']['finding']}
            """)
        
        st.markdown("#### 🛡️ Mitigation")
        st.info(results['high_frequency_switches']['mitigation'], icon="💡")
    
    st.markdown("---")
    
    # Comparative Impact
    render_section_header("Comparative Impact Analysis")
    
    impact_data = {
        'False Positives': fp_pnl,
        'Detection Lag': lag_pnl,
        'Extreme Jumps': jump_pnl,
        'HF Switches': hf_pnl,
    }
    
    fig = create_comparison_chart(
        impact_data,
        "PnL Impact by Failure Mode",
        "Mean PnL ($)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Synthesis
    render_section_header("Synthesis & Recommendations")
    
    summary = results['summary']
    
    st.markdown("#### 🎯 Overall Assessment")
    st.success(summary['overall_assessment'], icon="✅")
    
    st.markdown("#### 📊 Failure Mode Summary")
    
    failure_modes = summary['failure_modes']
    
    df_data = []
    for mode in failure_modes:
        df_data.append({
            'Failure Mode': mode['name'],
            'Impact': mode['impact'],
            'Mitigation Strategy': mode['mitigation'],
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Recommendations
    render_section_header("Production Deployment Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Essential Safeguards")
        st.markdown("""
        1. **Multi-signal confirmation**
           - Don't rely on VPIN alone
           - Add volume confirmation
           - Monitor realized volatility
        
        2. **Adaptive thresholds**
           - Dynamic VPIN threshold based on market conditions
           - Shorter bucket windows for faster detection
           - Hysteresis to prevent oscillation
        
        3. **Position limits**
           - Hard caps on inventory
           - Auto-flattening at thresholds
           - Emergency stop-loss levels
        """)
    
    with col2:
        st.markdown("#### 🎛️ Parameter Tuning")
        st.markdown("""
        4. **VPIN calibration**
           - Bucket size: 2,500-10,000 shares
           - Threshold: 0.65-0.75
           - Number of buckets: 30-50
        
        5. **Spread multiplier**
           - Conservative: 1.5-2.0x
           - Aggressive: 1.2-1.5x
           - Emergency: 3.0x+ (pause)
        
        6. **Risk monitoring**
           - Real-time P&L tracking
           - Drawdown alerts
           - Regime change detection
        """)
    
    st.markdown("---")
    
    # Limitations
    render_section_header("Known Limitations")
    
    render_info_box("""
    **This research has important limitations:**
    
    1. **Simulation vs Reality**
       - Real markets have latency, order book dynamics, queue position
       - Assumes fills happen instantly at quoted prices
       - No market impact from our own orders
    
    2. **VPIN Assumptions**
       - Bulk classification is approximate
       - Volume bucketing may miss fast events
       - Parameters need market-specific calibration
    
    3. **Regime Modeling**
       - Real toxicity is continuous, not binary
       - Multiple informed traders with different signals
       - Correlation with broader market stress
    
    4. **Strategy Simplifications**
       - No consideration of multiple assets
       - Ignores correlation effects
       - Single-agent framework
    
    **→ Production deployment requires extensive backtesting on real data.**
    """, box_type='warning')

else:
    render_info_box(
        "Click 'Run Experiment' above to test failure modes, or view sample findings below.",
        box_type='info'
    )
    
    st.markdown("---")
    
    render_section_header("Sample Results")
    
    render_kpi_row({
        'False Positives': {
            'value': '$1,247',
            'delta': '🟢 Low Impact',
        },
        'Detection Lag': {
            'value': '$-524',
            'delta': '🟡 Medium Impact',
        },
        'Extreme Jumps': {
            'value': '$-2,156',
            'delta': '🔴 High Impact',
        },
        'HF Switches': {
            'value': '$-892',
            'delta': '🟡 Medium Impact',
        },
    })
    
    st.markdown("""
    **Sample Finding:** The adaptive strategy is robust to most edge cases. Main vulnerability 
    is extreme price jumps (unavoidable inventory risk). False positives have minimal impact, 
    while detection lag is manageable with proper parameter tuning.
    
    *Run the experiment above to see detailed impact analysis for each failure mode.*
    """)

st.markdown("---")

st.markdown("### 📍 Navigate Research")
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/4_🔄_Regime_Switching.py", label="← Previous: Regime Switching", icon="🔄")
with col2:
    st.page_link("pages/6_🎮_Live_Simulator.py", label="Next: Live Simulator →", icon="🎮")

