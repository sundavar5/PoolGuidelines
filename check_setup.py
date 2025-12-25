import sys
import os

def check_setup():
    print("--- Environment Check ---")

    # 1. Check Python Version
    major, minor, micro, release, serial = sys.version_info
    print(f"Python Version: {major}.{minor}.{micro}")

    if major == 3:
        if minor >= 13:
            print("WARNING: You are using a very new version of Python.")
            print("         Libraries like 'numpy' and 'opencv-python' may fail to install")
            print("         because binary wheels are not yet available.")
            print("         RECOMMENDATION: Install Python 3.12.")
        elif minor < 9:
            print("WARNING: Your Python version is quite old. Some libraries may not work.")
        else:
            print("Python version is compatible (3.9 - 3.12).")
    else:
        print("WARNING: This script is designed for Python 3.")

    print("-" * 20)

    # 2. Check Tkinter
    try:
        import tkinter
        print("Tkinter: INSTALLED")
    except ImportError:
        print("Tkinter: MISSING")
        print("         Please install Tkinter. (e.g. 'sudo apt install python3-tk' on Linux)")
        print("         On Windows, check the 'tcl/tk and IDLE' option during Python installation.")

    print("-" * 20)

    # 3. Check Dependencies
    dependencies = ["cv2", "numpy", "mss"]
    missing = []

    for dep in dependencies:
        try:
            if dep == "cv2":
                import cv2
            elif dep == "numpy":
                import numpy
            elif dep == "mss":
                import mss
            print(f"{dep}: INSTALLED")
        except ImportError:
            print(f"{dep}: MISSING")
            missing.append(dep)

    if missing:
        print("-" * 20)
        print("You need to install missing dependencies:")
        print(f"pip install {' '.join(['opencv-python' if m == 'cv2' else m for m in missing])}")

    print("\nCheck Complete.")

if __name__ == "__main__":
    check_setup()
