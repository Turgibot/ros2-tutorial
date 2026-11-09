#!/usr/bin/env python3
"""Find a block in the overhead camera image by its colour and turn the pixel into table coordinates:
pixel_to_table.py LETTER      (A red, B blue, C green, D yellow)

The camera is at (0.65, 0, 1.3) looking straight down (see worlds/lab.sdf); the top of a block is at z = 0.35."""
import sys
import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image

CAM_X, CAM_Y, CAM_Z = 0.65, 0.0, 1.3
BLOCK_TOP_Z = 0.35
# hue ranges (OpenCV: 0..179) of the four block colours
HUE = {"A": [(0, 8), (172, 179)], "B": [(100, 125)], "C": [(50, 80)], "D": [(20, 35)]}


def main():
    letter = sys.argv[1]
    rclpy.init()
    node = Node("pixel_to_table")
    box = {}
    node.create_subscription(CameraInfo, "/overhead_camera/camera_info", lambda m: box.setdefault("info", m), 1)
    node.create_subscription(Image, "/overhead_camera/image", lambda m: box.setdefault("img", m), 1)
    while rclpy.ok() and len(box) < 2:
        rclpy.spin_once(node, timeout_sec=0.5)

    fx, fy, cx, cy = box["info"].k[0], box["info"].k[4], box["info"].k[2], box["info"].k[5]
    bgr = CvBridge().imgmsg_to_cv2(box["img"], "bgr8")
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = np.zeros(hsv.shape[:2], bool)
    for lo, hi in HUE[letter]:
        mask |= (hsv[:, :, 0] >= lo) & (hsv[:, :, 0] <= hi) & (hsv[:, :, 1] > 100) & (hsv[:, :, 2] > 60)
    v, u = np.nonzero(mask)
    u, v = u.mean(), v.mean()                      # centre of the coloured pixels
    d = CAM_Z - BLOCK_TOP_Z                        # distance from the camera to the top of the block
    x = CAM_X + (cy - v) / fy * d                  # image up is +x
    y = CAM_Y + (cx - u) / fx * d                  # image left is +y
    print(f"fx = {fx:.1f}  fy = {fy:.1f}  cx = {cx:.1f}  cy = {cy:.1f}")
    print(f"block {letter}: {mask.sum()} pixels, centre at pixel u = {u:.1f}, v = {v:.1f}")
    print(f"        table position x = {x:.3f} m, y = {y:.3f} m")


if __name__ == "__main__":
    main()
