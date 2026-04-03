#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math

class LidarDebug(Node):
    def __init__(self):
        super().__init__('lidar_angle_debug')
        self.sub = self.create_subscription(LaserScan, '/scan', self.callback, 10)
        self.get_logger().info("📡 Subscribed to /scan. Waiting for data...")

    def callback(self, msg: LaserScan):
        # 기본 정보 출력 (한 번만)
        if not hasattr(self, '_once'):
            self._once = True
            self.get_logger().info(
                f"\nangle_min = {math.degrees(msg.angle_min):.2f}°"
                f"\nangle_max = {math.degrees(msg.angle_max):.2f}°"
                f"\nangle_increment = {math.degrees(msg.angle_increment):.3f}°"
                f"\nrange count = {len(msg.ranges)}"
            )

        # 확인할 각도들 (도 단위)
        check_degs = [-120, -90, -60, -30, 0, 30, 60, 90, 120]
        amin = msg.angle_min
        ainc = msg.angle_increment
        n = len(msg.ranges)

        def deg_to_index(deg):
            rad = math.radians(deg)
            idx = int(round((rad - amin) / ainc))
            return max(0, min(idx, n - 1))

        print("\n=== 🔎 LiDAR Distance by Angle ===")
        for d in check_degs:
            i = deg_to_index(d)
            dist = msg.ranges[i]
            if math.isfinite(dist):
                print(f"{d:+4d}° → {dist:.3f} m")
            else:
                print(f"{d:+4d}° → inf")

        print("=" * 40)

def main():
    rclpy.init()
    node = LidarDebug()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
