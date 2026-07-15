# fire-ice-write

Webcam hand-tracking particle thing. Left hand makes fire particles, right makes ice. Bring both close and they fuse. Point your index finger to draw trails.

Adapted from [upendra8690/fire-ice-write](https://github.com/upendra8690/fire-ice-write) — see ATTRIBUTION.md. MIT.

## run

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # windows
# source .venv/bin/activate    # mac/linux
pip install -r requirements.txt
python main.py
```

needs a webcam. mediapipe is pinned to 0.10.21 because newer builds dropped the Hands Solutions API.

## controls

- left hand → fire
- right hand → ice
- both hands close → fusion
- point index → draw
- fist → explode particles
- q quit, r reset, s screenshot, f fullscreen
- b toggle stars
- 1 / 2 / 3 colour themes

## notes

particle count defaults to ~1000 (upstream had 6000 which melts a laptop). camera capped at 640x480, hands model_complexity=0. tweak `PARTICLE_COUNT` in main.py if you want more juice or more fps.

if cam doesn't open try `cv2.VideoCapture(1)`. if mediapipe blows up about solutions, reinstall the pinned version from requirements.txt.
