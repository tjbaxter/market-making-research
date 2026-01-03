from setuptools import setup, find_packages

setup(
    name="market_making_research",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "scipy>=1.10.0",
    ],
    python_requires=">=3.9",
    author="Tom Baxter",
    description="Advanced market-making research engine",
    keywords="quantitative finance, market making, adverse selection",
)

