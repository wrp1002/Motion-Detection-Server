from datetime import datetime

def Log(message, cam=None, messageType="INFO"):
    message = str(message)
    message = message.capitalize()
    time = str(datetime.now())
    message = ("[" + messageType + "] ") + ("[" + time + "] ") + ("[" + cam.name + "] " if cam else " ") + message
    print(message)