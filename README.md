# Pool Guideline Overlay

This Python script creates a transparent overlay on your screen to help visualize pool shots. It is designed to work over any pool game or website.

## Features

- **Moveable Pockets**: 6 drag-and-drop circles to define the table boundaries.
- **Table Guidelines**: Dashed lines connecting the pockets to visualize the table edges.
- **Target Ball Marker**: A cyan circle to place over the object ball you intend to hit.
- **Trajectory Calculation**: Automatically calculates and draws:
  - The path from the Target Ball to the nearest Pocket.
  - The **Ghost Ball** position (where the Cue Ball must impact).
  - An **Aim Line** indicating the required approach angle for the Cue Ball.

## Requirements

- Python 3.x
- Tkinter (usually included with Python)

## How to Run

1. Open a terminal or command prompt.
2. Navigate to the directory containing `pool_overlay.py`.
3. Run the script:
   ```bash
   python pool_overlay.py
   ```

## Usage

1. **Align Pockets**: Drag the 6 black circles to match the pockets of the pool table on your screen. The white dashed lines help align the walls.
2. **Set Target**: Drag the **Cyan** circle (Target Marker) over the ball you want to sink.
3. **View Guidelines**:
   - The **Green Line** shows the path to the nearest hole.
   - The **White Dashed Circle** is the "Ghost Ball" position. You need to aim your cue ball so it occupies this space at the moment of impact.
   - The **Red Line** shows the line you should aim along.

## Controls

- **Left Click + Drag**: Move circles.
- **'q' or 'Esc'**: Quit the overlay.

## Troubleshooting

- **Transparency on Windows**: The script uses a specific background color (`grey15`) and sets it to be transparent. If this conflicts with the game colors, you can edit the `bg_color` variable in the script.
- **Transparency on Mac/Linux**: The script uses window-wide alpha transparency (`-alpha`). You can adjust the transparency level in the script (default is 0.5) if it's too dark or too light.
