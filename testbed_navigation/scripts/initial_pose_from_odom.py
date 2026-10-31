#!/usr/bin/env python3
"""Publish /initialpose from the robot's current /odom pose.

In this simulation the diff-drive plugin reports odometry in the Gazebo world
frame and the map is aligned with the world, so the odom pose is also the
robot's pose in the map frame. This lets AMCL start correctly wherever the
robot happens to be.
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped


class InitialPoseFromOdom(Node):
    def __init__(self):
        super().__init__('initial_pose_from_odom')
        self.declare_parameter('settle_ticks', 3)
        self.declare_parameter('publish_count', 5)
        self.settle = self.get_parameter('settle_ticks').value
        self.remaining = self.get_parameter('publish_count').value
        self.odom = None
        self.pub = self.create_publisher(PoseWithCovarianceStamped, 'initialpose', 10)
        self.create_subscription(Odometry, 'odom', self.on_odom, 10)
        self.create_timer(1.0, self.tick)

    def on_odom(self, msg):
        self.odom = msg

    def tick(self):
        if self.remaining <= 0 or self.odom is None:
            return
        if self.pub.get_subscription_count() == 0:
            return  # AMCL is not up yet
        if self.settle > 0:
            self.settle -= 1  # give AMCL a moment to activate
            return
        msg = PoseWithCovarianceStamped()
        msg.header.stamp = self.odom.header.stamp
        msg.header.frame_id = 'map'
        msg.pose.pose = self.odom.pose.pose
        msg.pose.covariance[0] = 0.02
        msg.pose.covariance[7] = 0.02
        msg.pose.covariance[35] = 0.02
        self.pub.publish(msg)
        self.remaining -= 1
        p = msg.pose.pose.position
        self.get_logger().info(
            f'Published initial pose from odom: x={p.x:.2f} y={p.y:.2f}')


def main():
    rclpy.init()
    node = InitialPoseFromOdom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()