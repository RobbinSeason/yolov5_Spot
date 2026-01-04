from setuptools import setup
from glob import glob
import os

package_name = 'yolov5_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 安装 launch 文件（注意只复制 *.launch.py）
        (os.path.join('share', package_name, 'launch'), glob('launch/*_launch.py')),
        # 安装 config 目录
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        # 安装 resource 目录（如果需要）
        (os.path.join('share', package_name, 'resource'), glob('resource/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fishros',
    maintainer_email='fishros@foxmail.com',
    description='YOLOv5 ROS2 Inference Node',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "yolo_detect_2d = yolov5_ros2.yolo_detect_2d:main"
        ],
    },
)
