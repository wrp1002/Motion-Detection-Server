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

# bufferless VideoCapture
class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.fps = self.MeasureFPS()
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
                Log("cv2 error: " + e, messageType="ERROR")

    def read(self):
        return self.q.get()

    def get(self, what):
        return self.cap.get(what)

    def MeasureFPS(self):
        num_frames = 120
        start = time.time()

        for i in range(0, num_frames):
            ret, frame = self.cap.read()

        seconds = time.time() - start
        fps  = num_frames / seconds
        return fps



class Box:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def GetArea(self):
        return self.w * self.h


class VideoDevice:
    def __init__(self, name, url, sensitivity, configManager):
        self.name = name
        self.compareFrame = None
        self.currentFrame = None
        self.url = url
        Log("Initializing...", self)
        self.history = collections.deque(maxlen=historyLen)
        self.threshold = 0
        self.sensitivity = sensitivity
        self.dead = False
        self.config = configManager
        self.refreshRate = self.config.GetValue("refreshComparisonRate")
        self.nextRefreshTime = time.time()

        try:
            self.cap = VideoCapture(self.url)
        except Exception as e:
            Log(e, self, "ERROR")

        if not self.cap.cap.isOpened():
            Log("Could not start video capture", self, "ERROR")
            self.dead = True
            return

        self.fps = self.cap.fps
        Log("Initialized with {} fps".format(self.fps), cam=self)

    def ShouldUpdateCompareFrame(self):
        return time.time() > self.nextRefreshTime

    def UpdateCompareFrame(self, frame):
        self.compareFrame = frame
        self.nextRefreshTime = time.time() + self.refreshRate

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

    def ProcessFrame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def CompareFrames(self, prevFrame, frame):
        frameDelta = cv2.absdiff(self.compareFrame, frame)

        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        boxes = self.GetBoxes(thresh)
        for box in boxes:
            cv2.rectangle(frame, (box.x, box.y), (box.x + box.w, box.y + box.h), (0, 255, 0), 2)

        return (frameDelta, thresh, boxes)

    def Update(self):
        while not self.dead:
            frame = self.cap.read()
            if frame is None:
                continue

            frame = imutils.resize(frame, width=500)
            gray = self.ProcessFrame(frame)

            if self.compareFrame is None or self.ShouldUpdateCompareFrame():
                self.UpdateCompareFrame(gray)
                continue

            frameDelta, thresh, boxes = self.CompareFrames(self.compareFrame, gray)

            text = "Unoccupied"
            motion = False
            biggest = self.GetBiggestBox(boxes)
            if biggest:
                cv2.rectangle(frame, (biggest.x, biggest.y), (biggest.x + biggest.w, biggest.y + biggest.h), (0, 0, 255), 2)
                text = "Occupied"
                motion = True

            cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imshow(self.name + " Security Feed", frame)
            if motion:
                self.SaveVideo()
            #cv2.imshow(self.name + " Thresh", thresh)
            #cv2.imshow(self.name + " Frame Delta", frameDelta)
            cv2.waitKey(1)

            #print(self.cap.get(cv2.CAP_PROP_FPS))

    def Stop(self):
        self.dead = True

    def GetOuputDir(self):
        outputDir = os.path.abspath(self.config.GetValue("outputDir"))
        outputDir = os.path.join(outputDir, self.name)

        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
        return outputDir

    def SaveVideo(self):
        startTime = time.time()
        outputDir = self.GetOuputDir()

        fileName = str(int(time.time()))+ ".avi"
        fileName = os.path.join(outputDir, fileName)

        height, width = self.cap.read().shape[:2]
        print("Size: ", width, "x", height)
        print("fps:", self.fps)
        print("Saving video to: " + fileName + "...", end="")

        videoWriter = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc('M','J','P','G'), self.fps, (width, height))
        videoLength = self.config.GetValue("saveVideoLength")

        while time.time() - startTime < videoLength:
            frame = self.cap.read()

            videoWriter.write(frame)
            cv2.imshow(self.name + " Security Feed", frame)
            cv2.waitKey(1)

        videoWriter.release()
        self.compareFrame = None
        print("Done!")

        return fileName

    def SaveImage(self, image):
        outputDir = self.GetOuputDir()
        fileName = self.name + "-" + str(time.time()) + ".jpg"
        fileName = os.path.join(outputDir, fileName)
        print("Saving image to", fileName)
        cv2.imwrite(fileName, image)



