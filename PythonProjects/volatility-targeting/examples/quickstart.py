from volatility_targeting import VolTargetConfig, VolTargeter, summary_stats, synthetic_returns

r = synthetic_returns(n_days=2000, sigma=0.25, seed=1)
cfg = VolTargetConfig(target_vol=0.10, window=20, lag=1, leverage_cap=3.0)
res = VolTargeter(cfg).fit(r)

print("raw:")
for k, v in summary_stats(r).items():
    print(f"  {k}: {v:.4f}")

print("targeted:")
for k, v in summary_stats(res.scaled_returns).items():
    print(f"  {k}: {v:.4f}")
