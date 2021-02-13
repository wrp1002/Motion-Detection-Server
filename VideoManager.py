from VideoDevice import VideoDevice
from Log import Log
import ConfigManager as config
import sys
import os

self = sys.modules[__name__]
self.cams = []
self.nextCamID = 0
self.name = "VideoManager"

def Init():
    Log("Initializing Video Device Manager...", self)
    self.cams = []
    self.nextCamID = 0


def InitCams():
    self.cams = []
    self.nextCamID = 0

    for cam in config.GetValue("cams"):
        try:
            c = VideoDevice(cam["name"], cam["url"], 1.5, self.nextCamID)
            self.cams.append(c)
            self.nextCamID += 1

        except KeyError as e:
            print("================================================================")
            print("Error reading config value:")
            print(cam)
            print("Error reading key:", e)
            print("================================================================")

    Log("Cameras loaded", self)

def Cleanup():
    Log("Cleaning preview directory...", self)
    for file in os.listdir(os.path.join(config.scriptDir, "web/static/previews/")):
        os.remove(os.path.join(config.scriptDir, "web/static/previews/", file))
    Log("Done", self)

def Stop():
    Log("Shutting down...")
    for c in self.cams:
        Log("Stopping", c)
        c.Stop()
    Cleanup()

def Restart():
    Stop()
    InitCams()

def GetCamInfo():
    camInfo = []
    for cam in self.cams:
        info = {
            "name": cam.name,
            "id": cam.ID,
            "connected": cam.IsConnected(),
        }
        camInfo.append(info)

    return camInfo