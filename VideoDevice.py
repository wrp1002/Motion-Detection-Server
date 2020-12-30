import os, sys, time
from cv2 import cv2
import numpy as np

import queue
import threading
import collections
import imutils
import requests

from Log import Log
import logging

historyLen = 30
videoCodec = cv2.VideoWriter_fourcc("D", "I", "V", "X")
videoCaptureTime = 10
scriptDir = os.path.dirname(sys.argv[0])


# bufferless VideoCapture
class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

  # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            try:
                if not self.cap.isOpened():
                    time.sleep(1)
                    continue

                ret, frame = self.cap.read()
                if not ret:
                    break

                if not self.q.empty():
                    try:
                        self.q.get_nowait()   # discard previous (unprocessed) frame
                    except queue.Empty:
                        pass

                self.q.put(frame)

            except cv2.error as e:
                print("Error hsfd")

    def read(self):
        return self.q.get()

    def get(self, what):
        return self.cap.get(what)


class Box:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def GetArea(self):
        return self.w * self.h


class VideoDevice:
    def __init__(self, name, url, fps, sensitivity):
        self.name = name
        self.firstFrame = None
        self.url = url
        self.fps = fps
        Log("Initializing...", self)
        self.history = collections.deque(maxlen=historyLen)
        self.threshold = 0
        self.sensitivity = sensitivity
        self.dead = False

        try:
            self.cap = VideoCapture(self.url)
        except Exception as e:
            Log(e, self, "ERROR")

        if not self.cap.cap.isOpened():
            Log("Could not start video capture", self, "ERROR")
            self.dead = True
            return

        time.sleep(0.5)

        Log("initialized with " + str(self.fps) + " fps", self)

    def ShowFrames(self, images):
        outputImage = np.vstack(images)
        cv2.imshow(self.name, outputImage)
        cv2.waitKey(250)
        #cv2.destroyAllWindows()

    def ShowFrame(self, image):
        self.ShowFrames([image])

    def GetBiggestBox(self, boxes):
        biggest = None
        for box in boxes:
            if biggest == None or box.GetArea() > biggest.GetArea():
                biggest = box

        return biggest


    def GetBoxes(self, frame):
        boxes = []

        cnts = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:
            if cv2.contourArea(c) < 500:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            boxes.append(Box(x, y, w, h))

        return boxes


    def Update(self):
        while not self.dead:
            frame = self.cap.read()
            text = "Unoccupied"

            if frame is None:
                continue

            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self.firstFrame is None:
                self.firstFrame = gray
                continue

            frameDelta = cv2.absdiff(self.firstFrame, gray)

            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)

            boxes = self.GetBoxes(thresh)
            for box in boxes:
                cv2.rectangle(frame, (box.x, box.y), (box.x + box.w, box.y + box.h), (0, 255, 0), 2)

            biggest = self.GetBiggestBox(boxes)
            if biggest:
                cv2.rectangle(frame, (biggest.x, biggest.y), (biggest.x + biggest.w, biggest.y + biggest.h), (0, 0, 255), 2)
                text = "Occupied"

            cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imshow(self.name + " Security Feed", frame)
            #cv2.imshow(self.name + " Thresh", thresh)
            #cv2.imshow(self.name + " Frame Delta", frameDelta)
            cv2.waitKey(1)

            print(self.cap.get(cv2.CAP_PROP_FPS))

    def Stop(self):
        self.dead = True
        self.cap.cap.release()

    def SaveVideo(self):
        startTime = time.time()
        fileName = self.name + "-" + str(time.time()) + ".avi"
        fileName = os.path.join(scriptDir, fileName)

        height, width = self.firstFrame.shape[:2]
        print("Size: ", width, "x", height)

        videoWriter = cv2.VideoWriter(fileName, videoCodec, self.fps, (width, height))

        while time.time() - startTime < videoCaptureTime:
            videoWriter.write(self.cap.read())

        videoWriter.release()

        return fileName

