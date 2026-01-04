[中文文档](./README.md) | [English Document](./README_EN.md)

# YOLO_ROS2

基于YOLOV5 的ROS2封装，允许用户使用给定的模型文件和相机参数进行三维空间物体检测和抓取操作。

![YOLO_ROS2](https://img-blog.csdnimg.cn/592a90f1441f4a3ab4b94891878fbc55.png)

## 1. 安装依赖

首先，确保您已经更新了系统并且安装了必要的依赖。以下是一些安装步骤，其中`$ROS_DISTRO` 是您的ROS2发行版（例如：`foxy`、`galactic`）：

```bash
sudo apt update
sudo apt install python3-pip ros-$ROS_DISTRO-vision-msgs
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple yolov5  
```

## 2. 下载编译和运行

下载开源库

```bash
mkdir -p yolov5_ws/src
cd yolov5_ws/src
git clone https://github.com/fishros/yolov5_ros2.git
```

编译项目并设置环境变量

```bash
cd yolov5_ws
colcon build
source install/setup.bash
```

现在，您可以运行Yolo_ROS2节点。默认情况下，它将使用CPU来进行检测，使用名为`/image`的图像话题。您可以根据需要更改这些参数：

```bash
ros2 run yolov5_ros2 yolo_detect_2d --ros-args -p device:=cpu -p image_topic:=/image
```

如果您要使用真实相机，请修改默认的图像话题（`image_topic:=/image`），然后在另一个终端中运行以下命令来将相机图像转化为ROS话题：

```bash
ros2 run image_tools cam2image --ros-args -p width:=640 -p height:=480 -p frequency:=30.0 -p device_id:=-1
```

您也可以使用其他相机，例如`usb_cam`。在这种情况下，安装相应的包并运行`usb_cam`节点：

```bash
sudo apt-get install ros-<ros2-distro>-usb-cam # 安装
ros2 run usb_cam usb_cam_node_exe
```

![Yolo_ROS2相机](https://img-blog.csdnimg.cn/c65bed0b67694ed69776151c203bb950.png)

## 3. 订阅结果

Yolo_ROS2将检测结果发布到`/yolo_result`话题中，包括原始像素坐标以及归一化后的相机坐标系下的x和y坐标。您可以使用以下命令查看检测结果：

```bash
ros2 topic echo /yolo_result
```

![Yolo_ROS2检测结果](https://img-blog.csdnimg.cn/ac963f4226bf497790c0ef2fd8d942a3.png)

## 4. 更进一步使用

### 4.1 参数设置

在运行Yolo_ROS2节点时，您可以使用 `-p name:=value` 的方式来修改参数值。

#### 4.1.1 图像话题

您可以通过指定以下参数来更改图像话题：

```bash
image_topic:=/image
```

#### 4.1.2 计算设备设置

如果您有CUDA支持的显卡，可以选择以下参数来配置计算设备：

```bash
device:=cpu
```

#### 4.1.3 是否实时显示结果

您可以使用以下参数来控制是否实时显示检测结果。设置为`True`将实时显示结果，设置为`False`则不会显示：

```bash
show_result:=False
```

请注意，实时显示中的`cv2.imshow`可能会卡住。如果只需要验证结果，可以将此参数设置为`False`。

#### 4.1.4 切换不同Yolov5模型

默认情况下，Yolo_ROS2使用`yolov5s`模型。您可以通过以下参数来更改模型：

```bash
model:=yolov5m
```

#### 4.1.5 是否发布结果图像

如果您希望Yolo_ROS2发布检测结果的图像，请使用以下参数：

```bash
pub_result_img:=True
```

这将允许您通过`/result_img`话题查看检测结果的图像。

#### 4.1.5 相机参数文件

功能包默认从 /camera/camera_info 话题获取相机参数，在获取成功前，相机参数文件路径可以通过参数进行设置，参数为：camera_info_file，通过该参数可以设置文件路径，注意需要使用绝对目录：

```bash
camera_info_file:=/home/fishros/chapt9/src/yolov5_ros2/config/camera_info.yaml
```





------------------------------------------------------

## self readme start #
## object detection part

## 0. 安装依赖

首先，确保您已经更新了系统并且安装了必要的依赖。以下是一些安装步骤，其中`$ROS_DISTRO` 是您的ROS2发行版（例如：`foxy`、`galactic`）：

```bash
sudo apt update
sudo apt install python3-pip ros-$ROS_DISTRO-vision-msgs
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple yolov5  
```

## 0.1. 下载open_source library (only for first time to build)

下载开源库

```bash
mkdir -p yolov5_ws/src
cd yolov5_ws/src
git clone https://github.com/fishros/yolov5_ros2.git
```

## 1. ducument configuration
 best.pt :  need to be put under the document of config

## 2. adjust the parameter and select the camera
yolov5_ros2_launch.py 
# first node 
some parameters
# others
topic about camera

## 3. colcon build and lauch

编译项目并设置环境变量

```bash
cd yolov5_ws
colcon build
source install/setup.bash

ros2 launch yolov5_ros2 yolov5_ros2_launch.py
```

## 4.result
the result will be shown by topic : /Vision_result_Team3

basic introduction about the msg:  (only list the key-info)
---
frame_id: spot/body       # name of coorderate base
class_id: ball            # class
score: 0.8171692490577698 # the confidence of the bbox
position:                 # coorderate after tf
  x: -1.1204196044181618
  y: -0.49767466398206756
  z: -0.5263708318374491

# self start #
*1 制作训练集
'image_topic': '/spot/camera/frontleft/image'


##### ------------------------------------------- #####
## 0.2. 测试
## 0.2.1. 发布图像
如果您要使用真实相机，请修改默认的图像话题（`image_topic:=/image`），然后在另一个终端中运行以下命令来将相机图像转化为ROS话题：

```bash
ros2 run image_tools cam2image --ros-args -p width:=640 -p height:=480 -p frequency:=30.0 -p device_id:=-1
```

您也可以使用其他相机，例如`usb_cam`。在这种情况下，安装相应的包并运行`usb_cam`节点：

```bash
sudo apt-get install ros-<ros2-distro>-usb-cam # 安装
ros2 run usb_cam usb_cam_node_exe
```

![Yolo_ROS2相机](https://img-blog.csdnimg.cn/c65bed0b67694ed69776151c203bb950.png)

现在，您可以运行Yolo_ROS2节点。默认情况下，它将使用CPU来进行检测，使用名为`/image`的图像话题。您可以根据需要更改这些参数：

## 0.2.2. 运行yolo节点
现在，您可以运行Yolo_ROS2节点。默认情况下，它将使用CPU来进行检测，使用名为`/image`的图像话题。您可以根据需要更改这些参数：
```bash
ros2 run yolov5_ros2 yolo_detect_2d --ros-args -p device:=cpu -p image_topic:=/image
```

## 0.2.3. 订阅结果
Yolo_ROS2将检测结果发布到`/yolo_result`话题中，包括原始像素坐标以及归一化后的相机坐标系下的x和y坐标。您可以使用以下命令查看检测结果：

```bash
ros2 topic echo /yolo_result
```
此外可通过 rviz2工具查看结果 


## 1. 制作数据集 （这里我切换到windows系统下完成了 因为后续训练model要用GPU我只能在windows系统里训练 数据集不用来回导了）
## 1.1. 原始视频 
录制rosbag
rosbag输出视频

  # 1) 播放 bag（若有多个话题需要同步，就同时 play）
  ros2 bag play your.bag

  # 2) 录制目标图像话题为视频
  ros2 run image_view video_recorder --ros-args -r image:=/spot/camera/frontleft/image
  # 默认输出 out.avi，想换文件名或帧率可用 __params 配置




## 1.2. 打标
安装并启动 CVAT（Docker）
```bash
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release -y
sudo mkdir -m 0755 -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

---

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

---

cd ~
git clone https://github.com/opencv/cvat.git
cd cvat

---

sudo docker compose up -d

---
```
浏览器访问并登录：
```bash
http://localhost:8080
```
## 1.3.创建 CVAT 标注任务

进入 Tasks

创建新任务（New Task）

设置标签：

bottle
ball
cube


上传图片目录 ~/SpotDataset/images/

## 1.4. 使用 CVAT 自动追踪 + 手动修正
## 1.5. 导出 YOLO 格式数据集
YOLO 1.1 
下载.zip
Use default settings → 可以保持关闭（OFF）
## 1.6. 整理为 YOLOv5 标准格式  （这里还是问GPT大致思路）

编写脚本

运行脚本
python3 split_dataset.py

## 2. 训练model
## 2.1. 首先还是搭建环境
搭环境依照深度学习tip那个文件来 然后源码要download下来 
## 2.2. 创建一个 yolov5 的 YAML 文件（比如 spot_objects.yaml）
train: ./dataset1/images/train
val: ./dataset1/images/val
test: ./dataset1/images/test

nc: 3
names: ["bottle", "ball", "cube"]
## 2.3. 训练
python train.py --img 640 --batch 16 --epochs 50 --data ../datasets/dataset1/data.yaml --weights yolov5s.pt
## 2.4. test
yolov5-master/runs/train/exp3/weights/best.pt
## 2.5. 导出模型
best.pt
last.pt

## 4. 应用新模型进行目标检测
## 4.1. 导入模型
具体就参照当前的文件目录格式 看best的位置
## 4.2. 编写lyolo_detect_launch  （启动文件）
## 4.3  编写setup.py
## 4.4  改yolo_detect_2d  （功能文件 后面要增减功能都来这里改）
## 4.5 编译
cd ~/yolov5_ws
colcon build --symlink-install
source install/setup.bash

## 4.6 发布话题
ros2 launch yolov5_ros2 yolov5_ros2_launch.py device:=cpu

## （待完成）5. 按照测试环节重新来一次 验证一下模型效果
1.输入话题根据spot话题来改  yolov5_ros2_launch
  image_topic → Spot RGB 话题

  depth_topic → Spot depth 话题



2.相机内参也要根据spot实际情况来改  camera_info.yaml 
    camera_info_topic → Spot camera_info
3.verify Spot depth unit (meters or millimeters)
4.看一下坐标关系 然后理顺逻辑
  ros2 run tf2_tools view_frames

  （可视化仍显示 camera 坐标（不影响功能））
   cv2.putText(image, f"{name}({camera_x:.2f},{camera_y:.2f})", ...)


5.实际做的时候关一下这个 self.get_logger().info(str(detect_result))


具体转换和功能 增减话题订阅和发布 要到 yolo_detect_2d 这里来实现

## test
ros2 topic list | grep yolo  #看话题列表里有没有/yolo_result
ros2 topic info /yolo_result  #看看类型是不是这个 Type: vision_msgs/msg/Detection2DArray
ros2 topic echo /yolo_result  #看内容  frame_id = vision   x / y / z 在变化


