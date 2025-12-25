import cv2
import numpy as np
import mss
import platform

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self, monitor_index=1):
        """
        Captures the screen.
        Returns a numpy array (RGB) compatible with OpenCV.
        """
        monitor = self.sct.monitors[monitor_index]
        sct_img = self.sct.grab(monitor)
        # Convert to numpy array
        img = np.array(sct_img)
        # Convert BGRA to BGR (standard OpenCV)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

class BallDetector:
    def __init__(self):
        # Default tuning parameters for Hough Circles
        self.dp = 1.2        # Inverse ratio of the accumulator resolution to the image resolution
        self.minDist = 20    # Minimum distance between the centers of the detected circles
        self.param1 = 50     # Higher threshold of the two passed to the Canny edge detector
        self.param2 = 30     # Accumulator threshold for the circle centers at the detection stage
        self.minRadius = 10  # Minimum circle radius
        self.maxRadius = 30  # Maximum circle radius

    def update_params(self, dp=None, minDist=None, param1=None, param2=None, minRadius=None, maxRadius=None):
        if dp is not None: self.dp = dp
        if minDist is not None: self.minDist = minDist
        if param1 is not None: self.param1 = param1
        if param2 is not None: self.param2 = param2
        if minRadius is not None: self.minRadius = minRadius
        if maxRadius is not None: self.maxRadius = maxRadius

    def detect(self, img):
        """
        Detects circles in the given image.
        Returns a list of (x, y, r) tuples.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply blur to reduce noise
        gray = cv2.medianBlur(gray, 5)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=self.dp,
            minDist=self.minDist,
            param1=self.param1,
            param2=self.param2,
            minRadius=self.minRadius,
            maxRadius=self.maxRadius
        )

        detected = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # i[0]=x, i[1]=y, i[2]=radius
                detected.append((int(i[0]), int(i[1]), int(i[2])))

        return detected
