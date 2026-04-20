# Robotics Java Projects

Old Java assignments and experiments from a robotics-ish course. Nothing here plugs into real hardware—it’s mostly simulations, grids, and console output.

## What’s in here

- **AutonomousNavigation.java** — grid world, A*, obstacles, prints a little map.
- **PIDController.java** — PID toy with tuning knobs and fake “motor” limits.
- **SensorFusion.java** — Kalman-ish fusion demo with noisy fake sensors.
- **RobotArmKinematics.java** — forward/inverse kinematics practice on a simple arm model.
- **VisionProcessing.java** — very lightweight image-ish grid stuff (not OpenCV).
- **RobotCommunication.java** — fake messages between fake robots.

## Run

```bash
javac Whatever.java
java Whatever
```

Swap `Whatever` for the file you actually want. Some of these might need others on the classpath—if it breaks, read the top of the file for hints.

If you’re expecting industrial-grade robotics code, lower your expectations; this is coursework.
