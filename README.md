# Endokelp_Projects

Public experiments, quant finance scripts, robotics demos, and the portfolio template behind **[endokelp.com](https://endokelp.com)**.

Main portfolio site code lives in [Endokelp/Endoweb](https://github.com/Endokelp/Endoweb). This repo is the grab bag: research packages, Java robotics sims, Snake, and coursework.

---

## Python projects

**overfit-aware-signals** (`PythonProjects/overfit-aware-signals/`) — flagship quant package

Most student backtests print one Sharpe and stop. That number is easy to inflate when you try several ideas. This package evaluates three real cross-sectional equity signals (12-1 momentum, one-month reversal, low-vol) with the overfitting toolkit from primary sources: purged CV with lookback-aware embargo, combinatorial purged CV, the Deflated Sharpe Ratio, and Probability of Backtest Overfitting. The centerpiece is an honest per-signal PASS/FAIL verdict under fixed thresholds, not a vanity Sharpe chart. Live run on ~50 US names (2005–2026) is documented in the package README, including a survivorship caveat (current constituents, not a point-in-time panel). Offline demo: `python -m overfit_aware_signals synth`. Live: `python -m overfit_aware_signals run`. Not trading advice.

**MPT** (`PythonProjects/portfolio_mpt/`)

Mean-variance portfolio playground. Pulls prices from Yahoo, builds expected returns and a covariance matrix, then runs efficient frontier, tangency, equal-weight and MVP comparisons, plus a Monte Carlo pass over random long-only weights. Longer multi-asset backtest path with correlation heatmaps, drawdowns, and equity-style plots if you feed it the bigger workbook. Shared matplotlib style so plots do not look like default neon homework. Not trading advice. Details in that folder’s README.

**volatility-targeting** (`PythonProjects/volatility-targeting/`)

Scales a daily return series so realized vol tracks a target. Rolling std and EWMA estimators, capped/floored leverage, and a one-bar lag on the scaler so nothing peeks at the return it is sizing. CLI for CSVs or synthetic data, pytest coverage, ruff. Details in that folder’s README.

**momentum-backtest** (`PythonProjects/momentum-backtest/`)

From-scratch monthly cross-sectional momentum engine (signal, portfolio formation, rebalance loop, analytics). No black-box backtest framework. Details in that folder’s README.

---

## Robotics projects

Old Java coursework style demos: grids, fake sensors, and console output, not real hardware.

A. `AutonomousNavigation.java`  
B. `PIDController.java`  
C. `RobotArmKinematics.java`  
D. `RobotCommunication.java`, `SensorFusion.java`, `VisionProcessing.java`  

---

## Portfolio template

`ProfessionalPersonalWebsiteTemplate/` is the codebase behind my portfolio site **endokelp.com**. Fork or copy it if you want a starting point or layout ideas. It is Vite, React, TypeScript, and Tailwind.

---

## Snake game

`snake_game.py` is Snake with optional chasing enemies, two maps, speed levels, and a high score file that persists.

## Ultimate even / odd

`UltimateEven_Odd.java` is a CLI: you type numbers, it prints them back labeled even or odd, and can show basic list stats if you want.
