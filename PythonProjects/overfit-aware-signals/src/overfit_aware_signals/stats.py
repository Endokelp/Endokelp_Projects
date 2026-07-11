import math
from statistics import NormalDist

# Euler–Mascheroni; math.euler_gamma is 3.12+ (package targets 3.11+)
_EULER_GAMMA = 0.5772156649015329


def probabilistic_sharpe_ratio(
    sr: float,
    t: int,
    *,
    skew: float,
    kurt: float,
    sr_star: float = 0.0,
) -> float:
    if t < 2:
        raise ValueError(f"T must be >= 2, got {t}")
    # kurt = γ4 (non-excess); normal → 3. Bailey & López de Prado 2014 Eq.(2)
    den = math.sqrt(1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr * sr)
    if den == 0.0:
        raise ValueError("PSR denominator is zero")
    z = (sr - sr_star) * math.sqrt(t - 1) / den
    return NormalDist().cdf(z)


def expected_max_sharpe(n_trials: int, var_sr: float) -> float:
    if n_trials < 2:
        raise ValueError(f"n_trials must be >= 2, got {n_trials}")
    if var_sr < 0.0:
        raise ValueError(f"var_sr must be >= 0, got {var_sr}")
    if var_sr == 0.0:
        return 0.0
    inv = NormalDist().inv_cdf
    g = _EULER_GAMMA
    return math.sqrt(var_sr) * (
        (1.0 - g) * inv(1.0 - 1.0 / n_trials)
        + g * inv(1.0 - 1.0 / (n_trials * math.e))
    )


def deflated_sharpe_ratio(
    sr: float,
    t: int,
    n_trials: int,
    *,
    skew: float,
    kurt: float,
    var_sr: float,
) -> float:
    sr0 = expected_max_sharpe(n_trials, var_sr)
    return probabilistic_sharpe_ratio(sr, t, skew=skew, kurt=kurt, sr_star=sr0)
