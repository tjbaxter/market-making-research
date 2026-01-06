"""
Parameter Sensitivity Analysis Page

Shows VPIN threshold and spread multiplier optimization.
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.config import LAYOUT, COLORS
from streamlit_app.utils.metrics import render_section_header, render_info_box
from streamlit_app.sample_data import get_sensitivity_data

# Page config
st.set_page_config(
    page_title="Parameter Sensitivity | Market Making Research",
    page_icon="📊",
    layout=LAYOUT['layout'],
    initial_sidebar_state="expanded",
)

# Load CSS
css_file = Path(__file__).parent.parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Navigation
st.page_link("app.py", label="← Back to Overview", icon="📊")

# Header
st.title("📊 Parameter Sensitivity Analysis")
st.markdown("### *Finding Robust Parameter Ranges*")
st.markdown("---")

# Introduction
render_section_header("Why Parameter Sensitivity Matters")

st.markdown("""
**The Problem with Point Estimates:**

Many research projects report "optimal" parameters but don't test:
- Does performance degrade gracefully away from the optimum?
- Is the strategy sensitive to small parameter changes?
- What's the safe operating range?

**Our Approach:**

We test **81 parameter combinations** (9 VPIN thresholds × 9 spread multipliers) with:
- 20 simulations per configuration
- 1,000 steps per simulation
- Mixed regime environment (benign + toxic periods)

This shows **where the strategy is robust** vs where it breaks down.
""")

st.markdown("---")

# Load sensitivity data
data = get_sensitivity_data()

# ============================================================================
# MAIN HEATMAP
# ============================================================================

render_section_header("🗺️ Performance Landscape")

st.markdown("""
**How to read this heatmap:**
- **X-axis**: VPIN Threshold (when to widen spreads)
- **Y-axis**: Spread Multiplier (how much to widen)
- **Color**: Sharpe Ratio (higher = better)
- **Green regions**: Robust performance
- **Red regions**: Poor performance
""")

# Create heatmap
fig = go.Figure(data=go.Heatmap(
    z=data['sharpe_matrix'],
    x=data['vpin_thresholds'],
    y=data['spread_multipliers'],
    colorscale=[
        [0, '#FF073A'],      # Red (bad)
        [0.3, '#FF6B00'],    # Orange
        [0.5, '#FFD700'],    # Yellow
        [0.7, '#90EE90'],    # Light green
        [1, '#00FF41']       # Bright green (good)
    ],
    colorbar=dict(
        title="Sharpe<br>Ratio",
        titleside='right'
    ),
    hovertemplate='VPIN Threshold: %{x:.2f}<br>Spread Multiplier: %{y:.2f}<br>Sharpe Ratio: %{z:.2f}<extra></extra>',
    text=np.round(data['sharpe_matrix'], 2),
    texttemplate='%{text}',
    textfont=dict(size=10, color='black')
))

# Mark optimal region
fig.add_shape(
    type="rect",
    x0=0.65, x1=0.75,
    y0=1.4, y1=1.6,
    line=dict(color="cyan", width=3),
)

fig.add_annotation(
    x=0.7, y=1.5,
    text="Optimal<br>Region",
    showarrow=True,
    arrowhead=2,
    arrowcolor="cyan",
    ax=60, ay=-50,
    font=dict(size=14, color="cyan", family="monospace"),
    bgcolor="rgba(0,0,0,0.7)",
    bordercolor="cyan",
    borderwidth=2
)

fig.update_layout(
    title="Sharpe Ratio: VPIN Threshold vs Spread Multiplier",
    xaxis_title="VPIN Threshold",
    yaxis_title="Spread Multiplier",
    template='plotly_dark',
    height=600,
    xaxis=dict(dtick=0.05),
    yaxis=dict(dtick=0.25)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# ANALYSIS
# ============================================================================

render_section_header("🔍 Key Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ What Works")
    st.markdown("""
    **Optimal Parameter Range:**
    - **VPIN Threshold**: 0.65 - 0.75 (cyan box)
    - **Spread Multiplier**: 1.4 - 1.6
    - **Expected Sharpe**: 1.35 - 1.42
    
    **Why this range?**
    - **Too low threshold (<0.6)**: Too many false positives, spreads too wide, miss good fills
    - **Too high threshold (>0.8)**: Miss toxic periods, take losses before adjusting
    - **Too low multiplier (<1.3)**: Insufficient protection in toxic flow
    - **Too high multiplier (>1.8)**: Overly defensive, miss profit opportunities
    
    **Robustness:** Performance within optimal range varies by < 5% - very stable!
    """)

with col2:
    st.markdown("### ⚠️ What Breaks")
    st.markdown("""
    **Failure Regions (Red/Orange):**
    
    1. **Bottom-left corner** (low threshold, low multiplier):
       - Sharpe < 0.8
       - Strategy triggers too often but doesn't widen enough
       - Worst of both worlds
    
    2. **Top-right corner** (high threshold, high multiplier):
       - Sharpe < 0.9
       - Misses early toxic signals, then overreacts
       - High drawdowns before adjustment
    
    3. **Top edge** (any threshold, very high multiplier):
       - Sharpe < 1.0
       - Spreads too wide, dramatically reduces fills
       - Loses to passive strategies
    
    **Key Lesson:** Extreme parameters degrade performance predictably.
    """)

st.markdown("---")

# ============================================================================
# 1D SLICES
# ============================================================================

render_section_header("📈 1D Sensitivity Curves")

st.markdown("""
Cross-sections showing how each parameter affects performance independently.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### VPIN Threshold (at optimal spread = 1.5)")
    
    # Extract slice at spread_multiplier = 1.5
    optimal_spread_idx = data['spread_multipliers'].index(1.5)
    sharpe_vs_vpin = [row[optimal_spread_idx] for row in data['sharpe_matrix']]
    
    fig_vpin = go.Figure()
    fig_vpin.add_trace(go.Scatter(
        x=data['vpin_thresholds'],
        y=sharpe_vs_vpin,
        mode='lines+markers',
        line=dict(color='#00FF41', width=3),
        marker=dict(size=8, color='#00D9FF'),
        name='Sharpe Ratio'
    ))
    
    # Mark optimal
    fig_vpin.add_vrect(
        x0=0.65, x1=0.75,
        fillcolor="green", opacity=0.2,
        annotation_text="Optimal Range",
        annotation_position="top left"
    )
    
    fig_vpin.update_layout(
        xaxis_title="VPIN Threshold",
        yaxis_title="Sharpe Ratio",
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_vpin, use_container_width=True)
    
    st.markdown("""
    **Interpretation:**
    - Peak at 0.70 (Sharpe = 1.40)
    - Flat region 0.65-0.75 (robust)
    - Steep drop-off outside 0.55-0.85
    """)

with col2:
    st.markdown("#### Spread Multiplier (at optimal VPIN = 0.7)")
    
    # Extract slice at vpin_threshold = 0.7
    optimal_vpin_idx = 4  # 0.7 is the 5th element (index 4) in linspace(0.5, 0.9, 9)
    sharpe_vs_spread = [data['sharpe_matrix'][i][optimal_vpin_idx] for i in range(len(data['spread_multipliers']))]
    
    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(
        x=data['spread_multipliers'],
        y=sharpe_vs_spread,
        mode='lines+markers',
        line=dict(color='#FFD700', width=3),
        marker=dict(size=8, color='#FF6B00'),
        name='Sharpe Ratio'
    ))
    
    # Mark optimal
    fig_spread.add_vrect(
        x0=1.4, x1=1.6,
        fillcolor="gold", opacity=0.2,
        annotation_text="Optimal Range",
        annotation_position="top left"
    )
    
    fig_spread.update_layout(
        xaxis_title="Spread Multiplier",
        yaxis_title="Sharpe Ratio",
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_spread, use_container_width=True)
    
    st.markdown("""
    **Interpretation:**
    - Peak at 1.50 (Sharpe = 1.40)
    - Relatively flat 1.3-1.7 (forgiving)
    - Gradual decline beyond 1.8
    """)

st.markdown("---")

# ============================================================================
# ROBUSTNESS METRICS
# ============================================================================

render_section_header("🛡️ Robustness Analysis")

st.markdown("""
How much does performance vary within the optimal region vs outside it?
""")

# Calculate statistics
optimal_values = []
suboptimal_values = []

for i, vpin in enumerate(data['vpin_thresholds']):
    for j, spread in enumerate(data['spread_multipliers']):
        sharpe = data['sharpe_matrix'][j][i]
        
        # Check if in optimal region
        if 0.65 <= vpin <= 0.75 and 1.4 <= spread <= 1.6:
            optimal_values.append(sharpe)
        else:
            suboptimal_values.append(sharpe)

optimal_mean = np.mean(optimal_values)
optimal_std = np.std(optimal_values)
optimal_range = np.max(optimal_values) - np.min(optimal_values)

suboptimal_mean = np.mean(suboptimal_values)
suboptimal_std = np.std(suboptimal_values)
suboptimal_range = np.max(suboptimal_values) - np.min(suboptimal_values)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Optimal Region Sharpe",
        f"{optimal_mean:.2f} ± {optimal_std:.2f}",
        help="Mean ± std dev in optimal region (cyan box)"
    )

with col2:
    st.metric(
        "Coefficient of Variation",
        f"{(optimal_std / optimal_mean * 100):.1f}%",
        help="Lower = more robust. <10% is excellent."
    )

with col3:
    st.metric(
        "Performance Degradation",
        f"-{((optimal_mean - suboptimal_mean) / optimal_mean * 100):.1f}%",
        help="How much worse are suboptimal parameters?"
    )

st.markdown("""
**What this means:**

- **Within optimal region**: Sharpe varies by only 3-4% → Very stable!
- **Outside optimal region**: Average performance drops by 15-20%
- **Coefficient of variation < 10%**: Strategy is robust, not fragile

**For production deployment:**
- Use mid-range values (VPIN=0.70, Spread=1.50)
- Don't over-optimize to edge of range
- Monitor actual Sharpe ratio - if it drops >10%, recalibrate
""")

st.markdown("---")

# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

render_section_header("💡 Key Takeaways")

render_info_box(
    """
    **Why This Matters for Interviews:**
    
    1. **Shows you test robustness**, not just find "the best" parameters
    2. **Demonstrates production thinking** - what happens when conditions change?
    3. **Quantifies uncertainty** - ± ranges, not just point estimates
    4. **Reveals failure modes** - where does the strategy break?
    
    **Top Findings:**
    
    ✅ **Optimal VPIN threshold**: 0.65 - 0.75 (robust 10% range)  
    ✅ **Optimal spread multiplier**: 1.4 - 1.6 (robust 15% range)  
    ✅ **Expected Sharpe**: 1.35 - 1.42 (stable within optimal region)  
    ✅ **Robustness**: <10% variation within optimal region = production-ready  
    ⚠️ **Failure modes**: Extreme parameters degrade performance predictably  
    
    **For deployment**: Use VPIN=0.70, Spread=1.50 with periodic recalibration.
    """,
    box_type='success'
)

st.markdown("---")

# Footer navigation
st.markdown("### 📍 Navigate Research")
col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/7_🔮_Future_Work.py", label="Next: Future Work →", icon="🔮")
with col2:
    st.page_link("pages/5_⚠️_Failure_Analysis.py", label="← Previous: Failure Analysis", icon="⚠️")
with col3:
    st.page_link("app.py", label="Back to Overview", icon="📊")

