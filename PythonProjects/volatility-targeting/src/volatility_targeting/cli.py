import argparse
import sys

from .data import load_returns, synthetic_returns
from .diagnostics import summary_stats
from .targeting import VolTargetConfig, VolTargeter


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="volatility-targeting")
    sub = p.add_subparsers(dest="cmd", required=True)

    # shared vol-target args
    def _add_common(sp):
        sp.add_argument("--target", type=float, default=0.10)
        sp.add_argument("--method", default="rolling", choices=["rolling", "ewma"])
        sp.add_argument("--window", type=int, default=20)
        sp.add_argument("--halflife", type=float, default=20.0)
        sp.add_argument("--lag", type=int, default=1)
        sp.add_argument("--cap", type=float, default=3.0)
        sp.add_argument("--floor", type=float, default=0.0)
        sp.add_argument("--out", required=True)
        sp.add_argument("--plot", default=None)

    run = sub.add_parser("run", help="target vol on a CSV return series")
    run.add_argument("--input", required=True)
    run.add_argument("--date-col", default="date")
    run.add_argument("--ret-col", default="ret")
    _add_common(run)

    synth = sub.add_parser("synth", help="run on synthetic data")
    synth.add_argument("--n", type=int, default=2520)
    synth.add_argument("--seed", type=int, default=42)
    synth.add_argument("--mu", type=float, default=0.07)
    synth.add_argument("--sigma", type=float, default=0.18)
    _add_common(synth)

    return p


def _run(args) -> int:
    if args.cmd == "run":
        r = load_returns(args.input, date_col=args.date_col, ret_col=args.ret_col)
    else:
        r = synthetic_returns(n_days=args.n, mu=args.mu, sigma=args.sigma, seed=args.seed)

    cfg = VolTargetConfig(
        target_vol=args.target,
        method=args.method,
        window=args.window,
        halflife=args.halflife,
        lag=args.lag,
        leverage_cap=args.cap,
        leverage_floor=args.floor,
    )
    result = VolTargeter(cfg).fit(r)
    result.to_frame().to_csv(args.out)

    stats = summary_stats(result.scaled_returns)
    for k, v in stats.items():
        print(f"{k}: {v:.4f}")

    if args.plot:
        from .plotting import plot_results
        plot_results(result, args.plot)

    return 0


def main() -> int:
    p = _build_parser()
    args = p.parse_args()
    return _run(args)


if __name__ == "__main__":
    sys.exit(main())
