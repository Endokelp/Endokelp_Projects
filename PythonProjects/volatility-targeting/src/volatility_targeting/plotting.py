import matplotlib.pyplot as plt


def plot_results(result, out_path) -> None:
    sr = result.scaled_returns.dropna()
    rr = (sr / result.scale.replace(0, float("nan"))).dropna()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    (1 + rr).cumprod().plot(ax=ax1, label="raw")
    (1 + sr).cumprod().plot(ax=ax1, label="vol-targeted")
    ax1.set_title("Equity curve (gross)")
    ax1.legend()
    ax1.grid(True)

    result.scale.plot(ax=ax2)
    ax2.set_title("Leverage scale")
    ax2.grid(True)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
