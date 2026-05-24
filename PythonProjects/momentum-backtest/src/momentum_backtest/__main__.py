"""Entry point: python -m momentum_backtest"""
from . import BacktestConfig, make_synthetic_prices, run_backtest
from .analytics import compute_metrics, print_metrics, save_equity_curve


def main() -> None:
    config = BacktestConfig(
        lookback_months=12,
        skip_recent_month=True,
        portfolio_mode="long_only",
        n_longs=5,
        cost_bps=10.0,
        n_assets=20,
        n_years=15,
        seed=42,
    )

    print("Generating synthetic price panel ...")
    prices = make_synthetic_prices(
        n_assets=config.n_assets,
        n_years=config.n_years,
        seed=config.seed,
        annual_mu=config.annual_mu,
        annual_sigma=config.annual_sigma,
    )
    print(f"  Shape: {prices.shape}")
    print(f"  Dates: {prices.index[0].date()} to {prices.index[-1].date()}")

    print(f"\nRunning {config.portfolio_mode} momentum backtest ...")
    print(f"  Lookback={config.lookback_months}m  skip_recent={config.skip_recent_month}")
    print(f"  n_longs={config.n_longs}  cost={config.cost_bps}bps")

    result = run_backtest(prices, config)
    metrics = compute_metrics(result)

    print("\nPerformance Metrics:")
    print_metrics(metrics)

    out = "equity_curve.csv"
    save_equity_curve(result, out)
    print(f"\nEquity curve saved to {out}")


if __name__ == "__main__":
    main()
