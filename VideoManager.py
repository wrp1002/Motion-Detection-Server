from VideoDevice import VideoDevice
from Log import Log
import ConfigManager as config
import sys

self = sys.modules[__name__]
self.cams = []

def Init():
    Log("Initializing Video Device Manager...")
    self.cams = []


def InitCams():
    self.cams = []

    for cam in config.GetValue("cams"):
        try:
            c = VideoDevice(cam["name"], cam["url"], 1.5)
            if c.dead:
                Log("Error initializing device", c, "ERROR")
            else:
                self.cams.append(c)

        except KeyError as e:
            print("================================================================")
            print("Error reading config value:")
            print(cam)
            print("Error reading key:", e)
            print("================================================================")

def Stop():
    Log("Shutting down...")
    for c in self.cams:
        Log("Stopping", c)
        c.Stop()


def Restart():
    Stop()
    InitCams()
