# Market Making Research Dashboard

Professional Streamlit dashboard for visualizing market-making research results.

## 🚀 Quick Start

### Local Development
```bash
# Navigate to streamlit_app directory
cd streamlit_app

# Install dependencies (if not already installed)
pip install streamlit plotly pandas numpy

# Run the app
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure
```
streamlit_app/
├── app.py                          # Main entry point (Overview page)
├── config.py                       # Theme & constants
├── utils/
│   ├── plotting.py                 # Chart utilities
│   └── metrics.py                  # KPI utilities
├── pages/
│   ├── 2_💰_PnL_Decomposition.py
│   ├── 3_🔍_VPIN_Analysis.py
│   ├── 4_🔄_Regime_Switching.py
│   ├── 5_⚠️_Failure_Analysis.py
│   └── 6_🎮_Live_Simulator.py
├── assets/
│   └── style.css                   # Custom styling
└── .streamlit/
    └── config.toml                 # Streamlit config
```

## 🎨 Design Features

- **Dark theme** with neon accents (Bloomberg terminal aesthetic)
- **Plotly dark** template for all charts
- **Professional typography** (Inter + Fira Code)
- **Smooth interactions** and animations
- **Mobile responsive** design
- **Custom CSS** for polish

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set main file: `streamlit_app/app.py`
5. Deploy!

**Environment variables:** None required

### Alternative: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/app.py"]
```
```bash
docker build -t market-making-dashboard .
docker run -p 8501:8501 market-making-dashboard
```

### Alternative: Heroku
```bash
# Create Procfile
echo "web: streamlit run streamlit_app/app.py --server.port $PORT" > Procfile

# Deploy
heroku create market-making-research
git push heroku main
```

## 🧪 Running Experiments

The dashboard can run experiments live if the parent project is installed:
```bash
# From project root
pip install -e .

# Then run dashboard
cd streamlit_app
streamlit run app.py
```

Click "Run Experiment" buttons on each page to generate live results.

## 📊 Pages Overview

1. **Overview** - Executive summary and key findings
2. **PnL Decomposition** - Adverse selection quantification
3. **VPIN Analysis** - Toxicity detection validation
4. **Regime Switching** - Adaptive strategy comparison
5. **Failure Analysis** - Edge cases and limitations
6. **Live Simulator** - Interactive strategy testing

## 🎯 For Recruiters

This dashboard visualizes research from a comprehensive market-making study:

**Research Question:** "How much does adverse selection cost, and can you detect it?"

**Key Findings:**
- Adverse selection accounts for **68%** of losses in toxic regimes
- VPIN provides **3.2x** loss increase prediction
- Adaptive strategy achieves **41%** drawdown reduction

**GitHub:** [github.com/yourusername/market-making-research](https://github.com)

## 📝 Customization

### Change Theme Colors

Edit `config.py`:
```python
COLORS = {
    'accent_green': '#00FF41',  # Change to your color
    'accent_red': '#FF073A',
    # ...
}
```

### Add New Page

1. Create `pages/7_Your_Page.py`
2. Use existing pages as template
3. Import from `config` and `utils`
4. Streamlit auto-detects new pages

### Modify Charts

Edit chart functions in `utils/plotting.py`:
```python
def your_custom_chart(data):
    fig = go.Figure()
    # Your chart code
    return apply_theme(fig)
```

## 🐛 Troubleshooting

**CSS not loading:**
```bash
# Clear Streamlit cache
streamlit cache clear
```

**Import errors:**
```bash
# Ensure parent project is installed
pip install -e .
```

**Port already in use:**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

## 📄 License

MIT License - See parent project

## 👤 Author

**Tom Baxter**  
Cambridge Physics MPhil  
[GitHub](https://github.com/yourusername) • [LinkedIn](https://linkedin.com/in/yourprofile)

---

Built with ❤️ using Streamlit, Plotly, and Python

