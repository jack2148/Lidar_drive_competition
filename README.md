# Lidar_drive_competition

## 1. Overview

<p align="center">
  <img src="assets/hardware_setup.jpg" alt="Robot Hardware Setup" width="45%">
  <img src="assets/cone_map_home_setup.jpg" alt="Cone Driving Map" width="45%">
</p>

This repository reorganizes my IRO cone-driving experiment into a reproducible ROS 2 case study. I implemented a LiDAR-only reactive navigation pipeline consisting of scan calibration, sector-based distance extraction, and difference-based steering control. Although the final setup did not complete the task reliably, the project exposed two important engineering issues: sensor orientation/configuration mismatch and sensor-task mismatch in narrow-gap near-range cone detection.

## 2. My Contribution

My main contribution was building the end-to-end LiDAR pipeline from raw `/scan` data to steering commands. This included:
- Angle-index calibration
- Sector-based distance abstraction
- Noise filtering
- Reactive steering logic for cone navigation

I also analyzed the failure modes and revised both the driver parameters and the perception logic.

## 3. System Pipeline

The pipeline is structured as follows:

`LaserScan -> sector extraction -> filtered left/right/front distances -> steering command`

The perception module converts raw scan data into robust sector distances using valid-range filtering, lower-percentile aggregation, and EMA smoothing. The controller then computes steering from the left-right distance difference and switches to a recovery mode when both sides are lost.

## 4. Failure Analysis

Two major issues limited the final performance:

1. **Sensor Orientation Mismatch**: The LiDAR was mounted in the opposite direction during one setup, which caused an orientation mismatch between the physical installation and the driver configuration.
2. **Sensor-Task Mismatch**: The YDLIDAR G6 was not a good sensor-task match for this cone configuration. The cone spacing was narrow and the required detection range was very short, which made stable near-range cone perception difficult.

## 5. Fixes Attempted

I revised the scan-related parameters to reduce unstable returns and tightened the perception logic to ignore implausible center readings above a task-specific threshold. I also restructured the controller around simple distance-difference steering to keep the vehicle centered between the cones.

## 6. Result

The final setup was not robust enough to complete the task reliably. However, this project provided two practical lessons:
- LiDAR configuration must be validated against the real mounting direction before controller tuning.
- Sensor selection must match the task geometry, especially in narrow-gap near-range navigation.

## 7. Lessons Learned

This project taught me how to:
- Interpret raw `LaserScan` data.
- Build a simple reactive controller from sector distances.
- Diagnose failures caused by the interaction between sensor limits and task design.

## 8. Repository Contents

- `scan_angle_debug.py`: verifies angle-index mapping
- `sector_extractor.py`: converts raw scans into robust sector distances
- `cone_controller.py`: computes steering from distance differences
- `ydlidar_g6_cone.yaml`: driver configuration
- `failure_analysis.md`: documents failure modes and fixes