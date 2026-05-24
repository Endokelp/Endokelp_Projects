import pandas as pd
import pytest

from momentum_backtest.portfolio import form_weights_long_only, form_weights_long_short


def test_long_only_top1():
    sig = pd.Series({"A": 0.20, "B": -0.20, "C": 0.00})
    w = form_weights_long_only(sig, n_longs=1)
    assert w["A"] == pytest.approx(1.0)
    assert w["B"] == pytest.approx(0.0)
    assert w["C"] == pytest.approx(0.0)


def test_long_only_top2_equal_weight():
    sig = pd.Series({"A": 0.20, "B": -0.20, "C": 0.00})
    w = form_weights_long_only(sig, n_longs=2)
    # A=0.20, C=0.00 are top-2
    assert w["A"] == pytest.approx(0.5)
    assert w["C"] == pytest.approx(0.5)
    assert w["B"] == pytest.approx(0.0)
    assert w.sum() == pytest.approx(1.0)


def test_long_only_weights_sum_to_one():
    sig = pd.Series({"A": 0.3, "B": 0.1, "C": 0.2, "D": -0.1})
    w = form_weights_long_only(sig, n_longs=3)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= 0).all()


def test_long_only_excludes_nan():
    sig = pd.Series({"A": 0.20, "B": float("nan"), "C": 0.10})
    w = form_weights_long_only(sig, n_longs=2)
    # B excluded; top-2 from {A, C}
    assert w["A"] == pytest.approx(0.5)
    assert w["C"] == pytest.approx(0.5)
    assert w["B"] == pytest.approx(0.0)


def test_long_only_all_nan_returns_zero():
    sig = pd.Series({"A": float("nan"), "B": float("nan")})
    w = form_weights_long_only(sig, n_longs=1)
    assert w.sum() == pytest.approx(0.0)


def test_long_only_n_longs_exceeds_assets():
    sig = pd.Series({"A": 0.1, "B": 0.2})
    w = form_weights_long_only(sig, n_longs=10)
    assert w.sum() == pytest.approx(1.0)
    assert w["A"] == pytest.approx(0.5)
    assert w["B"] == pytest.approx(0.5)


def test_long_short_weights_sum_to_zero():
    sig = pd.Series({"A": 0.30, "B": 0.20, "C": -0.10, "D": -0.20})
    w = form_weights_long_short(sig, n_longs=2, n_shorts=2)
    assert w.sum() == pytest.approx(0.0)


def test_long_short_correct_sides():
    sig = pd.Series({"A": 0.30, "B": 0.20, "C": -0.10, "D": -0.20})
    w = form_weights_long_short(sig, n_longs=2, n_shorts=2)
    assert w["A"] == pytest.approx(0.5)
    assert w["B"] == pytest.approx(0.5)
    assert w["C"] == pytest.approx(-0.5)
    assert w["D"] == pytest.approx(-0.5)


def test_long_short_gross_exposure():
    sig = pd.Series({"A": 0.4, "B": 0.1, "C": -0.1, "D": -0.4})
    w = form_weights_long_short(sig, n_longs=1, n_shorts=1)
    assert w.abs().sum() == pytest.approx(2.0)
