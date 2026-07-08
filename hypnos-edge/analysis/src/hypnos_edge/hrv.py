from __future__ import annotations

import numpy as np


def rmssd(ibi_ms: np.ndarray) -> float:
    if len(ibi_ms) < 2:
        raise ValueError("rmssd needs >= 2 intervals")
    d = np.diff(ibi_ms)
    return float(np.sqrt(np.mean(d**2)))


def sdnn(ibi_ms: np.ndarray) -> float:
    if len(ibi_ms) < 2:
        raise ValueError("sdnn needs >= 2 intervals")
    return float(np.std(ibi_ms, ddof=1))
