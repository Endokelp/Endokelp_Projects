# hypnos-edge — State
Vision: Real ESP32-S3 + MAX30102 (PPG/HR) + BH1750 (light) sensor node running on-device TFLite Micro inference, closing the loop with REAL physiological data instead of simulation (the ISEF "Hypnos" project's never-built real-time Plan B). Core research contribution: rigorous on-device ML evaluation (int8 quantization ablation, on-device-vs-laptop runtime parity, latency, memory). n=1 self-experiment, stated honestly. Safety-scoped: light-only actuation, caffeine advisory-only (no autonomous stimulant-dosing loop).
Stack: Python 3.11+ analysis package (numpy/pandas/tensorflow/scikit-learn/matplotlib) + PlatformIO firmware, `framework=arduino` (ponytail: vendor sensor libraries — SparkFun MAX3010x, Christopher Laws BH1750 — not hand-rolled I2C drivers; a maintained library reading a well-known chip correctly isn't reinventing the wheel. Arduino-ESP32 core also has more turnkey TFLite Micro integration paths than raw ESP-IDF — less toolchain risk for a solo build).
Run (Phase 1, `analysis/` only — no hardware yet): `cd analysis && pip install -e ".[dev]" && pytest -v && ruff check src/ tests/`

## Done
- P1: hardware-independent core logic — `engine.py` (Forger-99 RK4, from-scratch, cited), `policy.py` (safety-scoped, hysteresis via optional `prev` kwarg), `synth.py`, `hrv.py` built. `pip install -e ".[dev]"` clean, `pytest -v` 14/14 green, `ruff check` clean, `python -m hypnos_edge` demo runs: alertness swings -0.84 (6am) to +1.15 (6pm) tracking the lux curve; caffeine_note never an actionable token in any test case.

## Current phase: 2 — ML pipeline on synthetic data (still hardware-independent)
Goals (`analysis/` package only — `firmware/` is Phase 3+):
- `model.py`: small dense MLP (32-IBI window -> `log1p(RMSSD_ms)`), tf.keras
- `train.py`: trains on `synth.py` + `inject_artifacts` output (robust-to-artifacts framing — the actual justification for using ML instead of the closed-form formula)
- `quantize.py`: `export_fp32`/`export_int8` via `TFLiteConverter` (`representative_dataset`, `TFLITE_BUILTINS_INT8`)
- `export_header.py`: pure-Python `.tflite` -> C-array header emitter (no `xxd`, Windows-friendly) — writes what `firmware/src/model_data.h` will need later
- First-pass float32-vs-int8 ablation on synthetic data (provisional numbers, real numbers come once hardware sessions exist)
Done-when: `pip install -e ".[dev]"` succeeds (now adding tensorflow/scikit-learn/matplotlib); `pytest -v` green; `ruff check` clean; the synthetic ablation runs end-to-end and prints a plausible (non-degenerate) fp32-vs-int8 accuracy delta.

## Decisions
- Vendor Arduino libraries for MAX30102/BH1750, not hand-rolled I2C drivers (ponytail flip from initial design — a real driver is not "a few lines," a maintained library already does it correctly).
- `framework=arduino` in PlatformIO, not `framework=espidf` — fewer toolchain-version-mismatch risks for a solo build; Arduino-ESP32 core's TFLite Micro integration is more turnkey.
- Fingertip PPG placement, not wrist — RMSSD error is ~12x worse on wrist under contact-pressure drift (peer-reviewed). Session-based measurement, not continuous wearable — deliberate scope, not a limitation to apologize for.
- No caffeine-actuation loop, ever — a hobby-grade, non-clinical sensor should not autonomously drive real stimulant intake. Light-only actuation (safe, physically closeable via relay+lamp stretch goal later).
- n=1 framing stated explicitly in README — MAX30102 is not medical-grade per its own docs; "ground truth" is the researcher's own classical computation, not clinical reference.
- Session-level (not row-level) train/test split once real data arrives — same lookahead-discipline as this repo's momentum-backtest.

## Gotchas
- ESP32-S3 specifically (has PIE/hardware SIMD via ESP-NN) — not plain ESP32 or C3, which lack it.
- Google renamed TFLite -> "LiteRT" (2024 rebrand) — same underlying tech/API, don't be thrown by doc naming drift.
- `data/sessions/` (real logged biosignal data) must be gitignored by default once created — public repo, personal data.

## Key files
- `analysis/src/hypnos_edge/engine.py` — Forger-99 reimplementation, everything downstream depends on this being right
- `analysis/src/hypnos_edge/policy.py` — safety-scoped decision logic
- `analysis/src/hypnos_edge/synth.py` — synthetic data enabling all pre-hardware development/testing
- Full design (firmware modules, evaluation plan, cost breakdown, phases 2-10): `C:\Users\venni\.claude\plans\sorted-gathering-willow.md`
