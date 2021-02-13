import json
import os
import sys
import shutil
from functools import reduce
import operator

from Log import Log

self = sys.modules[__name__]
self.scriptDir = ""
self.configFileName = ""
self.configFile = ""
self.config = {}
self.name = "ConfigManager"

def SaveDefaultConfig():
    data = {
            "version": "v0.0",
            "saveVideoLength": 5,
            "refreshComparisonRate": 10,
            "cameraRestartTime": 10,
            "secondsBefore": 1,
            "outputDir": "./Captures/",
            "motionEnabled": True,
            "missedFrameLimit": 60,
            "previewTimer": 5,
            "email": {
                "sender_email": "email@gmail.com",
                "password": "pass",
                "receiver_email": "1234567890@mms.att.net",
                "port": 465,
                "smtp_server": "smtp.gmail.com"
            },
            "webserver": {
                "port": 8090
            },
            "cams": [
                {
                    "name": "Test_Cam",
                    "url": "rtsp://10.0.0.12"
                }
            ]
        }

    with open(self.configFile, 'w') as file:
        file.write(json.dumps(data, indent=4))

def LoadConfig():
    Log("Loading config", self)
    try:
        with open(self.configFile, 'r') as configFile:
            config = json.loads(configFile.read())
            print(config)
            self.config = config
            return config

    except FileNotFoundError:
        Log("Config not found. Creating now... ", self)
        self.SaveDefaultConfig()
        return LoadConfig()
    except Exception as e:
        Log("Error reading config:", self)
        print(e)
        return None

def RestoreConfig():
    Log("Restoring config")
    if os.path.exists("config.json.back"):
        os.remove("config.json.back")

    shutil.copyfile(self.configFile, "config.json.back")
    SaveDefaultConfig()
    
    LoadConfig()


def SaveConfig(data):
    with open(self.configFile, 'w') as configFile:
        configFile.write(json.dumps(data, indent=4))
    LoadConfig()

def GetValue(*keys):
    try:
        return reduce(operator.getitem, keys, self.config)
    except:
        Log("Key not found: " + str(keys), self, messageType="ERROR")
        return None

def SetValue(value, *keys):
    GetValue(*keys[:-1])[keys[-1]] = value

def AsString():
    return json.dumps(self.config)

def GetScriptDir():
    return self.scriptDir

def Init(scriptDir, configFileName):
    self.scriptDir = scriptDir
    self.configFileName = configFileName
    self.configFile = os.path.join(scriptDir, configFileName)
    self.config = {}
    LoadConfig()
    Log("Config loaded!", self)
    #print(self.configFile)


CONFIG_FILE_NAME = "config.json"
scriptDir = os.path.dirname(sys.argv[0])

Init(scriptDir, CONFIG_FILE_NAME)