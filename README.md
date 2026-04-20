# Endokelp_Projects

This repo is basically my public junk drawer—but organized. I keep small projects here while I learn, break things, and slowly nudge my work toward quant and ML research.

If something looks half-finished, it probably is.

## PythonProjects

I added a `PythonProjects/` folder for Python work that’s a bit more “portfolio-shaped.” The idea is to collect a few end-to-end projects I can point to on a resume: data in, assumptions explicit, tests where it matters, and a README that explains what I did (and what I didn’t claim).

What I’m planning to build there, in order:

1. **Volatility targeting** — scale exposure to chase a vol target without pretending the world is neat and stationary.
2. **Momentum backtest (from scratch)** — signals, rebalances, costs, and the boring stuff that keeps a backtest honest.
3. **Monte Carlo (GBM)** — simulate paths, check convergence, maybe poke at variance reduction if I’m feeling brave.
4. **Options pricing (Black–Scholes)** — Europeans, Greeks, and tests against reference cases so I’m not just trusting a formula I copied.
5. **Portfolio risk dashboard** — a small Streamlit (or similar) front-end on top of an analytics core I can actually unit test.

Nothing here is production trading advice. It’s practice.

## What’s here right now

**Java — Ultimate even/odd** (`UltimateEven_Odd.java`)  
A console program that takes numbers, prints them back, labels even vs odd, and can optionally spit out basic list stats (mean, mode, standard deviation, that kind of thing).

**Python — Snake** (`snake_game.py`)  
Snake, but a little unhinged: you can spawn enemies that chase you Pac-Man ghost style, there are two maps, three speed levels, and a high score file that actually persists (so your best run sticks around).

**Website template** (`ProfessionalPersonalWebsiteTemplate/`)  
A Vite + React template I made for portfolio sites—mostly so future-me doesn’t start from a blank folder every time.

## Robotics

There’s also a `robotics java projects/` folder for older coursework-style Java bits.

---

If you’re browsing: start with whatever folder matches the language you care about. If you’re me, six months from now: please remember to commit more often.
