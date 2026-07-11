import matplotlib

matplotlib.use("Agg")

import numpy as np

from overfit_aware_signals.plotting import plot_is_oos_rank_scatter, plot_oos_sharpe_hist


def test_plot_oos_sharpe_hist(tmp_path):
    fig = plot_oos_sharpe_hist(
        np.array([0.1, 0.5, -0.2, 0.3, 0.0]), path=tmp_path / "h.png"
    )
    assert fig is not None
    assert (tmp_path / "h.png").exists()


def test_plot_is_oos_rank_scatter(tmp_path):
    t = 40
    rets = np.column_stack([np.full(t, 0.05), np.full(t, 0.0)])
    fig = plot_is_oos_rank_scatter(rets, n_groups=4, path=tmp_path / "s.png")
    assert fig is not None
    assert (tmp_path / "s.png").exists()
