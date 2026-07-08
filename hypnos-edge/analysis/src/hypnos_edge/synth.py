from __future__ import annotations

import numpy as np


def synth_ibi(
    n: int, hr_mean: float = 65.0, hr_std: float = 5.0, seed: int | None = None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    hr = np.clip(rng.normal(hr_mean, hr_std, n), 40.0, 180.0)
    return 60000.0 / hr


def inject_artifacts(
    ibi: np.ndarray, drop_p: float, spurious_p: float, motion_p: float, seed: int | None = None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out: list[float] = []
    for v in ibi:
        r = rng.random()
        if r < drop_p and out:
            out[-1] += v  # missed beat: merge into previous interval
        elif r < drop_p + spurious_p:
            half = v / 2
            out.extend([half, half])  # spurious beat: split in two
        else:
            out.append(v)
    arr = np.array(out)

    run_len = 5
    i = 0
    while i < len(arr):
        if rng.random() < motion_p:
            j = min(i + run_len, len(arr))
            arr[i:j] *= rng.uniform(0.7, 1.3)  # motion burst: scale a short contiguous run
            i = j
        else:
            i += 1
    return arr
