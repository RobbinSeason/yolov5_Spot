# Object Detection (YOLOv5 + ROS 2)

---

## 0. Prerequisites & Dependencies

Before building the workspace, make sure the required dependencies are installed.

> `$ROS_DISTRO` refers to your ROS 2 distribution (e.g. `foxy`, `galactic`, `humble`).

```bash
sudo apt update
sudo apt install python3-pip ros-$ROS_DISTRO-vision-msgs
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple yolov5
```

## 1. Model & File Configuration
YOLOv5 Weights

    best.pt

        Trained YOLOv5 model weights

        Must be placed under the config/ directory

Example structure:

yolov5_ws/
└── src/
    └── yolov5_ros2/
        └── config/
            └── best.pt

## 2. Parameter Configuration & Camera Selection

The main launch file is:

yolov5_ros2_launch.py

In this file, you can configure:
Detection Parameters

Camera Topics

Make sure the selected topics match the actual robot camera configuration.

## 3. Build & Launch

Build the workspace and source the environment:

cd yolov5_ws
colcon build
source install/setup.bash

Launch the object detection node:

ros2 launch yolov5_ros2 yolov5_ros2_launch.py

## 4. Output Topic & Message Format

Detection results are published on the following topic:

/Vision_result_Team3

Message Overview (only key info)

frame_id: spot/body        # reference coordinate frame
class_id: ball             # detected object class
score: 0.8171692490577698  # detection confidence
position:                 # 3D position after TF transformation
  x: -1.1204
  y: -0.4977
  z: -0.5264
