from cv2 import cv2
import numpy as np
import time
import threading
import queue
import collections
import sys
import os
from VideoDevice import VideoCapture, VideoDevice


cam = VideoDevice("PiCam", "rtsp://192.168.4.23:8554/unicast", 10, 1.5)
#cam = VideoDevice("6 Cam", "rtsp://admin:chris!@192.168.4.38:8554/live", 30)
#cam = VideoDevice("4 Cam", "rtsp://192.168.4.71", 30)



def main():
    while True:
        cam.GetFrame()
        time.sleep(0.5)



if __name__ == "__main__":
    main()


