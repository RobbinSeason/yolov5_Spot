import os
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


class MultiCameraBagExporter(Node):
    """
    Subscribe to multiple image topics and dump frames to disk for dataset prep.
    """

    def __init__(self):
        super().__init__("multi_camera_bag_exporter")

        self.bridge = CvBridge()

        # Topic list: add/remove as needed.
        self.camera_topics = {
            "frontleft": "/spot/camera/frontleft/image",
            "frontright": "/spot/camera/frontright/image",
            "left": "/spot/camera/left/image",
            "right": "/spot/camera/right/image",
            "back": "/spot/camera/back/image",
        }

        # Base output directory.
        self.base_dir = "dataset_raw"
        os.makedirs(self.base_dir, exist_ok=True)

        # Use best effort to match bag QoS; adjust if your bag is reliable.
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        for cam, topic in self.camera_topics.items():
            out_dir = os.path.join(self.base_dir, cam, "images")
            os.makedirs(out_dir, exist_ok=True)

            # Bind cam into the callback using default arg.
            self.create_subscription(
                Image,
                topic,
                lambda msg, cam=cam: self.image_callback(msg, cam),
                qos,
            )

        self.get_logger().info(f"Multi-camera bag exporter ready. Saving to {self.base_dir}")

    def image_callback(self, msg: Image, cam_name: str):
        # Use ROS stamp to build a filename; add counter fallback if needed.
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        filename = f"{stamp:.3f}.jpg"

        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        save_path = os.path.join(self.base_dir, cam_name, "images", filename)
        cv2.imwrite(save_path, img)


def main():
    rclpy.init()
    node = MultiCameraBagExporter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

