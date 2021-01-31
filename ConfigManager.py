import json
import os
import sys
import shutil

from Log import Log

self = sys.modules[__name__]
self.scriptDir = ""
self.configFileName = ""
self.configFile = ""
self.config = {}

def SaveDefaultConfig():
    data = {
            "version": "v0.0",
            "saveVideoLength": 5,
            "refreshComparisonRate": 10,
            "secondsBefore": 1,
            "outputDir": "./Captures/",
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
    print("Loading")
    try:
        with open(self.configFile, 'r') as configFile:
            config = json.loads(configFile.read())
            print(config)
            self.config = config
            return config

    except FileNotFoundError:
        print("Config not found. Creating now... ", end="")
        self.SaveDefaultConfig()
        return LoadConfig()
    except Exception as e:
        print("Error reading config:")
        print(e)
        return None

def RestoreConfig():
    print("Restoring")
    if os.path.exists("config.json.back"):
        os.remove("config.json.back")

    shutil.copyfile(self.configFile, "config.json.back")
    SaveDefaultConfig()
    
    LoadConfig()


def SaveConfig(data):
    with open(self.configFile, 'w') as configFile:
        configFile.write(json.dumps(data, indent=4))
    LoadConfig()

def SetValue(key, value):
    config = self.LoadConfig()
    config[key] = value
    self.SaveConfig(config)

def GetValue(key):
    try:
        value = self.config[key]
    except KeyError:
        Log("Key not found: " + key, messageType="ERROR")
        return None
    except Exception as e:
        Log("Error with config key: " + e, messageType="ERROR")
        return None

    return value

def _GetValueR(data, *args):
    if args and data:
        element  = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else _GetValueR(value, *args[1:])

def GetValueR(*args):
    return _GetValueR(self.config, *args)

def AsString():
    return json.dumps(self.config)

def Init(scriptDir, configFileName):
    self.scriptDir = scriptDir
    self.configFileName = configFileName
    self.configFile = os.path.join(scriptDir, configFileName)
    self.config = {}
    LoadConfig()
    Log("Config loaded!")
    #print(self.configFile)


CONFIG_FILE_NAME = "config.json"
scriptDir = os.path.dirname(sys.argv[0])

Init(scriptDir, CONFIG_FILE_NAME)