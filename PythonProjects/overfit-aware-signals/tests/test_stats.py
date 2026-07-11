import math
from statistics import NormalDist

import pytest

from overfit_aware_signals.stats import (
    deflated_sharpe_ratio,
    expected_max_sharpe,
    probabilistic_sharpe_ratio,
)


def test_psr_hand_worked_normal_case():
    # Bailey & López de Prado 2014 Eq.(2): SR=1, T=60, γ3=0, γ4=3, SR*=0
    # z = √59 / √1.5 = √(59/1.5)
    z = math.sqrt(59.0 / 1.5)
    expected = NormalDist().cdf(z)
    got = probabilistic_sharpe_ratio(1.0, 60, skew=0.0, kurt=3.0, sr_star=0.0)
    assert got == pytest.approx(expected, rel=1e-12)


def test_psr_sr_star_reduces_probability():
    psr0 = probabilistic_sharpe_ratio(1.0, 60, skew=0.0, kurt=3.0, sr_star=0.0)
    psr_half = probabilistic_sharpe_ratio(1.0, 60, skew=0.0, kurt=3.0, sr_star=0.5)
    assert psr_half < psr0


def test_expected_max_sharpe_hand_worked():
    # SR0 = √var · [(1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N e))]
    n_trials = 10
    var_sr = 1.0 / 59.0
    gamma = 0.5772156649015329
    inv = NormalDist().inv_cdf
    expected = math.sqrt(var_sr) * (
        (1.0 - gamma) * inv(1.0 - 1.0 / n_trials)
        + gamma * inv(1.0 - 1.0 / (n_trials * math.e))
    )
    got = expected_max_sharpe(n_trials, var_sr)
    assert got == pytest.approx(expected, rel=1e-12)


def test_dsr_hand_worked_normal_case():
    # Same moments as PSR fixture; N=10, var_sr = 1/(T-1) under null at SR=0
    sr, t, n_trials = 1.0, 60, 10
    var_sr = 1.0 / (t - 1)
    sr0 = expected_max_sharpe(n_trials, var_sr)
    expected = probabilistic_sharpe_ratio(sr, t, skew=0.0, kurt=3.0, sr_star=sr0)
    got = deflated_sharpe_ratio(
        sr, t, n_trials, skew=0.0, kurt=3.0, var_sr=var_sr
    )
    assert got == pytest.approx(expected, rel=1e-12)
    assert 0.0 < got < 1.0


def test_dsr_more_trials_lowers_probability():
    kwargs = dict(sr=1.0, t=60, skew=0.0, kurt=3.0, var_sr=1.0 / 59.0)
    dsr_few = deflated_sharpe_ratio(n_trials=5, **kwargs)
    dsr_many = deflated_sharpe_ratio(n_trials=100, **kwargs)
    assert dsr_many < dsr_few


def test_psr_rejects_short_sample():
    with pytest.raises(ValueError, match="T"):
        probabilistic_sharpe_ratio(1.0, 1, skew=0.0, kurt=3.0)


def test_expected_max_sharpe_rejects_bad_n():
    with pytest.raises(ValueError, match="n_trials"):
        expected_max_sharpe(1, 0.01)
