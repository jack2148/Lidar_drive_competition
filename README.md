# Lidar_drive_competition

## 🇰🇷 한국어 버전 (Korean Version)

### 1. 개요 (Overview)

<p align="center">
  <img src="assets/hardware_1.png" alt="로봇 하드웨어 설정 1" width="30%">
  <img src="assets/hardware_2.png" alt="로봇 하드웨어 설정 2" width="30%">
  <img src="assets/map.png" alt="콘 주행 맵" width="30%">
</p>

이 저장소는 IRO 콘 주행 실험을 재현 가능한 ROS 2 케이스 스터디로 정리한 것입니다. 스캔 보정, 섹터 기반 거리 추출, 차분 기반 스티어링 제어로 구성된 LiDAR 전용 반응형 내비게이션 파이프라인을 구현했습니다. 최종 설정에서 작업을 안정적으로 완료하지는 못했으나, 본 프로젝트를 통해 센서 방향/설정 불일치 및 좁은 간격의 근거리 콘 감지에서 발생하는 센서-작업 불일치라는 두 가지 중요한 엔지니어링 이슈를 확인했습니다.

### 2. 주요 기여 (My Contribution)

주요 기여는 원시 `/scan` 데이터에서 조향 명령에 이르는 엔드투엔드 LiDAR 파이프라인을 구축한 것입니다. 여기에는 다음이 포함됩니다:
- 각도-인덱스 보정
- 섹터 기반 거리 추상화
- 노이즈 필터링
- 콘 내비게이션을 위한 반응형 조향 로직

또한 실패 모드를 분석하고 드라이버 파라미터와 인지 로직을 수정했습니다.

### 3. 시스템 파이프라인 (System Pipeline)

파이프라인 구조는 다음과 같습니다:

`LaserScan -> 섹터 추출 -> 필터링된 좌/우/전방 거리 -> 조향 명령`

인지 모듈은 유효 범위 필터링, 하위 백분위수 집계, EMA 평활화를 사용하여 원시 스캔 데이터를 강인한 섹터 거리로 변환합니다. 제어기는 좌우 거리 차이로 조향을 계산하며, 양쪽이 모두 유실될 경우 복구 모드로 전환합니다.

### 4. 실패 분석 (Failure Analysis)

최종 성능을 저해한 두 가지 주요 이슈는 다음과 같습니다:

1. **센서 방향 불일치 (Sensor Orientation Mismatch)**: LiDAR가 실제 장착 방향과 반대로 설정되어 물리적 설치와 드라이버 설정 사이에 불일치가 발생했습니다.
2. **센서-작업 불일치 (Sensor-Task Mismatch)**: YDLIDAR G6는 본 콘 배치 환경에 적합하지 않았습니다. 콘 간격이 좁고 요구되는 감지 범위가 매우 짧아 안정적인 근거리 콘 인지가 어려웠습니다.

### 5. 수정 시도 (Fixes Attempted)

불안정한 반사값을 줄이기 위해 스캔 관련 파라미터를 수정하고, 작업 관련 임계값 이상의 비현실적인 중앙 감지값을 무시하도록 인지 로직을 강화했습니다. 또한 차량이 콘 사이의 중앙을 유지하도록 단순 거리 차이 기반 조향으로 제어기 구조를 재편했습니다.

### 6. 결과 (Result)

최종 설정은 작업을 안정적으로 완료할 만큼 견고하지 못했습니다. 하지만 본 프로젝트를 통해 다음 두 가지 실질적인 교훈을 얻었습니다:
- LiDAR 설정은 제어기 튜닝 전 실제 장착 방향과 대조하여 검증되어야 합니다.
- 센서 선택은 특히 좁은 간격의 근거리 주행 시 작업 기하 구조와 일치해야 합니다.

---

## 🇺🇸 English Version

### 1. Overview

<p align="center">
  <img src="assets/hardware_1.png" alt="Robot Hardware Setup 1" width="30%">
  <img src="assets/hardware_2.png" alt="Robot Hardware Setup 2" width="30%">
  <img src="assets/map.png" alt="Cone Driving Map" width="30%">
</p>

This repository reorganizes my IRO cone-driving experiment into a reproducible ROS 2 case study. I implemented a LiDAR-only reactive navigation pipeline consisting of scan calibration, sector-based distance extraction, and difference-based steering control. Although the final setup did not complete the task reliably, the project exposed two important engineering issues: sensor orientation/configuration mismatch and sensor-task mismatch in narrow-gap near-range cone detection.

### 2. My Contribution

My main contribution was building the end-to-end LiDAR pipeline from raw `/scan` data to steering commands. This included:
- Angle-index calibration
- Sector-based distance abstraction
- Noise filtering
- Reactive steering logic for cone navigation

I also analyzed the failure modes and revised both the driver parameters and the perception logic.

### 3. System Pipeline

The pipeline is structured as follows:

`LaserScan -> sector extraction -> filtered left/right/front distances -> steering command`

The perception module converts raw scan data into robust sector distances using valid-range filtering, lower-percentile aggregation, and EMA smoothing. The controller then computes steering from the left-right distance difference and switches to a recovery mode when both sides are lost.

### 4. Failure Analysis

Two major issues limited the final performance:

1. **Sensor Orientation Mismatch**: The LiDAR was mounted in the opposite direction during one setup, which caused an orientation mismatch between the physical installation and the driver configuration.
2. **Sensor-Task Mismatch**: The YDLIDAR G6 was not a good sensor-task match for this cone configuration. The cone spacing was narrow and the required detection range was very short, which made stable near-range cone perception difficult.

### 5. Fixes Attempted

I revised the scan-related parameters to reduce unstable returns and tightened the perception logic to ignore implausible center readings above a task-specific threshold. I also restructured the controller around simple distance-difference steering to keep the vehicle centered between the cones.

### 6. Result

The final setup was not robust enough to complete the task reliably. However, this project provided two practical lessons:
- LiDAR configuration must be validated against the real mounting direction before controller tuning.
- Sensor selection must match the task geometry, especially in narrow-gap near-range navigation.

### 7. Lessons Learned

This project taught me how to:
- Interpret raw `LaserScan` data.
- Build a simple reactive controller from sector distances.
- Diagnose failures caused by the interaction between sensor limits and task design.

### 8. Repository Contents

- `scan_angle_debug.py`: verifies angle-index mapping
- `sector_extractor.py`: converts raw scans into robust sector distances
- `cone_controller.py`: computes steering from distance differences
- `ydlidar_g6_cone.yaml`: driver configuration
- `failure_analysis.md`: documents failure modes and fixes