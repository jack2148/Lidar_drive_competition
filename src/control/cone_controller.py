#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, Float32

class WallFollowAvoidance(Node):
    def __init__(self):
        super().__init__('lidar_cone')

        # === 1. 구독 ===
        self.sub = self.create_subscription(
            Float32MultiArray, '/cone_distances', self.callback, 10)

        # === 2. 발행 ===
        self.steer_pub = self.create_publisher(Float32, '/steering_cmd_deg', 10)

        # === 3. 파라미터 ===
        self.declare_parameter('Kp', 70.0)
        self.declare_parameter('max_steer_deg', 70.0)
        self.declare_parameter('recover_time', 0.2)  # 컵 놓침 시 직진 유지 시간 (초)

        self.Kp = self.get_parameter('Kp').value
        self.max_steer_deg = self.get_parameter('max_steer_deg').value
        self.recover_time = self.get_parameter('recover_time').value

        # === 4. 상태 변수 ===
        self.left = 999.0
        self.right = 999.0
        self.lost_timer = 0.0  # 컵 놓침 누적시간

        # === 5. 10Hz 제어 루프 ===
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("✅ lidar_cone node started (2m recovery mode)")

    # ==========================================================
    def callback(self, msg: Float32MultiArray):
        """거리값 수신 및 저장"""
        if len(msg.data) >= 3:
            _, self.left, self.right = msg.data

            # 유효 범위 필터 (2m 초과는 무시)
            if (not math.isfinite(self.left)) or (self.left > 5.0) or (self.left <= 0.05):
                self.left = 999.0
            if (not math.isfinite(self.right)) or (self.right > 5.0) or (self.right <= 0.05):
                self.right = 999.0

    # ==========================================================
    def control_loop(self):
        """10Hz 조향 계산"""
        steering_deg = 0.0
        left_valid = self.left < 2.0
        right_valid = self.right < 2.0

        # --- ① 양쪽 다 멀리 (컵 놓침 상태) ---
        if not left_valid and not right_valid:
            self.lost_timer += 0.1
            if self.lost_timer < self.recover_time:
                # 짧게 직진하며 다시 인식 대기
                steering_deg = 0.0
                self.get_logger().info("🟡 Lost both → go straight to recover")
            else:
                # 그래도 복구 안 되면 좌회전으로 탐색
                steering_deg = self.max_steer_deg
                self.get_logger().info("🔄 Still lost → rotate left to search")

        else:
            # --- 정상 복귀 ---
            self.lost_timer = 0.0

            # --- ② 양쪽 감지: 거리차 기반 중심 유지 ---
            if left_valid and right_valid:
                error = self.left - self.right
                steering_deg = self.Kp * (-error)

            # --- ③ 한쪽만 감지 ---
            elif not left_valid:
                steering_deg = self.max_steer_deg  # 왼쪽 안보임 → 오른쪽 회전
            elif not right_valid:
                steering_deg = -self.max_steer_deg # 오른쪽 안보임 → 왼쪽 회전

        # 조향 제한
        steering_deg = max(-self.max_steer_deg, min(steering_deg, self.max_steer_deg))

        # 발행
        msg = Float32()
        msg.data = float(steering_deg)
        self.steer_pub.publish(msg)

        # 디버그 로그
        self.get_logger().info(f"L={self.left:.2f} R={self.right:.2f} → steer={steering_deg:+.1f}°")

# ==========================================================
def main(args=None):
    rclpy.init(args=args)
    node = WallFollowAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
