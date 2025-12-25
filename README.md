# Pool Guideline Overlay

This Python script creates a transparent overlay on your screen to help visualize pool shots. It includes computer vision features to automatically detect balls and calculate trajectories.

## Features

- **Auto-Detection**: Scans the screen to find pool balls using Computer Vision.
- **Trajectory Calculation**: Select any detected ball to see:
  - Paths to **all 6 pockets**.
  - The "Ghost Ball" aiming point for each pocket.
  - The aiming line for the Cue Ball.
- **Moveable Pockets**: Drag circles to align the overlay with your game's table.
- **Interactive Tuning**: Resize the target marker to match real balls for accurate detection.

## Requirements

- **Python 3.10, 3.11, or 3.12** (Recommended)
    - *Note: Python 3.13+ may fail to install dependencies without a C++ compiler.*
- Tkinter (usually included with Python)
- OpenCV (cv2)
- NumPy
- MSS (for screen capture)

## Installation

1. **Check your Python version**:
   Run the included check script to ensure your environment is ready:
   ```bash
   python check_setup.py
   ```

2. **Install the required Python packages**:
   ```bash
   pip install opencv-python numpy mss
   ```
   *(Note: You can use `opencv-python-headless` if you don't need OpenCV's UI tools, which saves space.)*

## How to Run

1. Open a terminal or command prompt.
2. Navigate to the directory containing `pool_overlay.py`.
3. Run the script:
   ```bash
   python pool_overlay.py
   ```

## Usage

1. **Align Pockets**: Drag the 6 black circles to match the pockets of the pool table on your screen.
2. **Calibrate Size**:
   - Place the **Cyan** "Target Ball" circle over a real ball on the screen.
   - **Scroll Mouse Wheel** to resize the circle until it matches the ball size perfectly.
   - *This step is crucial for the auto-detection to work.*
3. **Scan Screen**: Press **`s`** to scan. The overlay will flicker as it captures the screen.
4. **Select Ball**: Click on any **Orange** circle (detected ball). It will turn **Cyan**, and lines will appear showing the shot path to every pocket.

## Controls

- **`s`**: Scan for balls.
- **Mouse Wheel**: Resize the Target Ball (for calibration).
- **Left/Right Arrows**: Adjust detection sensitivity (Left=More sensitive, Right=Less).
- **Left Click + Drag**: Move pockets manually.
- **Left Click**: Select a detected ball.
- **`q`** or **`Esc`**: Quit.

## Troubleshooting

### No Balls Detected?
1. **Check Size**: Ensure the Cyan circle matches the real ball size. The detector looks for circles of that exact size (+/- 5 pixels).
2. **Adjust Sensitivity**: Press **Left Arrow** to lower the sensitivity threshold (allow weaker circles). Watch the status text on screen.
3. **Debug**: The script saves `debug_gray_TIMESTAMP.png` when scanning. Check this image to see if the screen capture is working and if the balls are visible in grayscale.

### Installation Errors
If you see an error like `metadata-generation-failed`, `Failed to activate VS environment`, or `Unknown compiler` when installing requirements:
- **Cause**: You are likely using a very new version of Python (e.g., Python 3.13 or 3.14).
- **Solution**: Please install **Python 3.12** and try again.

### Transparency Issues
- **Windows**: The script uses a specific background color (`grey15`) and sets it to be transparent. Ensure you are running in a windowed mode if possible if the overlay doesn't appear on top.
- **Mac/Linux**: The script uses window-wide alpha transparency (`-alpha`). You can adjust this in the code if needed.
