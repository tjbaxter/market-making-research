"""
Plotting utilities for professional quant charts.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import COLORS, PLOTLY_LAYOUT

def apply_theme(fig):
    """Apply consistent theme to Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def create_line_chart(x, y, name, color=None, show_legend=True):
    """Create styled line chart."""
    if color is None:
        color = COLORS['accent_blue']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name=name,
        line=dict(color=color, width=2.5),
        hovertemplate='%{x}<br>%{y:,.2f}<extra></extra>',
        showlegend=show_legend,
    ))
    
    return apply_theme(fig)

def create_comparison_chart(data_dict, title, ylabel):
    """
    Create comparison bar chart.
    
    Args:
        data_dict: {strategy_name: value}
        title: Chart title
        ylabel: Y-axis label
    """
    strategies = list(data_dict.keys())
    values = list(data_dict.values())
    
    # Color bars based on positive/negative
    colors = [COLORS['accent_green'] if v >= 0 else COLORS['accent_red'] for v in values]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=strategies,
        y=values,
        marker=dict(
            color=colors,
            line=dict(color=COLORS['border'], width=1),
        ),
        text=[f'{v:,.0f}' for v in values],
        textposition='outside',
        textfont=dict(color=COLORS['text_primary'], size=12),
        hovertemplate='%{x}<br>%{y:,.2f}<extra></extra>',
    ))
    
    fig.update_layout(
        title=title,
        yaxis_title=ylabel,
        showlegend=False,
        yaxis=dict(gridcolor=COLORS['border']),
        xaxis=dict(tickangle=-15),
    )
    
    return apply_theme(fig)

def create_pnl_chart(pnl_series, title="PnL Evolution"):
    """Create PnL evolution chart with fill."""
    x = np.arange(len(pnl_series))
    
    fig = go.Figure()
    
    # Determine color based on final PnL
    color = COLORS['accent_green'] if pnl_series[-1] >= 0 else COLORS['accent_red']
    
    fig.add_trace(go.Scatter(
        x=x,
        y=pnl_series,
        mode='lines',
        name='PnL',
        line=dict(color=color, width=3),
        fill='tozeroy',
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)",
        hovertemplate='Step %{x}<br>PnL: $%{y:,.2f}<extra></extra>',
    ))
    
    # Add zero line
    fig.add_hline(y=0, line=dict(color=COLORS['text_secondary'], width=1, dash='dash'))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time Step',
        yaxis_title='Cumulative PnL ($)',
        showlegend=False,
    )
    
    return apply_theme(fig)

def create_distribution_chart(data_dict, title, xlabel):
    """
    Create distribution comparison (histogram).
    
    Args:
        data_dict: {strategy_name: [values]}
        title: Chart title
        xlabel: X-axis label
    """
    fig = go.Figure()
    
    colors = [COLORS['accent_green'], COLORS['accent_red'], COLORS['accent_blue']]
    
    for i, (name, data) in enumerate(data_dict.items()):
        fig.add_trace(go.Histogram(
            x=data,
            name=name,
            opacity=0.7,
            marker=dict(color=colors[i % len(colors)]),
            hovertemplate='%{x}<br>Count: %{y}<extra></extra>',
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title='Frequency',
        barmode='overlay',
    )
    
    return apply_theme(fig)

def create_decomposition_chart(categories, benign_values, toxic_values):
    """Create PnL decomposition comparison chart."""
    fig = go.Figure()
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig.add_trace(go.Bar(
        x=[i - width/2 for i in x],
        y=benign_values,
        name='Benign Flow',
        marker=dict(color=COLORS['accent_green']),
        width=width,
        hovertemplate='%{y:,.2f}<extra></extra>',
    ))
    
    fig.add_trace(go.Bar(
        x=[i + width/2 for i in x],
        y=toxic_values,
        name='Toxic Flow',
        marker=dict(color=COLORS['accent_red']),
        width=width,
        hovertemplate='%{y:,.2f}<extra></extra>',
    ))
    
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(x),
            ticktext=categories,
            tickangle=-15,
        ),
        yaxis_title='PnL ($)',
        barmode='group',
    )
    
    # Add zero line
    fig.add_hline(y=0, line=dict(color=COLORS['text_secondary'], width=1, dash='dash'))
    
    return apply_theme(fig)

def create_vpin_chart(vpin_series, threshold=0.7):
    """Create VPIN time series with threshold."""
    fig = go.Figure()
    
    x = np.arange(len(vpin_series))
    
    # Color points based on threshold
    colors = [COLORS['accent_red'] if v > threshold else COLORS['accent_blue'] 
              for v in vpin_series]
    
    fig.add_trace(go.Scatter(
        x=x,
        y=vpin_series,
        mode='lines+markers',
        name='VPIN',
        line=dict(color=COLORS['accent_blue'], width=2),
        marker=dict(color=colors, size=4),
        hovertemplate='Bucket %{x}<br>VPIN: %{y:.3f}<extra></extra>',
    ))
    
    # Add threshold line
    fig.add_hline(
        y=threshold,
        line=dict(color=COLORS['accent_yellow'], width=2, dash='dash'),
        annotation_text=f'Threshold ({threshold})',
        annotation_position='right',
    )
    
    fig.update_layout(
        title='VPIN Evolution',
        xaxis_title='Volume Bucket',
        yaxis_title='VPIN',
        showlegend=False,
        yaxis=dict(range=[0, 1]),
    )
    
    return apply_theme(fig)

def create_multi_line_chart(data_dict, title, xlabel, ylabel):
    """
    Create multi-line comparison chart.
    
    Args:
        data_dict: {series_name: [values]}
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
    """
    fig = go.Figure()
    
    colors = [COLORS['accent_green'], COLORS['accent_red'], COLORS['accent_blue']]
    
    for i, (name, data) in enumerate(data_dict.items()):
        fig.add_trace(go.Scatter(
            x=np.arange(len(data)),
            y=data,
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=2.5),
            hovertemplate='%{x}<br>%{y:,.2f}<extra></extra>',
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
    )
    
    return apply_theme(fig)

def create_heatmap(data, x_labels, y_labels, title):
    """Create correlation/confusion heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, COLORS['accent_red']],
            [0.5, COLORS['card_bg']],
            [1, COLORS['accent_green']],
        ],
        text=np.round(data, 2),
        texttemplate='%{text}',
        textfont=dict(color=COLORS['text_primary']),
        hovertemplate='%{x} vs %{y}<br>Value: %{z:.2f}<extra></extra>',
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(side='bottom'),
    )
    
    return apply_theme(fig)

