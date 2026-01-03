"""
Metric card utilities for dashboard.
"""
import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import COLORS

def render_metric_card(label, value, delta=None, delta_color="normal", help_text=None):
    """
    Render styled metric card.
    
    Args:
        label: Metric label
        value: Metric value (formatted string)
        delta: Optional delta value
        delta_color: "normal", "inverse", or "off"
        help_text: Optional help tooltip
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text,
    )

def render_kpi_row(metrics_dict):
    """
    Render row of KPI cards.
    
    Args:
        metrics_dict: {
            'metric_name': {
                'value': str,
                'delta': str (optional),
                'delta_color': str (optional),
                'help': str (optional),
            }
        }
    """
    cols = st.columns(len(metrics_dict))
    
    for col, (label, data) in zip(cols, metrics_dict.items()):
        with col:
            render_metric_card(
                label=label,
                value=data['value'],
                delta=data.get('delta'),
                delta_color=data.get('delta_color', 'normal'),
                help_text=data.get('help'),
            )

def format_number(value, precision=2, prefix='', suffix=''):
    """Format number with prefix/suffix."""
    if isinstance(value, (int, float)):
        if abs(value) >= 1e6:
            return f"{prefix}{value/1e6:.{precision}f}M{suffix}"
        elif abs(value) >= 1e3:
            return f"{prefix}{value/1e3:.{precision}f}K{suffix}"
        else:
            return f"{prefix}{value:.{precision}f}{suffix}"
    return str(value)

def format_currency(value, precision=2):
    """Format as currency."""
    return format_number(value, precision=precision, prefix='$')

def format_percentage(value, precision=1):
    """Format as percentage."""
    return format_number(value * 100, precision=precision, suffix='%')

def render_comparison_table(data, title=None):
    """
    Render styled comparison table.
    
    Args:
        data: DataFrame or dict
        title: Optional title
    """
    if title:
        st.subheader(title)
    
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=False,
    )

def render_info_box(text, box_type='info'):
    """
    Render info/warning/success box.
    
    Args:
        text: Message text
        box_type: 'info', 'success', 'warning', 'error'
    """
    if box_type == 'info':
        st.info(text, icon='ℹ️')
    elif box_type == 'success':
        st.success(text, icon='✅')
    elif box_type == 'warning':
        st.warning(text, icon='⚠️')
    elif box_type == 'error':
        st.error(text, icon='🚨')

def render_section_header(title, description=None):
    """Render section header with optional description."""
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"*{description}*")
    st.markdown("---")

