import os, sys, time
from cv2 import cv2
import numpy as np

import queue
import threading
import collections
import imutils
import requests
import time

from Log import Log
import logging
import ConfigManager as config
import EmailManager as email

historyLen = 30
videoCodec = cv2.VideoWriter_fourcc("D", "I", "V", "X")

class VideoWriter:
    def __init__(self):
        self.queue = queue.Queue()
        self.fileName = None
        self.videoWriter = None
        self.writing = False
        self.writeThread = None

    def Start(self, fileName, fps, width, height, fourcc):
        self.fileName = fileName
        self.writing = True
        with self.queue.mutex:
            self.queue.queue.clear()

        self.videoWriter = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc(*fourcc), fps, (width, height))
        self.writeThread = threading.Thread(target=self.Run)
        self.writeThread.start()

    def Stop(self):
        self.writing = False
        self.writeThread.join()
        self.videoWriter.release()

    def Run(self):
        while self.writing or not self.queue.empty():
            if not self.queue.empty():
                self.videoWriter.write(self.queue.get())
            else:
                time.sleep(0.1)

    def Feed(self, frame):
        if not self.queue.full():
            self.queue.put(frame)


# bufferless VideoCapture
class VideoCapture:
    def __init__(self, name, cam):
        self.cap = cv2.VideoCapture(name, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            self.dead = True
            raise Exception("Could not start video capture")

        self.q = queue.Queue()
        self.dead = False
        self.updateThread = threading.Thread(target=self._reader)
        self.updateThread.daemon = True
        self.updateThread.start()
        Log("Measuring FPS...", cam)
        self.fps = self.MeasureFPS(cam.name)

  # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while not self.dead:
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

    def Stop(self):
        self.dead = True
        self.updateThread.join()
        self.cap.release()

    def MeasureFPS(self, camName):
        videoWriter = VideoWriter()
        height, width = self.read().shape[:2]
        videoWriter.Start("measure" + camName + ".mp4", 20, width, height, "mp4v")

        num_frames = 120
        start = time.time()

        for i in range(0, num_frames):
            frame = self.read()
            videoWriter.Feed(frame)

        seconds = time.time() - start
        fps  = num_frames / seconds
        videoWriter.Stop()

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
    def Init(self):
        if self.dead:
            return

        Log("Initializing...", self)
        try:
            self.cap = VideoCapture(self.url, self)
        except Exception as e:
            Log(e, self, "ERROR")
            restartTime = config.GetValue("cameraRestartTime")
            Log("Waiting", restartTime, "`seconds...")
            time.sleep(restartTime)
            self.Init()
            return

        self.fps = self.cap.fps
        self.prevFrames = collections.deque(maxlen=int(self.fps * config.GetValue("secondsBefore")))
        self.initialized = True
        Log("Initialized with {} fps. Will keep a buffer of {} frames".format(self.fps, self.prevFrames.maxlen), cam=self)

        

    def __init__(self, name, url, sensitivity):
        self.name = name
        self.compareFrame = None
        self.currentFrame = None
        self.url = url
        self.threshold = 0
        self.sensitivity = sensitivity
        self.refreshRate = config.GetValue("refreshComparisonRate")
        self.nextRefreshTime = time.time()
        self.videoWriter = VideoWriter()
        self.initialized = False
        self.dead = False

        # Start update thread
        self.updateThread = threading.Thread(target=self.Update)
        self.updateThread.start()

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
            try:
                if not self.initialized:
                    self.Init()
                    continue

                frame = self.cap.read()
                if frame is None:
                    continue

                self.prevFrames.appendleft(frame.copy())
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

                #cv2.imshow(self.name + " Security Feed", frame)
                #cv2.imshow(self.name + " Thresh", thresh)
                #cv2.imshow(self.name + " Frame Delta", frameDelta)

                if motion:
                    self.SaveVideo()
                    #email.SendMessage("Motion detected from '" + self.name + "'")

                cv2.waitKey(1)
            except Exception as e:
                Log("Exception in Update: " + e, self)

    def Stop(self):
        self.cap.Stop()

    def GetOuputDir(self):
        outputDir = os.path.abspath(config.GetValue("outputDir"))
        outputDir = os.path.join(outputDir, self.name)

        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        return outputDir

    def SaveVideo(self):
        outputDir = self.GetOuputDir()

        fileName = str(int(time.time()))+ ".mp4"
        fileName = os.path.join(outputDir, fileName)

        height, width = self.cap.read().shape[:2]
        print("Size: ", width, "x", height)
        print("fps:", self.fps)
        print("Saving video to: " + fileName + "...", end="")

        #videoWriter = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc(*"mp4v"), int(self.fps), (width, height))
        self.videoWriter.Start(fileName, self.fps, width, height, "mp4v")
        videoLength = config.GetValue("saveVideoLength")

        if self.prevFrames:
            self.videoWriter.Feed(self.prevFrames.pop())

        saveFrame = None

        sent = False
        count = 0
        startTime = time.time()
        while time.time() - startTime < videoLength:
            self.prevFrames.appendleft(self.cap.read())

            frame = self.prevFrames.pop()
            self.videoWriter.Feed(frame)
            #cv2.imshow(self.name + " Security Feed", frame)
            count += 1

            if time.time() - startTime > videoLength / 2 and not sent:
                sent = True
                saveFrame = frame

        fps = count / (time.time() - startTime)
        print("Actual FPS:", fps)
        self.videoWriter.Stop()

        self.compareFrame = None
        if config.GetValue("email", "enabled"):
            fileName = self.SaveImage(frame)
            email.SendImage(fileName)
        #os.sys("ffmpeg -y -r 30 -i 6bad.mp4 6out.mp4")

        print("Done!")
        return fileName

    def SaveImage(self, image):
        outputDir = self.GetOuputDir()
        fileName = self.name + "-" + str(time.time()) + ".jpg"
        fileName = os.path.join(outputDir, fileName)
        print("Saving image to", fileName)
        cv2.imwrite(fileName, image)
        return fileName
