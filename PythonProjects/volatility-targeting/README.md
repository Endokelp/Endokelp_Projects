# volatility-targeting

scale daily returns so realized vol tracks a target — no lookahead.

## What it does

- estimates rolling or EWMA realized vol from a daily return series
- computes a leverage scalar (`target / est_vol`), capped and floored
- applies a configurable lag so the scalar only uses information available before the return date
- ships a CLI for quick runs on CSV data or synthetic series

## Methodology

vol is estimated two ways: a rolling window standard deviation or an EWMA (via pandas `ewm`). both are annualized with √252. the scaler is simply `leverage = target_vol / est_vol`, clipped to `[leverage_floor, leverage_cap]`. the lag (default 1 day) shifts the scalar forward before multiplying: you're using vol estimated through day t−1 to scale the return on day t. that one-day shift is what keeps it live-tradeable — without it you'd be peeking at same-day vol to set same-day size. all annualization uses 252 periods/year throughout.

## Install

from the subproject root:

```bash
pip install -e .[dev]
```

## Usage

```python
from volatility_targeting import synthetic_returns, VolTargeter, VolTargetConfig, summary_stats

r = synthetic_returns(n_days=2520, sigma=0.18, seed=42)
cfg = VolTargetConfig(target_vol=0.10, method="rolling", window=20, lag=1, leverage_cap=3.0)
res = VolTargeter(cfg).fit(r)
print(summary_stats(res.scaled_returns))
```

CLI on a CSV:

```bash
volatility-targeting run --input returns.csv --target 0.10 --method rolling \
    --window 20 --lag 1 --cap 3.0 --floor 0.0 --out out.csv --plot out.png
```

CLI on synthetic data:

```bash
volatility-targeting synth --n 2520 --seed 42 --mu 0.07 --sigma 0.18 \
    --target 0.10 --method ewma --halflife 20 --lag 1 --cap 3.0 --floor 0.0 --out out.csv
```

## Tests

```bash
pytest
```

## Layout

```
src/
  volatility_targeting/
    __init__.py       re-exports public API
    __main__.py       python -m entrypoint
    data.py           load_returns, synthetic_returns
    vol.py            rolling_vol, ewma_vol
    targeting.py      VolTargetConfig, VolTargeter, VolTargetResult
    diagnostics.py    summary_stats, max_drawdown, turnover_proxy
    cli.py            argparse CLI (run / synth subcommands)
    plotting.py       plot_results
tests/
  test_data.py
  test_vol.py
  test_targeting.py
  test_diagnostics.py
```

## Not trading advice

research code, not a signal.
