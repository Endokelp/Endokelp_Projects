from .analytics import PerformanceMetrics, compute_metrics
from .backtest import BacktestResult, run_backtest
from .config import BacktestConfig, CVConfig, SignalConfig, UniverseConfig
from .cpcv import CombinatorialPurgedCV, oos_sharpe_distribution
from .cv import PurgedKFold, purge_train_indices
from .data import fetch_prices, make_synthetic_prices
from .pbo import cscv_logits, cscv_rank_pairs, probability_of_backtest_overfitting
from .portfolio import form_weights_long_only, form_weights_long_short
from .research import evaluate_signals, format_verdict_table
from .signals import SIGNAL_REGISTRY, compute_lowvol, compute_momentum, compute_reversal
from .stats import (
    deflated_sharpe_ratio,
    expected_max_sharpe,
    probabilistic_sharpe_ratio,
)

__all__ = [
    "SignalConfig",
    "BacktestConfig",
    "CVConfig",
    "UniverseConfig",
    "fetch_prices",
    "make_synthetic_prices",
    "compute_momentum",
    "compute_reversal",
    "compute_lowvol",
    "SIGNAL_REGISTRY",
    "form_weights_long_only",
    "form_weights_long_short",
    "BacktestResult",
    "run_backtest",
    "PerformanceMetrics",
    "compute_metrics",
    "PurgedKFold",
    "purge_train_indices",
    "CombinatorialPurgedCV",
    "oos_sharpe_distribution",
    "probabilistic_sharpe_ratio",
    "expected_max_sharpe",
    "deflated_sharpe_ratio",
    "cscv_logits",
    "cscv_rank_pairs",
    "probability_of_backtest_overfitting",
    "evaluate_signals",
    "format_verdict_table",
]
