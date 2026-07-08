import math

from hypnos_edge.engine import CircadianState, alertness, step


def test_state_stays_finite_and_bounded():
    state = CircadianState(0.1, 0.1, 0.0)
    dt = 1 / 60
    for _ in range(int(24 / dt)):
        state = step(state, 200.0, dt)
        assert math.isfinite(state.x)
        assert math.isfinite(state.xc)
        assert math.isfinite(state.stim)
        assert abs(state.x) < 10
        assert abs(state.xc) < 10
        assert -0.1 <= state.stim <= 1.1


def test_lux_measurably_changes_trajectory():
    dt = 1 / 60
    n_steps = int(24 / dt) * 3
    dark = CircadianState(0.1, 0.1, 0.0)
    bright = CircadianState(0.1, 0.1, 0.0)
    for _ in range(n_steps):
        dark = step(dark, 0.0, dt)
        bright = step(bright, 1000.0, dt)
    assert abs(dark.x - bright.x) > 1e-3


def test_alertness_is_finite():
    state = CircadianState(0.2, -0.3, 0.5)
    assert math.isfinite(alertness(state))
