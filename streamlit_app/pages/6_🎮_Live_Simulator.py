"""
Live Simulator Page
Interactive strategy testing
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.config import LAYOUT, COLORS
from streamlit_app.utils.metrics import render_kpi_row, render_section_header, render_info_box
from streamlit_app.utils.plotting import create_pnl_chart, create_vpin_chart, create_multi_line_chart

try:
    from src.simulation import (
        create_gbm, OrderFlowGenerator, OrderFlowConfig,
        FlowRegime, MarketSimulator, SimulationConfig
    )
    from src.strategies import (
        NaiveStrategy, InventoryAwareStrategy, AvellanedaStoikovStrategy
    )
    from src.metrics import VPINCalculator, VPINConfig
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False

st.set_page_config(
    page_title="Live Simulator | Market Making Research",
    page_icon="🎮",
    layout=LAYOUT['layout'],
)

css_file = Path(__file__).parent.parent / 'assets' / 'style.css'
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🎮 Live Market Making Simulator")
st.markdown("### *Interactive Strategy Testing*")
st.markdown("---")

render_section_header("Interactive Demo")
st.markdown("""
Test different market-making strategies in real-time with customizable parameters.
Visualize PnL, inventory, and VPIN dynamics as the simulation runs.
""")

if SIMULATION_AVAILABLE:
    # Sidebar Controls
    with st.sidebar:
        st.markdown("### 🎛️ Simulation Parameters")
        
        st.markdown("#### Market Parameters")
        initial_price = st.number_input(
            "Initial Price ($)",
            min_value=50.0,
            max_value=200.0,
            value=100.0,
            step=1.0
        )
        
        volatility = st.slider(
            "Volatility (σ)",
            min_value=0.01,
            max_value=0.05,
            value=0.02,
            step=0.001,
            format="%.3f",
            help="Annualized volatility"
        )
        
        st.markdown("#### Order Flow")
        arrival_rate = st.slider(
            "Arrival Rate (λ)",
            min_value=5.0,
            max_value=20.0,
            value=10.0,
            step=1.0,
            help="Average orders per period"
        )
        
        toxicity = st.slider(
            "Toxicity Factor",
            min_value=0.0,
            max_value=0.8,
            value=0.3,
            step=0.1,
            help="0 = benign, 0.5 = mixed, 0.8 = very toxic"
        )
        
        regime = st.selectbox(
            "Flow Regime",
            options=["BENIGN", "TOXIC"],
            index=0 if toxicity < 0.3 else 1
        )
        
        st.markdown("#### Strategy Selection")
        strategy_type = st.selectbox(
            "Strategy",
            options=["Naive", "Inventory-Aware", "Avellaneda-Stoikov"],
            index=2
        )
        
        if strategy_type == "Naive":
            spread = st.slider(
                "Spread Width",
                min_value=0.5,
                max_value=3.0,
                value=1.0,
                step=0.1
            )
        elif strategy_type == "Inventory-Aware":
            base_spread = st.slider(
                "Base Spread",
                min_value=0.5,
                max_value=3.0,
                value=1.0,
                step=0.1
            )
            inventory_penalty = st.slider(
                "Inventory Penalty",
                min_value=0.01,
                max_value=0.05,
                value=0.02,
                step=0.005,
                format="%.3f"
            )
        else:  # AS
            risk_aversion = st.slider(
                "Risk Aversion (γ)",
                min_value=0.05,
                max_value=0.2,
                value=0.1,
                step=0.01,
                format="%.2f"
            )
        
        st.markdown("#### Simulation")
        n_steps = st.slider(
            "Number of Steps",
            min_value=100,
            max_value=2000,
            value=500,
            step=100
        )
        
        seed = st.number_input(
            "Random Seed",
            min_value=0,
            max_value=9999,
            value=42,
            step=1,
            help="For reproducibility"
        )
        
        st.markdown("---")
        
        run_button = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
    # Main Content
    if run_button:
        with st.spinner("Running simulation..."):
            # Create price process
            price_process = create_gbm(
                S0=initial_price,
                sigma=volatility,
                dt=1/252,
                seed=seed
            )
            
            # Create order flow
            order_flow_config = OrderFlowConfig(
                A=arrival_rate,
                kappa=0.5,
                toxicity_factor=toxicity
            )
            order_flow = OrderFlowGenerator(order_flow_config, seed=seed)
            order_flow.set_regime(FlowRegime.TOXIC if regime == "TOXIC" else FlowRegime.BENIGN)
            
            # Create strategy
            if strategy_type == "Naive":
                strategy = NaiveStrategy(spread_width=spread)
            elif strategy_type == "Inventory-Aware":
                strategy = InventoryAwareStrategy(
                    base_spread=base_spread,
                    inventory_penalty=inventory_penalty
                )
            else:  # AS
                strategy = AvellanedaStoikovStrategy(
                    risk_aversion=risk_aversion,
                    volatility=volatility,
                    kappa=0.5
                )
            
            # Run simulation
            sim_config = SimulationConfig(n_steps=n_steps, seed=seed)
            results = MarketSimulator.run_simulation(
                price_process, order_flow, strategy, sim_config
            )
            
            # Calculate VPIN
            vpin_config = VPINConfig(bucket_size=5000, n_buckets=50)
            vpin_calc = VPINCalculator(vpin_config)
            
            for t in range(len(order_flow.order_history)):
                order = order_flow.order_history[t]
                vpin_calc.update(
                    volume=order.size,
                    price=order.filled_price,
                    is_buy=(order.side == 'buy')
                )
            
            vpin_series = vpin_calc.get_vpin_series()
            
            # Store results
            st.session_state['sim_results'] = results
            st.session_state['vpin_series'] = vpin_series
        
        st.success("✅ Simulation complete!")
    
    # Display Results
    if 'sim_results' in st.session_state:
        results = st.session_state['sim_results']
        vpin_series = st.session_state['vpin_series']
        
        st.markdown("---")
        
        # KPI Cards
        render_section_header("Performance Summary")
        
        decomp = results.pnl_decomposition
        
        render_kpi_row({
            'Final PnL': {
                'value': f"${results.final_pnl:,.0f}",
                'delta': '✅ Profitable' if results.final_pnl > 0 else '❌ Loss',
                'delta_color': 'normal' if results.final_pnl > 0 else 'inverse',
            },
            'Spread Capture': {
                'value': f"${decomp['spread_capture']:,.0f}",
                'help': 'Profit from bid-ask spread',
            },
            'Adverse Selection': {
                'value': f"${decomp['adverse_selection']:,.0f}",
                'delta': '⚠️ Toxic' if decomp['adverse_selection'] < -500 else '✅ Benign',
                'delta_color': 'inverse' if decomp['adverse_selection'] < -500 else 'normal',
                'help': 'Losses from informed traders',
            },
            'Num Trades': {
                'value': f"{results.n_trades}",
                'help': 'Total trades executed',
            },
        })
        
        st.markdown("---")
        
        # Charts
        render_section_header("Visualization")
        
        # PnL Evolution
        st.markdown("#### PnL Evolution")
        fig = create_pnl_chart(results.pnl, title=f"{strategy_type} Strategy PnL")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price Evolution
            st.markdown("#### Price Evolution")
            price_data = {'Price': results.prices}
            fig = create_multi_line_chart(
                price_data,
                "Mid Price Evolution",
                "Time Step",
                "Price ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Inventory Evolution
            st.markdown("#### Inventory Evolution")
            inventory_data = {'Inventory': results.inventories}
            fig = create_multi_line_chart(
                inventory_data,
                "Inventory Position",
                "Time Step",
                "Inventory (shares)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # VPIN
        if len(vpin_series) > 0:
            st.markdown("#### VPIN (Toxicity Detector)")
            fig = create_vpin_chart(vpin_series, threshold=0.7)
            st.plotly_chart(fig, use_container_width=True)
            
            avg_vpin = np.mean(vpin_series)
            max_vpin = np.max(vpin_series)
            pct_high = np.mean(vpin_series > 0.7) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average VPIN", f"{avg_vpin:.3f}")
            with col2:
                st.metric("Max VPIN", f"{max_vpin:.3f}")
            with col3:
                st.metric("% High Toxicity", f"{pct_high:.1f}%")
        
        st.markdown("---")
        
        # Trade Details
        with st.expander("📊 Trade Details", expanded=False):
            if not results.trades_df.empty:
                st.dataframe(
                    results.trades_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No trades executed")
        
        # PnL Decomposition
        with st.expander("💰 PnL Decomposition", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Spread Capture", f"${decomp['spread_capture']:,.0f}")
            with col2:
                st.metric("Inventory Timing", f"${decomp['inventory_timing']:,.0f}")
            with col3:
                st.metric("Adverse Selection", f"${decomp['adverse_selection']:,.0f}")
            
            st.markdown("---")
            
            st.metric("Total PnL", f"${decomp['total']:,.0f}")
            
            st.markdown("""
            **Components:**
            - **Spread Capture**: Profit from buying below mid and selling above mid
            - **Inventory Timing**: Gains/losses from price movements while holding inventory
            - **Adverse Selection**: Residual losses from trading with informed traders
            """)
    
    else:
        # Initial state
        render_info_box(
            "Configure parameters in the sidebar and click **'Run Simulation'** to start.",
            box_type='info'
        )
        
        st.markdown("---")
        
        # Tutorial
        render_section_header("How to Use")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Try These Scenarios")
            st.markdown("""
            **Scenario 1: Benign Flow**
            - Toxicity: 0.0
            - Strategy: Avellaneda-Stoikov
            - Expected: Profitable, low adverse selection
            
            **Scenario 2: Toxic Flow**
            - Toxicity: 0.7
            - Strategy: Naive
            - Expected: Losses from adverse selection
            
            **Scenario 3: Comparison**
            - Run same parameters with different strategies
            - Compare PnL and adverse selection
            """)
        
        with col2:
            st.markdown("#### 📊 What to Watch")
            st.markdown("""
            **PnL Chart:**
            - Green fill = profitable
            - Red fill = losses
            - Volatility = risk
            
            **Inventory:**
            - Oscillates around zero = good
            - Trending = inventory risk
            - Large swings = poor management
            
            **VPIN:**
            - < 0.3 = benign flow
            - 0.7+ = toxic flow detected
            - Correlates with adverse selection
            """)

else:
    render_info_box(
        "Simulation modules not available. Please ensure experiments are properly installed.",
        box_type='error'
    )

st.markdown("---")

st.markdown("### 📍 Navigate Research")
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/5_⚠️_Failure_Analysis.py", label="← Previous: Failure Analysis", icon="⚠️")
with col2:
    st.page_link("streamlit_app/app.py", label="← Back to Overview", icon="📊")
