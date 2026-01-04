from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.actions import SetParameter


def generate_launch_description():
    return LaunchDescription([

        #Only use sim time for simulation
        SetParameter(name='use_sim_time', value=False),

        #parameters need to be adjusted
        Node(
            
            package="yolov5_ros2",
            executable="yolo_detect_2d",
            name="yolov5_ros2",
            output="screen",
            parameters=[{
                "instance_radius": 0.5, #the radius of the instance
                "buffer_size": 5, #number of frames to average the detection results
                "publish_score_thresh": 0.7, #confidence threshold for publishing detection results
                "work_offset_distance": 0.25, #the distance from the robot to the working area
            }],
        ),

        # 以下是spot的五个摄像头节点配置
        Node(
            package='yolov5_ros2',
            executable='yolo_detect_2d',    # 这个必须和 setup.py 的 entry_points 一致
            name='yolov5_ros2_node_frontleft',
            output='screen',
            parameters=[{
                'device': 'cpu',             # 可以改成 'cuda:0'
                'model': 'best', 
                'image_topic': '/spot/camera/frontleft/image',     #改成spot对应的节点
                'depth_topic': '/spot/depth/frontleft/image',
                'camera_info_topic': '/spot/depth/frontleft/camera_info',  #改成spot深度相机内参

                'show_result': False,  #连接spot时候可以关掉
                'pub_result_img': True,
            }],
        ),

        Node(
            package='yolov5_ros2',
            executable='yolo_detect_2d',
            name='yolov5_ros2_node_frontright',
            output='screen',
            parameters=[{
                'device': 'cpu',             # 可以改成 'cuda:0'
                'model': 'best', 
                'image_topic': '/spot/camera/frontright/image',     #改成spot对应的节点
                'depth_topic': '/spot/depth/frontright/image',
                'camera_info_topic': '/spot/depth/frontright/camera_info',  #改成spot深度相机内参

                'show_result': False,  #连接spot时候可以关掉
                'pub_result_img': False,
            }],
        ),

        Node(
            package='yolov5_ros2',
            executable='yolo_detect_2d',
            name='yolov5_ros2_node_left',
            output='screen',
            parameters=[{
                'device': 'cpu',             # 可以改成 'cuda:0'
                'model': 'best', 
                'image_topic': '/spot/camera/left/image',     #改成spot对应的节点
                'depth_topic': '/spot/depth/left/image',
                'camera_info_topic': '/spot/depth/left/camera_info',  #改成spot深度相机内参

                'show_result': False,  #连接spot时候可以关掉
                'pub_result_img': False,
            }],
        ),

        Node(
            package='yolov5_ros2',
            executable='yolo_detect_2d',
            name='yolov5_ros2_node_right',
            output='screen',
            parameters=[{
                'device': 'cpu',             # 可以改成 'cuda:0'
                'model': 'best', 
                'image_topic': '/spot/camera/right/image',     #改成spot对应的节点
                'depth_topic': '/spot/depth/right/image',
                'camera_info_topic': '/spot/depth/right/camera_info',  #改成spot深度相机内参

                'show_result': False,  #连接spot时候可以关掉
                'pub_result_img': False,
            }],
        ),

        Node(
            package='yolov5_ros2',
            executable='yolo_detect_2d',
            name='yolov5_ros2_node_back',
            output='screen',
            parameters=[{
                'device': 'cpu',             # 可以改成 'cuda:0'
                'model': 'best', 
                'image_topic': '/spot/camera/back/image',     #改成spot对应的节点
                'depth_topic': '/spot/depth/back/image',
                'camera_info_topic': '/spot/depth/back/camera_info',  #改成spot深度相机内参

                'show_result': False,  #连接spot时候可以关掉
                'pub_result_img': False,
            }],
        ),
    ])







