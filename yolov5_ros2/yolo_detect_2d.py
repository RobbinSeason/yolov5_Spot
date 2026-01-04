import numpy as np
import cv2
import yaml
import rclpy
import os
import tf2_ros
import rclpy.duration
from yolov5 import YOLOv5
from vision_msgs.msg import Detection3DArray, Detection3D
from vision_msgs.msg import ObjectHypothesisWithPose
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from tf2_geometry_msgs import do_transform_pose  # 或 import tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped, Quaternion
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import ParameterDescriptor
from sensor_msgs.msg import Image, CameraInfo




# Get the ROS distribution version and set the shared directory for YoloV5 configuration files.
ros_distribution = os.environ.get("ROS_DISTRO")
package_share_directory = get_package_share_directory('yolov5_ros2')

# Create a ROS 2 Node class YoloV5Ros2.
class YoloV5Ros2(Node):
    def __init__(self):
        super().__init__('yolov5_ros2')
        self.get_logger().info(f"Current ROS 2 distribution: {ros_distribution}")

        ##Declare parameters
        #Declare device parameters.
        self.declare_parameter("device", "cpu", ParameterDescriptor(
            name="device", description="Compute device selection, default: cpu, options: cuda:0"))
        
        #Declare model parameter
        self.declare_parameter("model", "best", ParameterDescriptor(
            name="model", description="Default model selection: best"))
        
        #Declare ros2 parameters
        #Declare image topic parameter
        self.declare_parameter("image_topic", "/image_raw", ParameterDescriptor(
            name="image_topic", description="Image topic, default: /image_raw"))
        
        #Declare depth topic parameter
        self.got_camera_info = False
        self.depth_image = None
        self.depth_logged = False
        self.declare_parameter("depth_topic", "/spot/depth/frontleft/image", ParameterDescriptor(
            name="depth_topic", description="Depth image topic, default: /spot/depth/frontleft/image"))
        
        #Declare camera info topic parameter
        self.declare_parameter("camera_info_topic", "/camera/camera_info", ParameterDescriptor(
            name="camera_info_topic", description="Camera information topic, default: /camera/camera_info"))

        #Read parameters from the camera_info topic if available, otherwise, use the file-defined parameters.
        self.declare_parameter("camera_info_file", f"{package_share_directory}/config/camera_info.yaml", ParameterDescriptor(
            name="camera_info", description=f"Camera information file path, default: {package_share_directory}/config/camera_info.yaml"))

        # #Declare tf2 buffer and listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)


        # Default to displaying detection results.
        self.declare_parameter("show_result", False, ParameterDescriptor(
            name="show_result", description="Whether to display detection results, default: False"))

        # Default to publishing detection result images.
        self.declare_parameter("pub_result_img", False, ParameterDescriptor(
            name="pub_result_img", description="Whether to publish detection result images, default: False"))

        ## Initialize components.
        # 1. Load the model.
        model_path = package_share_directory + "/config/" + self.get_parameter('model').value + ".pt"
        device = self.get_parameter('device').value
        self.get_logger().info(f"Using device: {device}")
        self.yolov5 = YOLOv5(model_path=model_path, device=device)

        # 2. Create publishers.
        self.yolo_result_pub = self.create_publisher(
            Detection3DArray, "Vision_result_Team3", 10)
        self.result_msg = Detection3DArray()

        self.result_img_pub = self.create_publisher(Image, "result_img", 10)

        # 3. Create an RGB/Depth/Camera_info subscriber
        image_topic = self.get_parameter('image_topic').value
        self.image_sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            qos_profile_sensor_data)  # 10=reliable os_profile_sensor_data=best effort

        depth_topic = self.get_parameter("depth_topic").value
        self.depth_sub = self.create_subscription(
            Image,
            depth_topic,
            self.depth_callback,
            qos_profile_sensor_data) # 10=reliable os_profile_sensor_data=best effort

        camera_info_topic = self.get_parameter('camera_info_topic').value
        self.camera_info_sub = self.create_subscription(
            CameraInfo, camera_info_topic, self.camera_info_callback, 1)

        # Get camera information.
        with open(self.get_parameter('camera_info_file').value) as f:
            self.camera_info = yaml.full_load(f.read())
            self.get_logger().info(f"default_camera_info: {self.camera_info['k']} \n {self.camera_info['d']}")

        # 4. Image format conversion (using cv_bridge).
        self.bridge = CvBridge()

        self.show_result = self.get_parameter('show_result').value
        self.pub_result_img = self.get_parameter('pub_result_img').value

        # Declare work offset distance parameter
        self.declare_parameter("work_offset_distance", 0.2, ParameterDescriptor(
            name="work_offset_distance",
            description="Safety offset along body→target line (meters)"))
        self.work_offset_distance = float(self.get_parameter('work_offset_distance').value)
        
        # Per-object buffer + publish-once controls
        self.instance_radius = 0.5   # meters, same-class instance separation radius
        self.buffer_size = 5         # keep last N samples per instance
        self.publish_score_thresh = 0.7 # minimum score to publish detection
        self.buffers = {}            # {(name): [clusters]}, cluster: {"pos": np.array, "samples": [...]}
        self.published_instances = set()  # {(name, instance_id)}


    ## Callback functions
    # Depth image callback
    def depth_callback(self, msg: Image):
        self.depth_image = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding="passthrough"
        )
        
        if not self.depth_logged:
            h, w = self.depth_image.shape[:2]
            self.get_logger().info(
                f"Depth sample value: {self.depth_image[h//2, w//2]}"
            )
            self.depth_logged = True
            
    # Camera_info callback
    def camera_info_callback(self, msg: CameraInfo):
        if self.got_camera_info:
           return
        self.got_camera_info = True

        self.camera_info['k'] = msg.k
        self.camera_info['p'] = msg.p
        self.camera_info['d'] = msg.d
        self.camera_info['r'] = msg.r
        self.camera_info['roi'] = msg.roi

    # Image callback
    def image_callback(self, msg: Image):
        # Detect and publish results.
        image = self.bridge.imgmsg_to_cv2(msg)
        detect_result = self.yolov5.predict(image)

        #Only for debug
        #self.get_logger().info(str(detect_result))

        self.result_msg.detections.clear()
        self.result_msg.header.frame_id = "spot/map"
        self.result_msg.header.stamp = self.get_clock().now().to_msg()

        # Parse the results.
        predictions = detect_result.pred[0]
        boxes = predictions[:, :4]  # x1, y1, x2, y2
        scores = predictions[:, 4]  # confidence scores
        categories = predictions[:, 5]

        for index in range(len(categories)):
            name = detect_result.names[int(categories[index])]

            detection3d = Detection3D()
            detection3d.id = name

            x1, y1, x2, y2 = boxes[index]
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            # Compute bbox center and size
            center_x = (x1+x2)/2.0
            center_y = (y1+y2)/2.0

            # 2D result visualization
            if self.show_result or self.pub_result_img:
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(image, (int(center_x), int(center_y)), 4, (0,0,255), -1) 
                cv2.putText(
                    image,
                    name,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1
                )

            ## convert 2D box center to 3D point
            # 如果还没收到深度图，跳过
            if self.depth_image is None:
                self.get_logger().warn("No depth image received yet")
                continue
            
            #将BBOX中心的像素坐标映射到深度图上
            # 将 bbox 中心映射到深度图
            rgb_h, rgb_w = image.shape[:2]                 # 480, 640
            depth_h, depth_w = self.depth_image.shape[:2]  # 240, 424
            depth_u = int(np.clip(center_x, 0, rgb_w - 1) * depth_w / rgb_w)
            depth_v = int(np.clip(center_y, 0, rgb_h - 1) * depth_h / rgb_h)
            depth_u = int(np.clip(depth_u, 0, depth_w - 1))
            depth_v = int(np.clip(depth_v, 0, depth_h - 1))

            # 取一个 5×5 ROI
            half = 2  # half=1→3x3，half=2→5x5
            x_min = max(0, depth_u - half)
            x_max = min(depth_w - 1, depth_u + half)
            y_min = max(0, depth_v - half)
            y_max = min(depth_h - 1, depth_v + half)
            roi = self.depth_image[y_min:y_max + 1, x_min:x_max + 1]

            # 过滤无效深度并取平均或中值
            valid = roi[roi > 0]
            if valid.size == 0:
                continue  # 没有有效深度就跳过
            depth_value = float(np.median(valid))
            # If uint16 → divide by 1000   #frontleft_depth 16UC1
            if self.depth_image.dtype == np.uint16:  
                depth_value /= 1000.0

            # 相机内参
            fx = self.camera_info["k"][0]
            fy = self.camera_info["k"][4]
            cx = self.camera_info["k"][2]
            cy = self.camera_info["k"][5]

            # 转化为3d坐标
            camera_x = (depth_u - cx) * depth_value / fx
            camera_y = (depth_v - cy) * depth_value / fy
            camera_z = depth_value

            ## transform to spot/map 
            # pack 3D pose in camera frame
            pose_cam = PoseStamped()
            pose_cam.header.stamp = msg.header.stamp  # or self.get_clock().now().to_msg() 时间戳
            pose_cam.header.frame_id = msg.header.frame_id 
            pose_cam.pose.position.x = camera_x
            pose_cam.pose.position.y = camera_y
            pose_cam.pose.position.z = camera_z

            # Compute orientation based on object type
            # pose_cam.pose.orientation = Quaternion(x=1.0, y=2.0, z=3.0, w=1.0)  # default: end-effector faces downward

            ##orientation can be added later
            #ball 
                #抓取点在球的顶部，orientation垂直向下
            #cube
                #保证抓取臂垂直边缘方向
            #bottle
                #if站立，抓取点在顶部，保证抓取臂垂直边缘方向
                #if躺下，抓取点在中间，保证抓取臂垂直于边缘方向
            # if name == "ball":
            #     pose_cam.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)  # end-effector faces downward
            # elif name == "cube":
            #     yaw = estimate_cube_yaw(x1, y1, x2, y2)  # 根据 bbox 判断朝向（需自定义函数）
            #     qx, qy, qz, qw = tf_transformations.quaternion_from_euler(math.pi, 0.0, yaw)
            #     pose_cam.pose.orientation.x = qx
            #     pose_cam.pose.orientation.y = qy
            #     pose_cam.pose.orientation.z = qz
            #     pose_cam.pose.orientation.w = qw
            # elif name == "bottle":
            #     if bbox_is_upright(x1, y1, x2, y2):
            #         pose_cam.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)  # 抓顶部，法向向下
            #     else:
            #         yaw = estimate_bottle_laying_angle(x1, y1, x2, y2)
            #         qx, qy, qz, qw = tf_transformations.quaternion_from_euler(0.0, math.pi/2, yaw)
            #         pose_cam.pose.orientation.x = qx
            #         pose_cam.pose.orientation.y = qy
            #         pose_cam.pose.orientation.z = qz
            #         pose_cam.pose.orientation.w = qw
            # else:
            #     pose_cam.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

            # Compute orientation based on object type
 

            # tf2 transform from camera to map
            try:
                pose_map = self.tf_buffer.transform(
                    pose_cam,
                    "spot/map",
                    timeout=rclpy.duration.Duration(seconds=0.2)
                )
            except Exception as e:
                self.get_logger().warn(f"TF transform failed: {e}")
                continue
            
            
            ##select best per-object instance and publish
            candidate_pos = np.array([
                pose_map.pose.position.x,
                pose_map.pose.position.y,
                pose_map.pose.position.z,
            ], dtype=float)

            #devide into different instances based on name
            clusters = self.buffers.setdefault(name, [])
            
            #devide into different instances based on distance
            matched_idx = None
            for idx, cluster in enumerate(clusters):
                dist = np.linalg.norm(candidate_pos - cluster["pos"]) if "pos" in cluster else float("inf")
                if dist < 2 * self.instance_radius:
                    matched_idx = idx
                    break
            if matched_idx is None:
                clusters.append({"pos": candidate_pos, "samples": []})
                matched_idx = len(clusters) - 1
            
            cluster = clusters[matched_idx]
            samples = cluster.get("samples", [])
            samples.append({"score": float(scores[index]), "pos": candidate_pos})
            samples = samples[-self.buffer_size:]
            cluster["samples"] = samples
            best = max(samples, key=lambda s: s["score"])
            cluster["pos"] = best["pos"]

            # apply offset along body→target line to keep tool away from object
            publish_pos = best["pos"].copy()
            norm = np.linalg.norm(publish_pos)
            if norm > 1e-6 and self.work_offset_distance > 0.0:
                publish_pos = publish_pos - self.work_offset_distance * (publish_pos / norm)
            
            instance_key = (name, matched_idx)
            should_publish = best["score"] >= self.publish_score_thresh and instance_key not in self.published_instances
            if not should_publish:
                continue

            #publish the best instance (offset along body→target line)
            #pos
            self.published_instances.add(instance_key)
            detection3d.bbox.center.position.x = publish_pos[0]
            detection3d.bbox.center.position.y = publish_pos[1]
            detection3d.bbox.center.position.z = publish_pos[2]
            
            #score and class_id
            detection3d.results.clear()
            hyp = ObjectHypothesisWithPose()
            hyp.hypothesis.class_id = name
            hyp.hypothesis.score = best["score"]  # 置信度
            detection3d.results.append(hyp)

            # detection3d.bbox.center.orientation = pose_body.pose.orientation

            self.result_msg.detections.append(detection3d)

        # Display results if needed.
        if self.show_result:
            cv2.imshow('result', image)
            cv2.waitKey(1)

        # Publish result images if needed.
        if self.pub_result_img:
            result_img_msg = self.bridge.cv2_to_imgmsg(image, encoding="bgr8")
            result_img_msg.header = msg.header
            self.result_img_pub.publish(result_img_msg)

        # Only publish when there is at least one detection appended
        if self.result_msg.detections:
            self.yolo_result_pub.publish(self.result_msg)

def main():
    rclpy.init()
    rclpy.spin(YoloV5Ros2())
    rclpy.shutdown()

if __name__ == "__main__":
    main()
