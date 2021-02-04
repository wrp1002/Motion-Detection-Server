import ConfigManager as config
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from Log import Log
import sys
import os

CONFIG_FILE_NAME = "config.json"
scriptDir = os.path.dirname(sys.argv[0])

self = sys.modules[__name__]
self.port = ""
self.smtp_server = ""
self.sender_email = ""
self.receiver_email = ""
self.password = ""

def SendMessage(message):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.receiver_email, message)
            print("Sent!")
    except Exception as e:
        Log("Error logging in: " + str(e), messageType="ERROR")

def SendImage(ImgFileName):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)

            img_data = open(ImgFileName, 'rb').read()
            msg = MIMEMultipart()

            image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
            msg.attach(image)

            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())

    except Exception as e:
        Log("Error logging in: " + str(e), messageType="ERROR")


def Init():
    self.port = config.GetValue("email", "port")
    self.smtp_server = config.GetValue("email", "smtp_server")
    self.sender_email = config.GetValue("email", "sender_email")
    self.receiver_email = config.GetValue("email", "receiver_email")
    self.password = config.GetValue("email", "password")


if __name__ == "__main__":
    Init()
    SendImage("test.jpg")
    SendMessage("Wowww")