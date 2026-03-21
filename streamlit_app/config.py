"""
Global configuration for Streamlit dashboard.
Professional quant trader aesthetic.
"""

# Color Palette (Bloomberg Terminal / Military Tech)
COLORS = {
    'background': '#0E1117',
    'card_bg': '#1E1E1E',
    'accent_green': '#00FF41',      # Profit
    'accent_red': '#FF073A',        # Loss
    'accent_blue': '#00D9FF',       # Info/Neutral
    'accent_yellow': '#FFD700',     # Warning
    'text_primary': '#FAFAFA',
    'text_secondary': '#B0B0B0',
    'border': '#2E2E2E',
}

# Typography
FONTS = {
    'title': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    'body': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    'monospace': '"Fira Code", "JetBrains Mono", Consolas, monospace',
}

# Layout
LAYOUT = {
    'page_icon': '',
    'page_title': 'Market Making Research',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Plotly Template
PLOTLY_TEMPLATE = 'plotly_dark'

# Custom Plotly Layout
PLOTLY_LAYOUT = {
    'template': PLOTLY_TEMPLATE,
    'paper_bgcolor': COLORS['background'],
    'plot_bgcolor': COLORS['card_bg'],
    'font': {'color': COLORS['text_primary'], 'family': FONTS['body']},
    'title': {'font': {'size': 20, 'color': COLORS['text_primary']}},
    'xaxis': {
        'gridcolor': COLORS['border'],
        'linecolor': COLORS['border'],
        'zerolinecolor': COLORS['border'],
    },
    'yaxis': {
        'gridcolor': COLORS['border'],
        'linecolor': COLORS['border'],
        'zerolinecolor': COLORS['border'],
    },
    'hoverlabel': {
        'bgcolor': COLORS['card_bg'],
        'font': {'color': COLORS['text_primary']},
    },
}

# Page Metadata
PAGES_META = {
    'Overview': {
        'icon': '',
        'description': 'Executive summary of research findings',
    },
    'PnL Decomposition': {
        'icon': '',
        'description': 'Quantifying adverse selection costs',
    },
    'VPIN Analysis': {
        'icon': '',
        'description': 'Toxicity detection validation',
    },
    'Regime Switching': {
        'icon': '',
        'description': 'Adaptive strategy performance',
    },
    'Failure Analysis': {
        'icon': '',
        'description': 'Edge cases and failure modes',
    },
    'Live Simulator': {
        'icon': '',
        'description': 'Interactive strategy testing',
    },
}

