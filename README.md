# Pool Guideline Overlay

This Python script creates a transparent overlay on your screen to help visualize pool shots. It includes computer vision features to automatically detect balls and calculate trajectories.

## Features

- **Auto-Detection**: Scans the screen to find pool balls using Computer Vision.
- **Trajectory Calculation**: Select any detected ball to see:
  - Paths to **all 6 pockets**.
  - The "Ghost Ball" aiming point for each pocket.
  - The aiming line for the Cue Ball.
- **Moveable Pockets**: Drag circles to align the overlay with your game's table.
- **Tuning**: Adjust detection sensitivity for different ball sizes.

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- OpenCV (cv2)
- NumPy
- MSS (for screen capture)

## Installation

1. Install the required Python packages:
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
2. **Scan Screen**: Press **`s`** to scan the table. The overlay will briefly flicker as it captures the screen.
3. **Select Ball**: Click on any **Orange** circle (detected ball). It will turn **Cyan**, and lines will appear showing the shot path to every pocket.
4. **Tune Detection** (If balls aren't detected):
   - Press **`Up Arrow`** to increase the expected ball radius.
   - Press **`Down Arrow`** to decrease the expected ball radius.
   - Re-scan with `s` after adjusting.

## Controls

- **`s`**: Scan for balls.
- **Left Click + Drag**: Move pockets manually.
- **Left Click**: Select a detected ball.
- **`Up/Down Arrows`**: Adjust detection size.
- **`q`** or **`Esc`**: Quit.

## Troubleshooting

- **Transparency on Windows**: The script uses a specific background color (`grey15`) and sets it to be transparent.
- **Transparency on Mac/Linux**: The script uses window-wide alpha transparency (`-alpha`). You can adjust this in the code if needed.
