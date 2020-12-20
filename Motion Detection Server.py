from cv2 import cv2
import numpy as np
import time
import threading
import queue
import collections
import sys
import os
from VideoDevice import VideoCapture, VideoDevice
import json

CONFIG_FILE_NAME = "motion config.json"
scriptDir = os.path.dirname(sys.argv[0])

#cam = VideoDevice("PiCam", "rtsp://192.168.4.23:8554/unicast", 10, 1.5)
#cam = VideoDevice("6 Cam", "rtsp://admin:chris!@192.168.4.38:8554/live", 30, 1.5)

def LoadConfig():
    try:
        with open(os.path.join(scriptDir, CONFIG_FILE_NAME), 'r') as configFile:
            print("Loading config...")
            config = json.loads(configFile.read())
            print(config)

            return config


    except FileNotFoundError:
        print("Config not found. Creating now... ", end="")
        data = {
            "cams": [
                {
                    "name": "Demo Cam",
                    "url": "rtsp://192.168.4.1/live",
                    "fps": 30
                }
            ]
        }

        with open(os.path.join(scriptDir, CONFIG_FILE_NAME), 'w') as file:
            file.write(json.dumps(data, indent=4))

        print("Done")
        return None
    except:
        print("Error reading config")
        return None

def InitCams(config):
    cams = []
    
    for cam in config["cams"]:
        try:
            cams.append(VideoDevice(cam["name"], cam["url"], cam["fps"], 1.5))
        except KeyError as e:
            print("================================================================")
            print("Error reading config value:")
            print(cam)
            print("Error reading key:", e)
            print("================================================================")
        

    return cams


def main():
    config = LoadConfig()
    if not config:
        return

    cams = InitCams(config)
    if len(cams) == 0:
        return

    while True:
        for cam in cams:
            cam.Update()



if __name__ == "__main__":
    main()


