# Market-Making Research Dashboard

Streamlit dashboard for inspecting simulation and experiment outputs from `market-making-research`.

## Run Locally

```bash
cd streamlit_app
pip install streamlit plotly pandas numpy
streamlit run app.py
```

## Pages

1. Overview
2. PnL decomposition
3. VPIN analysis
4. Regime switching
5. Failure analysis
6. Live simulator
7. Future work
8. Sensitivity analysis

## Notes

-The dashboard can run sample analyses directly.
-For full project integration, install from repository root with `pip install -e .`.
-Styling is controlled by `assets/style.css` and `config.py`.

## Troubleshooting

-If imports fail, ensure the package is installed from project root.
-If CSS does not load, clear Streamlit cache.

## License

MIT (same as parent project).
