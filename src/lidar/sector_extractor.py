#!/usr/bin/env python3
"""
LiDAR 섹터 거리 추출기 (FRONT / LEFT / RIGHT 모두 범위 평균)
- 각 섹터: 하위 10% 평균 + 10m 이하 필터링
- EMA (지수 이동 평균)로 부드러운 추적
"""
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray

class LidarIndexReader(Node):
    def __init__(self):
        super().__init__('lidar_cone')

        # === QoS ===
        qos = QoSProfile(depth=100)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT

        # === Subscribers / Publishers ===
        self.sub = self.create_subscription(LaserScan, '/scan', self.callback, qos)
        self.dist_pub = self.create_publisher(Float32MultiArray, '/cone_distances', 10)

        # === 각도 섹터 정의 ===
        # (G6 기준: 0° = 정면)
        # 필요한 경우 ± 오프셋 조정 가능
        self.sectors_deg = [
            ("FRONT",  -20.0,   20.0),   # 정면 ±20°
            ("LEFT",    60.0,  120.0),   # 왼쪽 60~120°
            ("RIGHT", -120.0,  -60.0),   # 오른쪽 -120~-60°
        ]

        # === 상태 변수 ===
        self.prev = [999.0, 999.0, 999.0]
        self.alpha = 0.6  # EMA 비율
        self.get_logger().info("✅ Lidar front-sides range reader started")

    # ----------------------------------------------------------
    def angle_to_index(self, theta_deg, amin, ainc, n):
        """도 단위 각도를 LiDAR 인덱스로 변환"""
        theta = math.radians(theta_deg)
        idx = int(round((theta - amin) / ainc))
        return max(0, min(idx, n - 1))

    # ----------------------------------------------------------
    def sector_indices(self, dmin, dmax, amin, ainc, n):
        """섹터 각도 범위를 인덱스 리스트로 변환"""
        i1 = self.angle_to_index(dmin, amin, ainc, n)
        i2 = self.angle_to_index(dmax, amin, ainc, n)
        if i2 >= i1:
            return list(range(i1, i2 + 1))
        else:
            # wrap-around
            return list(range(i1, n)) + list(range(0, i2 + 1))

    # ----------------------------------------------------------
    def sector_avg_distance(self, ranges, idxs, rmin, rmax):
        """섹터 내 하위 10% 평균 (10m 이하만 포함)"""
        vals = [ranges[i] for i in idxs if math.isfinite(ranges[i]) and rmin <= ranges[i] <= min(rmax, 10.0)]
        if not vals:
            return float('inf')

        vals.sort()
        k = max(1, len(vals) // 10)
        low_vals = vals[:k]
        return sum(low_vals) / len(low_vals)

    # ----------------------------------------------------------
    def callback(self, msg: LaserScan):
        n = len(msg.ranges)
        if n == 0:
            return

        amin = msg.angle_min
        ainc = msg.angle_increment
        rmin = max(msg.range_min, 0.1)
        rmax = msg.range_max

        # 섹터별 거리 계산
        distances = []
        for name, dmin, dmax in self.sectors_deg:
            idxs = self.sector_indices(dmin, dmax, amin, ainc, n)
            d = self.sector_avg_distance(msg.ranges, idxs, rmin, rmax)
            distances.append(d if math.isfinite(d) else 999.0)

        # EMA (지수 이동 평균)
        smoothed = []
        for d, p in zip(distances, self.prev):
            if d >= 999.0:
                smoothed.append(p)
            elif p >= 999.0:
                smoothed.append(d)
            else:
                smoothed.append(self.alpha * d + (1 - self.alpha) * p)
        self.prev = smoothed

        # Publish
        msg_out = Float32MultiArray()
        msg_out.data = smoothed
        self.dist_pub.publish(msg_out)

        # Debug
        self.get_logger().info(
            f"FRONT={smoothed[0]:.2f}  LEFT={smoothed[1]:.2f}  RIGHT={smoothed[2]:.2f}"
        )

# ==========================================================
def main(args=None):
    rclpy.init(args=args)
    node = LidarIndexReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
