# Endokelp_Projects

Public repo where I stash smaller projects: coursework, experiments, and random builds. If something looks rough, it probably is.

---

## Python projects

**MPT** (`PythonProjects/portfolio_mpt/`)

This is a mean variance portfolio playground. It pulls stock prices from Yahoo, builds expected returns and a covariance matrix, then runs the usual optimization stuff: efficient frontier, tangency portfolio, equal weight and MVP comparisons, and a Monte Carlo pass that draws random long only weights so you can see how scattered outcomes are. There is also a longer multi asset backtest path with correlation heatmaps, drawdowns, and equity style plots if you feed it the bigger workbook, plus a small unrelated stats script for a strength vs endurance scatter. Plots use a shared matplotlib style so they are not the default neon homework look. Not trading advice. More detail and run commands are in that folder’s README.

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
