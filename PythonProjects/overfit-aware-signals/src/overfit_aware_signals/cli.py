import argparse
import sys
from pathlib import Path

import pandas as pd

from .backtest import run_backtest
from .config import BacktestConfig, CVConfig, SignalConfig, UniverseConfig
from .cpcv import CombinatorialPurgedCV, combinatorial_test_sharpes
from .data import fetch_prices, make_synthetic_prices
from .plotting import plot_block_sharpe_hist, plot_is_oos_rank_scatter
from .research import (
    RESEARCH_TRIAL_LOG,
    evaluate_signals,
    format_dsr_sensitivity,
    format_verdict_table,
    logged_n_trials,
    signal_lookback,
)
from .signals import SIGNAL_REGISTRY

_SURVIVORSHIP_BANNER = (
    "NON-CLAIM: live universe uses current constituents (survivorship bias). "
    "Absolute Sharpes are optimistic demo numbers, not a deployment claim. "
    "Prefer `synth` for an offline path that does not oversell live equity."
)


def _aligned_returns(prices, signal_cfg: SignalConfig, backtest_cfg: BacktestConfig):
    cols = {
        name: run_backtest(prices, fn(prices, signal_cfg), backtest_cfg).returns
        for name, fn in SIGNAL_REGISTRY.items()
    }
    return pd.DataFrame(cols).dropna(how="any")


def _run_eval(
    prices,
    *,
    pbo_n_groups: int,
    plot_dir: str | None,
    n_trials: int | None,
    show_sensitivity: bool,
    live: bool,
):
    if live:
        print(_SURVIVORSHIP_BANNER)
        print()
    signal_cfg = SignalConfig()
    backtest_cfg = BacktestConfig()
    cv_cfg = CVConfig()
    df = evaluate_signals(
        prices,
        signal_cfg,
        backtest_cfg,
        cv_cfg,
        pbo_n_groups=pbo_n_groups,
        n_trials=n_trials,
    )
    print(format_verdict_table(df))
    print()
    print(f"PBO threshold: reject if PBO > 0.05 (observed {df['pbo'].iloc[0]:.3f})")
    print("DSR threshold: require DSR >= 0.95")
    print(
        f"n_trials={int(df['n_trials'].iloc[0])} "
        f"(registry default={len(SIGNAL_REGISTRY)}; research log={logged_n_trials()})"
    )
    if show_sensitivity:
        print()
        print(format_dsr_sensitivity(prices, signal_cfg, backtest_cfg))

    if plot_dir:
        out = Path(plot_dir)
        out.mkdir(parents=True, exist_ok=True)
        ret_mat = _aligned_returns(prices, signal_cfg, backtest_cfg)
        plot_is_oos_rank_scatter(
            ret_mat.to_numpy(),
            n_groups=pbo_n_groups,
            path=out / "is_oos_rank.png",
        )
        for name, fn in SIGNAL_REGISTRY.items():
            rets = run_backtest(prices, fn(prices, signal_cfg), backtest_cfg).returns
            cv = CombinatorialPurgedCV(
                n_groups=cv_cfg.n_groups,
                n_test_groups=cv_cfg.n_test_groups,
                lookback=signal_lookback(name, signal_cfg),
                embargo_pct=cv_cfg.embargo_pct,
            )
            block = combinatorial_test_sharpes(rets.to_numpy(), cv)
            plot_block_sharpe_hist(
                block,
                title=f"{name} combinatorial block Sharpe",
                path=out / f"block_sharpe_{name}.png",
            )
        print(f"Plots written to {out}/")
    return df


def cmd_synth(args: argparse.Namespace) -> int:
    print(f"Synthetic panel: assets={args.assets} years={args.years} seed={args.seed}")
    print("(honest offline demo - no live equity claims)")
    prices = make_synthetic_prices(
        n_assets=args.assets, n_years=args.years, seed=args.seed
    )
    print(f"Shape {prices.shape}  {prices.index[0].date()} -> {prices.index[-1].date()}")
    print()
    _run_eval(
        prices,
        pbo_n_groups=args.pbo_groups,
        plot_dir=args.plot_dir,
        n_trials=args.n_trials,
        show_sensitivity=args.sensitivity,
        live=False,
    )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    uni = UniverseConfig(start=args.start, end=args.end)
    if args.tickers:
        uni.tickers = [t.strip() for t in args.tickers.split(",")]
    print(f"Fetching {len(uni.tickers)} tickers  {uni.start} -> {uni.end or 'today'}")
    prices = fetch_prices(uni.tickers, uni.start, uni.end)
    print(f"Shape {prices.shape}  {prices.index[0].date()} -> {prices.index[-1].date()}")
    print()
    _run_eval(
        prices,
        pbo_n_groups=args.pbo_groups,
        plot_dir=args.plot_dir,
        n_trials=args.n_trials,
        show_sensitivity=args.sensitivity,
        live=True,
    )
    return 0


def cmd_trials(_: argparse.Namespace) -> int:
    print(f"Research trial log ({logged_n_trials()} configs):")
    for row in RESEARCH_TRIAL_LOG:
        print(f"  [{row['status']:9}] {row['id']}: {row['note']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="overfit_aware_signals")
    sub = p.add_subparsers(dest="cmd", required=True)

    def _add_eval_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--plot-dir", default=None)
        sp.add_argument(
            "--n-trials",
            type=int,
            default=None,
            help=f"DSR trial count (default=registry {len(SIGNAL_REGISTRY)}; "
            f"log={logged_n_trials()})",
        )
        sp.add_argument(
            "--sensitivity",
            action="store_true",
            help="print DSR vs n_trials grid",
        )

    synth = sub.add_parser("synth", help="offline demo on synthetic prices (preferred)")
    synth.add_argument("--assets", type=int, default=20)
    synth.add_argument("--years", type=int, default=15)
    synth.add_argument("--seed", type=int, default=42)
    synth.add_argument("--pbo-groups", type=int, default=8)
    _add_eval_flags(synth)
    synth.set_defaults(func=cmd_synth)

    run = sub.add_parser(
        "run",
        help="fetch live universe (survivorship-biased; non-claim demo)",
    )
    run.add_argument("--start", default="2005-01-01")
    run.add_argument("--end", default=None)
    run.add_argument("--tickers", default=None, help="comma-separated override")
    run.add_argument("--pbo-groups", type=int, default=16)
    _add_eval_flags(run)
    run.set_defaults(func=cmd_run)

    trials = sub.add_parser("trials", help="print research trial log for n_trials honesty")
    trials.set_defaults(func=cmd_trials)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
