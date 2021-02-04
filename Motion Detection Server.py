from cv2 import cv2
import numpy as np
import time
import threading
import queue
import collections
import sys
import os
import json
from Log import Log
import ConfigManager as config
import EmailManager as email
import Webserver as web
import VideoManager as video

CONFIG_FILE_NAME = "config.json"
scriptDir = os.path.dirname(sys.argv[0])

#cam = VideoDevice("PiCam", "rtsp://192.168.4.23:8554/unicast", 10, 1.5)
#cam = VideoDevice("6 Cam", "rtsp://admin:chris!@192.168.4.38:8554/live", 30, 1.5)
email.Init()

def HandleMenu():
    options = ["Exit"]
    for i, val in enumerate(options):
        print(str(i+1) + ". " + val)

    cmd = int(input(">"))
    return options[cmd-1]


def main():
    video.InitCams()
    web.Run()

    Log("Server stopped")
    video.Stop()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

