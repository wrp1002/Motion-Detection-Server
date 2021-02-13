from datetime import datetime

def Log(message, obj=None, messageType="INFO"):
    message = str(message)
    message = message.capitalize()
    time = str(datetime.now())
    message = ("[" + messageType + "] ") + ("[" + time + "] ") + ("[" + obj.name + "] " if obj else " ") + message
    print(message)
