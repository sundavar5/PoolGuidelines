import tkinter as tk
import math
import os

# --- Geometry / Math Functions ---

def normalize_vector(v):
    """Returns the unit vector of v."""
    mag = math.sqrt(v[0]**2 + v[1]**2)
    if mag == 0:
        return (0, 0)
    return (v[0] / mag, v[1] / mag)

def scale_vector(v, s):
    """Scales vector v by scalar s."""
    return (v[0] * s, v[1] * s)

def add_vectors(v1, v2):
    """Adds two vectors."""
    return (v1[0] + v2[0], v1[1] + v2[1])

def subtract_vectors(v1, v2):
    """Subtracts v2 from v1."""
    return (v1[0] - v2[0], v1[1] - v2[1])

def distance(p1, p2):
    """Calculates Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_ghost_ball_pos(target_pos, pocket_pos, ball_diameter):
    """
    Calculates the Ghost Ball position.
    The Ghost Ball is the position the Cue Ball must be in at the moment of impact
    to send the Target Ball into the Pocket.
    It is located one ball diameter away from the Target Ball,
    along the line extending from the Pocket through the Target Ball.
    """
    # Vector from Target to Pocket
    vec_t_to_p = subtract_vectors(pocket_pos, target_pos)

    # Direction from Target to Pocket
    direction = normalize_vector(vec_t_to_p)

    # We want to go backwards from the Target (away from pocket) by one ball diameter
    # Ghost Pos = Target Pos - (Direction * Ball Diameter)
    offset = scale_vector(direction, ball_diameter)
    ghost_pos = subtract_vectors(target_pos, offset)

    return ghost_pos

# --- UI Classes ---

class DraggablePoint:
    def __init__(self, canvas, x, y, color, radius=10, name="point"):
        self.canvas = canvas
        self.radius = radius
        self.name = name
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

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        self.canvas.move(self.id, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # Update center coordinates
        coords = self.canvas.coords(self.id)
        self.center_x = (coords[0] + coords[2]) / 2
        self.center_y = (coords[1] + coords[3]) / 2

        # Notify the main app to redraw lines
        self.canvas.event_generate("<<PointMoved>>")

    def on_release(self, event):
        self._drag_data = {"x": 0, "y": 0}

    def get_position(self):
        return (self.center_x, self.center_y)

class PoolOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Pool Guideline Overlay")

        # Make window full screen and transparent
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Keep window on top
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True) # Remove title bar

        # Transparency handling
        self.bg_color = "grey15"
        if os.name == "nt": # Windows
            self.root.config(bg=self.bg_color)
            self.root.wm_attributes("-transparentcolor", self.bg_color)
            self.alpha_mode = False
        else:
            # Linux/Mac (Alpha transparency is the best we can do easily)
            self.root.attributes('-alpha', 0.5)
            self.root.config(bg=self.bg_color)
            self.alpha_mode = True

        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height,
                                bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Instructions
        self.instructions = self.canvas.create_text(
            screen_width // 2, 30,
            text="Drag circles to align pockets. Drag Cyan circle to Target Ball.\nPress 'q' or 'Esc' to Quit.",
            fill="yellow", font=("Arial", 14)
        )

        # Initialize Pockets (Standard Pool Table layout approx)
        # Using relative positions to screen size
        cx, cy = screen_width // 2, screen_height // 2
        w, h = 400, 200 # Approx table size, user adjusts

        self.pockets = []
        pocket_positions = [
            (cx - w, cy - h), (cx, cy - h), (cx + w, cy - h), # Top Row
            (cx - w, cy + h), (cx, cy + h), (cx + w, cy + h)  # Bottom Row
        ]

        for i, pos in enumerate(pocket_positions):
            p = DraggablePoint(self.canvas, pos[0], pos[1], color="black", radius=15, name=f"pocket_{i}")
            self.pockets.append(p)

        # Initialize Target Ball
        self.target_ball = DraggablePoint(self.canvas, cx, cy, color="cyan", radius=12, name="target")
        self.ball_diameter = 24 # Approx visual diameter (2 * radius)

        # Store Line IDs
        self.wall_lines = []
        self.trajectory_lines = []
        self.ghost_ball_id = None
        self.aim_line_id = None

        # Bind event for redraw
        self.canvas.bind("<<PointMoved>>", self.redraw)

        # Quit bindings
        self.root.bind("<q>", lambda e: root.destroy())
        self.root.bind("<Escape>", lambda e: root.destroy())

        self.redraw(None)

    def redraw(self, event):
        self.draw_walls()
        self.draw_trajectory()

    def draw_walls(self):
        # Clear old lines
        for line in self.wall_lines:
            self.canvas.delete(line)
        self.wall_lines = []

        # Connect pockets to form the table boundary
        # Order: Top-Left -> Top-Center -> Top-Right -> Bottom-Right -> Bottom-Center -> Bottom-Left -> Top-Left
        # Indices: 0, 1, 2, 5, 4, 3, 0 (based on initialization order)
        indices = [0, 1, 2, 5, 4, 3, 0]
        points = [self.pockets[i].get_position() for i in indices]

        for k in range(len(points) - 1):
            p1 = points[k]
            p2 = points[k+1]
            line_id = self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="white", width=2, dash=(5, 5))
            self.wall_lines.append(line_id)

    def draw_trajectory(self):
        # Clear old trajectory items
        for line in self.trajectory_lines:
            self.canvas.delete(line)
        self.trajectory_lines = []

        if self.ghost_ball_id:
            self.canvas.delete(self.ghost_ball_id)
            self.ghost_ball_id = None

        if self.aim_line_id:
            self.canvas.delete(self.aim_line_id)
            self.aim_line_id = None

        target_pos = self.target_ball.get_position()

        # Find closest pocket (or can be configured to show all)
        # For now, let's just show the trajectory to the closest pocket for clarity
        best_pocket = None
        min_dist = float('inf')

        for pocket in self.pockets:
            p_pos = pocket.get_position()
            d = distance(target_pos, p_pos)
            if d < min_dist:
                min_dist = d
                best_pocket = p_pos

        if best_pocket:
            # 1. Line from Target to Pocket
            l1 = self.canvas.create_line(
                target_pos[0], target_pos[1], best_pocket[0], best_pocket[1],
                fill="lime", width=2
            )
            self.trajectory_lines.append(l1)

            # 2. Calculate Ghost Ball Position
            ghost_pos = calculate_ghost_ball_pos(target_pos, best_pocket, self.ball_diameter)

            # 3. Draw Ghost Ball
            r = self.target_ball.radius
            self.ghost_ball_id = self.canvas.create_oval(
                ghost_pos[0] - r, ghost_pos[1] - r,
                ghost_pos[0] + r, ghost_pos[1] + r,
                outline="white", width=2, dash=(2, 2)
            )

            # 4. Draw Aim Line (from Ghost Ball extending outwards)
            # A line showing where the cue ball should come from
            # Vector from Pocket to Target (reverse of Target to Pocket)
            vec_p_to_t = subtract_vectors(target_pos, best_pocket)
            direction = normalize_vector(vec_p_to_t)

            # Extend aim line by some length (e.g. 200 pixels)
            aim_length = 300
            aim_end = add_vectors(ghost_pos, scale_vector(direction, aim_length))

            self.aim_line_id = self.canvas.create_line(
                ghost_pos[0], ghost_pos[1], aim_end[0], aim_end[1],
                fill="red", width=2, arrow=tk.FIRST
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = PoolOverlay(root)
    root.mainloop()
