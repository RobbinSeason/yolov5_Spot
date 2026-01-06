# Object Detection (YOLOv5 + ROS 2)

---

## 0.1 Prerequisites & Dependencies

Before building the workspace, make sure the required dependencies are installed.

> `$ROS_DISTRO` refers to your ROS 2 distribution (e.g. `foxy`, `galactic`, `humble`).

```bash
sudo apt update
sudo apt install python3-pip ros-$ROS_DISTRO-vision-msgs
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple yolov5
```

## 0.2 Clone repository

```bash
mkdir -p yolov5_ws/src
cd yolov5_ws/src
git clone https://github.com/RobbinSeason/yolov5_Spot
```

## 1. Model & File Configuration

YOLOv5 Weights:

```bash
best.pt
```

Trained YOLOv5 model weights must be placed under the config/ directory

Example structure:

```bash
yolov5_ws/
└── src/
    └── yolov5_ros2/
        └── config/
            └── best.pt
```

## 2. Parameter Configuration & Camera Selection

The main launch file is:

```bash
yolov5_ros2_launch.py
```

In this file, you can configure:

1.Detection Parameters

2.Camera Topics

Make sure the selected topics match the actual robot camera configuration.

The main function file is:

```bash
yolo_detect_2d.py
```

## 3. Build & Launch

Build the workspace and source the environment:

```bash
cd yolov5_ws
colcon build
source install/setup.bash
```

Launch the object detection node:

```bash
ros2 launch yolov5_ros2 yolov5_ros2_launch.py
```

## 4. Output Topic & Message Format

Detection results are published on the following topic:

```bash
/Vision_result_Team3
```

Message Overview (only key info):

```bash
frame_id: spot/body        # reference coordinate frame

class_id: ball             # detected object class

score: 0.8171692490577698  # detection confidence

position:                 # 3D position after TF transformation

  x: -1.1204
  
  y: -0.4977
  
  z: -0.5264
```

--------------------------------------------------------------------------------


## rosbag to yolo dataset

bag_to_yolo_images.py

input : rosbag topic 

output : dataset_raw 
