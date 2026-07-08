from __future__ import annotations

from dataclasses import dataclass

_LO_ENTER, _LO_EXIT = 0.30, 0.40  # alertness bands: below _LO_ENTER -> high_risk
_HI_ENTER, _HI_EXIT = 0.70, 0.60  # above _HI_ENTER -> low_risk
_DIM_LUX, _BRIGHT_LUX = 100.0, 300.0


@dataclass
class Recommendation:
    light_action: str
    risk_label: str
    caffeine_note: str


def _band(alertness: float, prev_label: str | None) -> str:
    if prev_label == "high_risk":
        if alertness < _LO_EXIT:
            return "high_risk"
    elif prev_label == "low_risk":
        if alertness > _HI_EXIT:
            return "low_risk"
    if alertness < _LO_ENTER:
        return "high_risk"
    if alertness > _HI_ENTER:
        return "low_risk"
    return "nominal"


def decide(
    alertness: float,
    lux: float,
    is_work_window: bool,
    prev: Recommendation | None = None,
) -> Recommendation:
    band = _band(alertness, prev.risk_label if prev else None)

    light_action = "maintain"
    if band == "high_risk" and is_work_window and lux < _DIM_LUX:
        light_action = "seek_bright"
    elif band != "high_risk" and not is_work_window and lux > _BRIGHT_LUX:
        light_action = "seek_dark"

    # safety invariant: caffeine_note is always plain advisory text, never one of
    # light_action's tokens, never structured — this project never auto-actuates caffeine
    notes = {
        "high_risk": "alertness low; caffeine is a personal choice, not a system action",
        "nominal": "alertness moderate; timing any caffeine relative to sleep is your call",
        "low_risk": "alertness adequate; no stimulant need indicated",
    }
    return Recommendation(light_action, band, notes[band])
