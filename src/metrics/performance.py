"""Performance metrics for strategy evaluation."""
import numpy as np
import pandas as pd
from typing import Optional

class PerformanceMetrics:
    @staticmethod
    def calculate_all(pnl: np.ndarray, trades: Optional[list] = None, risk_free_rate: float = 0.0) -> dict:
        returns = np.diff(pnl)
        metrics = {
            'total_pnl': pnl[-1] - pnl[0] if len(pnl) > 0 else 0,
            'sharpe_ratio': calculate_sharpe_ratio(returns, risk_free_rate),
            'sortino_ratio': calculate_sortino_ratio(returns, risk_free_rate),
            'max_drawdown': calculate_max_drawdown(pnl),
            'calmar_ratio': calculate_calmar_ratio(pnl, risk_free_rate),
            'volatility': np.std(returns) if len(returns) > 0 else 0,
            'mean_return': np.mean(returns) if len(returns) > 0 else 0,
        }
        if trades:
            metrics.update({'num_trades': len(trades), 'win_rate': calculate_win_rate(trades)})
        return metrics

def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    if len(returns) == 0: return 0.0
    mean_return, std_return = np.mean(returns), np.std(returns, ddof=1)
    if std_return == 0: return 0.0
    excess_return = mean_return - (risk_free_rate / periods_per_year)
    return (excess_return / std_return) * np.sqrt(periods_per_year)

def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    if len(returns) == 0: return 0.0
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0: return float('inf') if np.mean(returns) > 0 else 0.0
    downside_std = np.std(downside_returns, ddof=1)
    if downside_std == 0: return 0.0
    excess_return = np.mean(returns) - (risk_free_rate / periods_per_year)
    return (excess_return / downside_std) * np.sqrt(periods_per_year)

def calculate_max_drawdown(pnl: np.ndarray) -> float:
    if len(pnl) == 0: return 0.0
    running_max = np.maximum.accumulate(pnl)
    drawdown = (running_max - pnl) / (running_max + 1e-10)
    return np.max(drawdown)

def calculate_calmar_ratio(pnl: np.ndarray, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    if len(pnl) < 2: return 0.0
    total_return = (pnl[-1] - pnl[0]) / (pnl[0] + 1e-10)
    years = len(pnl) / periods_per_year
    annualized_return = (1 + total_return) ** (1 / years) - 1
    max_dd = calculate_max_drawdown(pnl)
    if max_dd == 0: return float('inf') if annualized_return > 0 else 0.0
    return annualized_return / max_dd

def calculate_win_rate(trades: list) -> float:
    if not trades: return 0.0
    winning_trades = sum(1 for t in trades if calculate_trade_pnl(t) > 0)
    return winning_trades / len(trades)

def calculate_trade_pnl(trade) -> float:
    if trade.side == 'buy': return (trade.mid_price - trade.price) * trade.size
    else: return (trade.price - trade.mid_price) * trade.size
