import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    base_path = '/home/chan/Lidar_drive_competition'
    
    ydlidar_params_file = os.path.join(base_path, 'config', 'ydlidar_g6_cone.yaml')

    # YDLIDAR Driver Node
    ydlidar_driver_node = Node(
        package='ydlidar_ros2_driver',
        executable='ydlidar_ros2_driver_node',
        name='ydlidar_ros2_driver_node',
        output='screen',
        emulate_tty=True,
        parameters=[ydlidar_params_file]
    )

    # Sector Extractor Node (거리값 추출)
    extractor_node = ExecuteProcess(
        cmd=['python3', os.path.join(base_path, 'src', 'lidar', 'sector_extractor.py')],
        output='screen'
    )

    # Cone Controller Node (조향 제어)
    controller_node = ExecuteProcess(
        cmd=['python3', os.path.join(base_path, 'src', 'control', 'cone_controller.py')],
        output='screen'
    )

    return LaunchDescription([
        ydlidar_driver_node,
        extractor_node,
        controller_node
    ])
