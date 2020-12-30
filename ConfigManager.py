import json
import os

class ConfigManager:
    def __init__(self, scriptDir, configFileName):
        self.scriptDir = scriptDir
        self.configFileName = configFileName
        self.configFile = os.path.join(scriptDir, configFileName)
        #print(self.configFile)

    def SaveDefaultConfig(self):
        data = {
            "updated": False,
            "version": "v0.0",
            "cams": [
                {
                    "name": "Demo Cam",
                    "url": "rtsp://192.168.4.1/live",
                    "fps": 30,
                }
            ]
        }

        with open(self.configFile, 'w') as file:
            file.write(json.dumps(data, indent=4))

    def LoadConfig(self):
        try:
            with open(self.configFile, 'r') as configFile:
                config = json.loads(configFile.read())
                #print(config)

                return config

        except FileNotFoundError:
            print("Config not found. Creating now... ", end="")
            self.SaveDefaultConfig()
            return None
        except Exception as e:
            print("Error reading config:")
            print(e)
            return None

    def SaveConfig(self, data):
        with open(self.configFile, 'w') as configFile:
            configFile.write(json.dumps(data, indent=4))

    def SetValue(self, key, value):
        config = self.LoadConfig()
        config[key] = value
        self.SaveConfig(config)
