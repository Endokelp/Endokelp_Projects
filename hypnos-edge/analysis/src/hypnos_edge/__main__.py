from __future__ import annotations

import math

from .engine import CircadianState, alertness, step
from .policy import decide


def _lux_at(hour: float) -> float:
    if 6 <= hour <= 18:
        return 500.0 * math.sin(math.pi * (hour - 6) / 12)
    return 0.0


def demo() -> None:
    state = CircadianState(x=0.0, xc=1.0, stim=0.0)
    dt = 1 / 60
    n_steps = int(24 / dt)
    check_hours = {0, 6, 9, 12, 15, 18, 22}
    prev = None
    for i in range(n_steps):
        hour = i * dt
        lux = _lux_at(hour)
        state = step(state, lux, dt)
        if int(hour) in check_hours and abs(hour - int(hour)) < dt:
            a = alertness(state)
            rec = decide(a, lux, is_work_window=9 <= hour <= 17, prev=prev)
            print(
                f"t={hour:5.1f}h lux={lux:6.1f} alertness={a:+.3f} "
                f"-> light={rec.light_action:11s} risk={rec.risk_label:9s} | {rec.caffeine_note}"
            )
            prev = rec
            check_hours.discard(int(hour))


if __name__ == "__main__":
    demo()
