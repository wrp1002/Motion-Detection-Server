import os, sys, time
from cv2 import cv2
import numpy as np

import queue
import threading
import collections

historyLen = 30
videoCodec = cv2.VideoWriter_fourcc("D", "I", "V", "X")
videoCaptureTime = 10
scriptDir = os.path.dirname(sys.argv[0])


class VideoDevice:
    def __init__(self, name, url, fps, sensitivity):
        self.name = name
        self.prevFrame = None
        self.frame = None
        self.url = url
        self.cap = VideoCapture(self.url)
        self.fps = fps
        self.history = collections.deque(maxlen=historyLen)
        self.threshold = 0
        self.sensitivity = sensitivity

        print(name, "initialized with", self.fps, " fps")

    def ShowFrames(self, images):
        outputImage = np.vstack(images)
        cv2.imshow(self.name, outputImage)
        cv2.waitKey(250)
        #cv2.destroyAllWindows()

    def ShowFrame(self, image):
        self.ShowFrames([image])

    def GetFrame(self):
        print("Getting frame...")

        frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #frame = cv2.fastNlMeansDenoising(frame, None, 10, 10, 7, 21)
        #frame = cv2.blur(frame, (15, 15))

        self.prevFrame = self.frame
        self.frame = frame

        #self.ShowFrames([blurImage, frame])
        #self.ShowFrame(frame)

        #kernel = np.ones((5, 5), np.uint8)
        #blurImage = cv2.dilate(frame, kernel, iterations = 1)
        
        #self.ShowFrame(blurImage)
        
        #cap.release()

        self.CompareFrames()
        
    def CalcDiff(self, frame1, frame2):
        difference = cv2.subtract(frame1, frame2)
        self.ShowFrame(difference)
        diff = difference.sum()
        sum = np.sum(diff)
        return sum

    def UpdateThreshold(self, n):
        self.history.append(n)
        self.threshold = int(sum(self.history) / len(self.history))

    def IsOverThreshold(self, n):
        #highest = max(self.history)
        return (n > self.threshold * self.sensitivity)

    def CompareFrames(self):
        print("Comparing")
        if self.frame is None or self.prevFrame is None:
            return None

        diff = self.CalcDiff(self.frame, self.prevFrame)
        self.UpdateThreshold(diff)

        print(diff)
        print("Current threshold:", self.threshold)

        if len(self.history) < self.history.maxlen:
            print("Not enough yet")
            return

        if self.IsOverThreshold(diff):
            print("Saving video...")
            fileName = self.SaveVideo()
            print("Saved to", fileName)
            time.sleep(1)

        

    def SaveVideo(self):
        startTime = time.time()
        fileName = self.name + "-" + str(time.time()) + ".avi"
        fileName = os.path.join(scriptDir, fileName)

        height, width = self.frame.shape[:2]
        print("Size: ", width, "x", height)

        videoWriter = cv2.VideoWriter(fileName, videoCodec, self.fps, (width, height))

        while time.time() - startTime < videoCaptureTime:
            videoWriter.write(self.cap.read())

        videoWriter.release()

        return fileName






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
            ret, frame = self.cap.read()
            if not ret:
                break

            if not self.q.empty():
                try:
                    self.q.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass

            self.q.put(frame)

    def read(self):
        return self.q.get()

    def get(self, what):
        return self.cap.get(what)