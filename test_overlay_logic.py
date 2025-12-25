import unittest
import math
from pool_overlay import normalize_vector, scale_vector, add_vectors, subtract_vectors, distance, calculate_ghost_ball_pos

class TestPoolOverlayLogic(unittest.TestCase):

    def test_normalize_vector(self):
        v = (3, 4)
        norm = normalize_vector(v)
        self.assertAlmostEqual(norm[0], 0.6)
        self.assertAlmostEqual(norm[1], 0.8)

        v_zero = (0, 0)
        self.assertEqual(normalize_vector(v_zero), (0, 0))

    def test_scale_vector(self):
        v = (1, 2)
        scaled = scale_vector(v, 2)
        self.assertEqual(scaled, (2, 4))

    def test_add_vectors(self):
        v1 = (1, 2)
        v2 = (3, 4)
        result = add_vectors(v1, v2)
        self.assertEqual(result, (4, 6))

    def test_subtract_vectors(self):
        v1 = (3, 4)
        v2 = (1, 2)
        result = subtract_vectors(v1, v2)
        self.assertEqual(result, (2, 2))

    def test_distance(self):
        p1 = (0, 0)
        p2 = (3, 4)
        self.assertEqual(distance(p1, p2), 5.0)

    def test_calculate_ghost_ball_pos(self):
        # Setup: Pocket at (100, 0), Target at (50, 0), Ball diameter 10
        # Line is horizontal along x-axis.
        # Vector Target -> Pocket is (50, 0). Normalized (1, 0).
        # We want Ghost Ball to be "behind" the Target relative to the Pocket.
        # So we move from Target (50, 0) AWAY from Pocket.
        # Wait, let's re-read the logic in the file:
        # Ghost Pos = Target Pos - (Direction * Ball Diameter)
        # Direction is Target -> Pocket.
        # So (50, 0) - ((1, 0) * 10) = (40, 0).
        # Pocket (100) <--- Target (50) <--- Ghost (40).
        # This seems correct for hitting the target INTO the pocket. The ghost ball (cue ball) hits the target from the left to push it right.

        pocket_pos = (100, 0)
        target_pos = (50, 0)
        ball_diameter = 10

        ghost_pos = calculate_ghost_ball_pos(target_pos, pocket_pos, ball_diameter)
        self.assertAlmostEqual(ghost_pos[0], 40.0)
        self.assertAlmostEqual(ghost_pos[1], 0.0)

    def test_calculate_ghost_ball_pos_vertical(self):
        # Pocket (0, 100), Target (0, 50), Diameter 10
        # Vector Target -> Pocket is (0, 50) -> (0, 1)
        # Ghost = (0, 50) - (0, 1)*10 = (0, 40)
        pocket_pos = (0, 100)
        target_pos = (0, 50)
        ball_diameter = 10

        ghost_pos = calculate_ghost_ball_pos(target_pos, pocket_pos, ball_diameter)
        self.assertAlmostEqual(ghost_pos[0], 0.0)
        self.assertAlmostEqual(ghost_pos[1], 40.0)

    def test_calculate_ghost_ball_pos_diagonal(self):
        # Pocket (100, 100), Target (50, 50)
        # Vector (50, 50). Norm (1/sqrt2, 1/sqrt2)
        # Diameter 10. Offset (10/sqrt2, 10/sqrt2) approx (7.07, 7.07)
        # Ghost = (50, 50) - (7.07, 7.07) = (42.93, 42.93)
        pocket_pos = (100, 100)
        target_pos = (50, 50)
        ball_diameter = 10

        ghost_pos = calculate_ghost_ball_pos(target_pos, pocket_pos, ball_diameter)
        offset = 10 / math.sqrt(2)
        self.assertAlmostEqual(ghost_pos[0], 50 - offset)
        self.assertAlmostEqual(ghost_pos[1], 50 - offset)

if __name__ == '__main__':
    unittest.main()
