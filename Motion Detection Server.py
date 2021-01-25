from cv2 import cv2
import numpy as np
import time
import threading
import queue
import collections
import sys
import os
from VideoDevice import VideoDevice
import json
from Log import Log
import ConfigManager as config
import EmailManager as email
import Webserver as web

CONFIG_FILE_NAME = "config.json"
scriptDir = os.path.dirname(sys.argv[0])

#cam = VideoDevice("PiCam", "rtsp://192.168.4.23:8554/unicast", 10, 1.5)
#cam = VideoDevice("6 Cam", "rtsp://admin:chris!@192.168.4.38:8554/live", 30, 1.5)
config.Init(scriptDir, CONFIG_FILE_NAME)
email.Init()

def InitCams():
    cams = []

    for cam in config.GetValue("cams"):
        try:
            c = VideoDevice(cam["name"], cam["url"], 1.5)
            if c.dead:
                Log("Error initializing device", c, "ERROR")
            else:
                cams.append(c)

        except KeyError as e:
            print("================================================================")
            print("Error reading config value:")
            print(cam)
            print("Error reading key:", e)
            print("================================================================")

    if any(c.dead for c in cams):
        return None

    return cams

def HandleMenu():
    options = ["Exit"]
    for i, val in enumerate(options):
        print(str(i+1) + ". " + val)

    cmd = int(input(">"))
    return options[cmd-1]


def main():
    cams = InitCams()
    if not cams:
        return

    camThreads = []
    Log("Starting camera update threads")
    for cam in cams:
        camThreads.append(threading.Thread(target=cam.Update))
    for t in camThreads:
        t.start()

    web.Run()

    while True:
        cmd = HandleMenu()
        if cmd == "Exit":
            break

    Log("Shutting down...")
    for c in cams:
        Log("Stopping", c)
        c.Stop()
    for c in cams:
        Log("Releasing", c)
        c.cap.cap.release()

    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()


