import tkinter as tk
from tkinter import ttk
import math
import os
import time
from vision import ScreenCapture, BallDetector

# --- Geometry / Math Functions ---

def normalize_vector(v):
    mag = math.sqrt(v[0]**2 + v[1]**2)
    if mag == 0: return (0, 0)
    return (v[0] / mag, v[1] / mag)

def scale_vector(v, s):
    return (v[0] * s, v[1] * s)

def add_vectors(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def subtract_vectors(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_ghost_ball_pos(target_pos, pocket_pos, ball_diameter):
    vec_t_to_p = subtract_vectors(pocket_pos, target_pos)
    direction = normalize_vector(vec_t_to_p)
    offset = scale_vector(direction, ball_diameter)
    ghost_pos = subtract_vectors(target_pos, offset)
    return ghost_pos

# --- UI Classes ---

class DraggablePoint:
    def __init__(self, canvas, x, y, color, radius=10, name="point", on_click_callback=None):
        self.canvas = canvas
        self.radius = radius
        self.color = color
        self.name = name
        self.on_click_callback = on_click_callback

        self.id = canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="white", width=2, tags=name
        )
        self.center_x = x
        self.center_y = y

        self.canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_release)

        self._drag_data = {"x": 0, "y": 0}

    def on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        if self.on_click_callback:
            self.on_click_callback(self)

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        self.canvas.move(self.id, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        coords = self.canvas.coords(self.id)
        self.center_x = (coords[0] + coords[2]) / 2
        self.center_y = (coords[1] + coords[3]) / 2

        self.canvas.event_generate("<<PointMoved>>")

    def on_release(self, event):
        self._drag_data = {"x": 0, "y": 0}

    def get_position(self):
        return (self.center_x, self.center_y)

    def set_radius(self, new_radius):
        self.radius = max(5, new_radius) # Min size 5
        self.canvas.coords(
            self.id,
            self.center_x - self.radius, self.center_y - self.radius,
            self.center_x + self.radius, self.center_y + self.radius
        )

    def destroy(self):
        self.canvas.delete(self.id)

class PoolOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Pool Guideline Overlay")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.bg_color = "grey15"
        if os.name == "nt":
            self.root.config(bg=self.bg_color)
            self.root.wm_attributes("-transparentcolor", self.bg_color)
        else:
            self.root.attributes('-alpha', 0.5)
            self.root.config(bg=self.bg_color)

        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height,
                                bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.instructions = self.canvas.create_text(
            screen_width // 2, 40,
            text="Step 1: Scroll to resize Cyan circle to match a ball.\nStep 2: Press 's' to Scan.\nStep 3: Click Orange ball to aim.",
            fill="yellow", font=("Arial", 16, "bold"), justify="center"
        )

        self.status_text = self.canvas.create_text(
            screen_width // 2, 80,
            text="Sensitivity: 25 (Adj: L/R Arrow)",
            fill="white", font=("Arial", 12)
        )

        # Vision Components
        self.capture = ScreenCapture()
        self.detector = BallDetector()
        self.detection_sensitivity = 25 # Default param2

        # Initialize Pockets
        cx, cy = screen_width // 2, screen_height // 2
        w, h = 400, 200

        self.pockets = []
        pocket_positions = [
            (cx - w, cy - h), (cx, cy - h), (cx + w, cy - h),
            (cx - w, cy + h), (cx, cy + h), (cx + w, cy + h)
        ]

        for i, pos in enumerate(pocket_positions):
            p = DraggablePoint(self.canvas, pos[0], pos[1], color="black", radius=15, name=f"pocket_{i}")
            self.pockets.append(p)

        # Initialize Target Ball
        self.target_ball = DraggablePoint(self.canvas, cx, cy, color="cyan", radius=15, name="target")

        # Detected Balls Management
        self.detected_balls = []
        self.selected_ball = None

        self.wall_lines = []
        self.trajectory_lines = []

        self.canvas.bind("<<PointMoved>>", self.redraw)

        # Bindings
        self.root.bind("<q>", lambda e: root.destroy())
        self.root.bind("<Escape>", lambda e: root.destroy())
        self.root.bind("<s>", self.scan_balls)

        # Resizing Target Ball
        self.root.bind("<MouseWheel>", self.on_scroll)   # Windows
        self.root.bind("<Button-4>", self.on_scroll_up) # Linux Scroll Up
        self.root.bind("<Button-5>", self.on_scroll_down) # Linux Scroll Down

        # Sensitivity Tuning
        self.root.bind("<Left>", lambda e: self.tune_sensitivity(1))  # Increase param2 (less sensitive)
        self.root.bind("<Right>", lambda e: self.tune_sensitivity(-1)) # Decrease param2 (more sensitive)

        self.redraw(None)

    def on_scroll(self, event):
        # Windows scroll event.delta is usually 120
        delta = 1 if event.delta > 0 else -1
        self.target_ball.set_radius(self.target_ball.radius + delta)

    def on_scroll_up(self, event):
        self.target_ball.set_radius(self.target_ball.radius + 1)

    def on_scroll_down(self, event):
        self.target_ball.set_radius(self.target_ball.radius - 1)

    def tune_sensitivity(self, delta):
        # param2 range: 10 (very sensitive/noisy) to 100 (very strict)
        self.detection_sensitivity = max(10, min(100, self.detection_sensitivity + delta))
        self.canvas.itemconfig(self.status_text, text=f"Sensitivity: {self.detection_sensitivity} (Lower=More Balls)")

    def scan_balls(self, event):
        # 1. Hide Window
        self.root.withdraw()
        self.root.update()
        time.sleep(0.2)

        # 2. Capture
        img = self.capture.capture()

        # 3. Restore Window
        self.root.deiconify()

        # 4. Detect
        # Use target ball size as reference (+/- 5 pixels)
        ref_radius = self.target_ball.radius

        print(f"Scanning... Target Radius: {ref_radius}, Sensitivity: {self.detection_sensitivity}")

        balls = self.detector.detect(
            img,
            min_radius=max(5, ref_radius - 5),
            max_radius=ref_radius + 5,
            sensitivity=self.detection_sensitivity,
            debug=True # Save debug images
        )

        print(f"Detected {len(balls)} balls.")
        self.canvas.itemconfig(self.instructions, text=f"Found {len(balls)} balls. Click Orange ball to aim.")

        # 5. Update UI
        self.clear_detected_balls()
        if balls:
            for b in balls:
                x, y, r = b
                dp = DraggablePoint(
                    self.canvas, x, y, color="orange", radius=r,
                    name="detected_ball", on_click_callback=self.select_ball
                )
                self.detected_balls.append(dp)

        self.redraw(None)

    def clear_detected_balls(self):
        for b in self.detected_balls:
            b.destroy()
        self.detected_balls = []
        self.selected_ball = None

    def select_ball(self, ball_obj):
        self.selected_ball = ball_obj
        for b in self.detected_balls:
            self.canvas.itemconfig(b.id, fill="orange")
        self.canvas.itemconfig(ball_obj.id, fill="cyan")
        self.redraw(None)

    def redraw(self, event):
        self.draw_walls()
        self.draw_trajectories()

    def draw_walls(self):
        for line in self.wall_lines:
            self.canvas.delete(line)
        self.wall_lines = []

        indices = [0, 1, 2, 5, 4, 3, 0]
        points = [self.pockets[i].get_position() for i in indices]

        for k in range(len(points) - 1):
            p1 = points[k]
            p2 = points[k+1]
            line_id = self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="white", width=2, dash=(5, 5))
            self.wall_lines.append(line_id)

    def draw_trajectories(self):
        for item in self.trajectory_lines:
            self.canvas.delete(item)
        self.trajectory_lines = []

        if not self.selected_ball:
            return

        target_pos = self.selected_ball.get_position()
        ball_diameter = self.selected_ball.radius * 2

        for pocket in self.pockets:
            pocket_pos = pocket.get_position()

            # 1. Line to Pocket
            l1 = self.canvas.create_line(
                target_pos[0], target_pos[1], pocket_pos[0], pocket_pos[1],
                fill="lime", width=1, dash=(2, 4)
            )
            self.trajectory_lines.append(l1)

            # 2. Ghost Ball
            ghost_pos = calculate_ghost_ball_pos(target_pos, pocket_pos, ball_diameter)
            r = self.selected_ball.radius
            gb = self.canvas.create_oval(
                ghost_pos[0] - r, ghost_pos[1] - r,
                ghost_pos[0] + r, ghost_pos[1] + r,
                outline="white", width=1, dash=(2, 2)
            )
            self.trajectory_lines.append(gb)

            # 3. Aim Line
            vec_p_to_t = subtract_vectors(target_pos, pocket_pos)
            direction = normalize_vector(vec_p_to_t)
            aim_length = 150
            aim_end = add_vectors(ghost_pos, scale_vector(direction, aim_length))

            al = self.canvas.create_line(
                ghost_pos[0], ghost_pos[1], aim_end[0], aim_end[1],
                fill="red", width=2, arrow=tk.FIRST
            )
            self.trajectory_lines.append(al)

if __name__ == "__main__":
    root = tk.Tk()
    app = PoolOverlay(root)
    root.mainloop()
