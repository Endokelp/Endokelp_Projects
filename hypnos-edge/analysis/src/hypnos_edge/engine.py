from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Forger, Jewett & Kronauer 1999, J Biol Rhythms 14(6):532-7 — reimplemented from scratch,
# structure only. Constants below are approximate/illustrative, not clinically calibrated.
TAU_X = 24.2  # h, intrinsic circadian period
MU = 0.23  # stiffness / non-orthogonality
Q = 1.0 / 3.0
K_LIGHT = 0.55  # light-drive coupling into xc
ALPHA_MAX = 0.10  # max saturating light-drive term
LUX_HALF = 150.0  # lux at half-maximal drive
KA = 0.15  # /h, stim compartment absorption-ish pull
KE = 0.35  # /h, stim compartment elimination rate


@dataclass
class CircadianState:
    x: float
    xc: float
    stim: float


def _deriv(x: float, xc: float, stim: float, lux: float) -> tuple[float, float, float]:
    # ponytail: full Forger/Kronauer models track a 3rd dynamic photoreceptor state `n`;
    # collapsed here to an instantaneous saturating function of lux to stay within the
    # 2-oscillator-state (x, xc) + stim dataclass. Upgrade path: add n as a 4th state
    # if higher fidelity is ever needed.
    alpha = ALPHA_MAX * lux / (lux + LUX_HALF)
    b = alpha * (1 - 0.4 * x) * (1 - 0.4 * xc)
    dx = (np.pi / 12) * (xc + MU * (x / 3 + (4 * x**3) / 3 - (256 * x**7) / 105) + b)
    dxc = (np.pi / 12) * (Q * b * xc - x * ((24 / (0.99669 * TAU_X)) ** 2 + K_LIGHT * b))
    dstim = KA * (1 - stim) - KE * stim
    return dx, dxc, dstim


def step(state: CircadianState, lux: float, dt_h: float) -> CircadianState:
    x0, xc0, s0 = state.x, state.xc, state.stim
    k1 = _deriv(x0, xc0, s0, lux)
    k2 = _deriv(x0 + dt_h / 2 * k1[0], xc0 + dt_h / 2 * k1[1], s0 + dt_h / 2 * k1[2], lux)
    k3 = _deriv(x0 + dt_h / 2 * k2[0], xc0 + dt_h / 2 * k2[1], s0 + dt_h / 2 * k2[2], lux)
    k4 = _deriv(x0 + dt_h * k3[0], xc0 + dt_h * k3[1], s0 + dt_h * k3[2], lux)
    x1 = x0 + (dt_h / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
    xc1 = xc0 + (dt_h / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    s1 = s0 + (dt_h / 6) * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
    return CircadianState(x1, xc1, s1)


def alertness(state: CircadianState) -> float:
    # convention for this sim: alertness falls as x rises, rises with stim — a defined
    # modeling choice here, not a clinically validated phase mapping
    return float(-state.x + 0.5 * state.stim)
