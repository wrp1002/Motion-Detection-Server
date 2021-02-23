from cv2 import cv2
import threading
import queue, collections
import sys, os, time
from Log import Log

import ConfigManager as config
import EmailManager as email
import Webserver as web
import VideoManager as video
import Updater as updater


CONFIG_FILE_NAME = "config.json"
scriptDir = os.path.dirname(sys.argv[0])

#cam = VideoDevice("PiCam", "rtsp://192.168.4.23:8554/unicast", 10, 1.5)
#cam = VideoDevice("6 Cam", "rtsp://admin:chris!@192.168.4.38:8554/live", 30, 1.5)

def HandleMenu():
    options = ["Exit"]
    for i, val in enumerate(options):
        print(str(i+1) + ". " + val)

    cmd = int(input(">"))
    return options[cmd-1]

def RestartServer():
    os.execv(sys.executable, [sys.executable] + sys.argv)

def main():
    config.LoadConfig()
    email.Init()
    video.InitCams()

    web.Run()
    shutdownState = web.GetShutdownState()

    Log("Server Shutting Down...")
    video.Stop()
    cv2.destroyAllWindows()

    if shutdownState == "restart":
        RestartServer()
    elif shutdownState == "update":
        Log("Updating server...")
        updater.Update()
        RestartServer()


if __name__ == "__main__":
    main()

