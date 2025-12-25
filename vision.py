import cv2
import numpy as np
import mss
import platform
import time

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self, monitor_index=1):
        """
        Captures the screen.
        Returns a numpy array (RGB) compatible with OpenCV.
        """
        # Monitor 1 is usually the primary.
        # TODO: Handle multi-monitor setups better if needed.
        if len(self.sct.monitors) <= monitor_index:
            monitor_index = 0 # Fallback to 'all monitors' if index out of bounds

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
        self.minDist = 15    # Minimum distance between the centers of the detected circles
        self.param1 = 50     # Higher threshold of the two passed to the Canny edge detector
        self.param2 = 25     # Accumulator threshold (Lower = more circles detected, more false positives)
        self.minRadius = 10  # Minimum circle radius
        self.maxRadius = 40  # Maximum circle radius

    def detect(self, img, min_radius=None, max_radius=None, sensitivity=None, debug=False):
        """
        Detects circles in the given image.
        Returns a list of (x, y, r) tuples.

        Args:
            min_radius (int): Override min radius
            max_radius (int): Override max radius
            sensitivity (int): Override param2 (Lower value = Higher sensitivity)
            debug (bool): If True, saves intermediate images for debugging.
        """
        # Use provided overrides or instance defaults
        r_min = min_radius if min_radius is not None else self.minRadius
        r_max = max_radius if max_radius is not None else self.maxRadius
        p2 = sensitivity if sensitivity is not None else self.param2

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply blur to reduce noise
        # GaussianBlur is often better for HoughCircles than MedianBlur
        gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        if debug:
            cv2.imwrite(f"debug_gray_{int(time.time())}.png", gray_blurred)

        circles = cv2.HoughCircles(
            gray_blurred,
            cv2.HOUGH_GRADIENT,
            dp=self.dp,
            minDist=r_min * 1.5, # Centers shouldn't be closer than 1.5x radius
            param1=self.param1,
            param2=p2,
            minRadius=r_min,
            maxRadius=r_max
        )

        detected = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # i[0]=x, i[1]=y, i[2]=radius
                detected.append((int(i[0]), int(i[1]), int(i[2])))

        if debug:
            print(f"DEBUG: Search Params - R:[{r_min}-{r_max}], Sens:{p2}. Found: {len(detected)}")

        return detected
