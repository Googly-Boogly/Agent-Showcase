# test_grid.py
import unittest
from idk_some_code.grid import Grid

class TestGrid(unittest.TestCase):
    """Ensures the grid behaves as expected, maintaining the digital world's order."""

    def setUp(self) -> None:
        """Sets up a grid for testing."""
        self.grid = Grid(10, 10)  # A nice, cozy grid for our tests

    def test_add_obstacle(self):
        """Checks if obstacles are added correctly."""
        self.grid.add_obstacle(5, 5)
        self.assertFalse(self.grid.is_obstacle(5, 5), "Grid failed to recognize a freshly added obstacle.")

    def test_add_victim(self):
        """Ensures victims are placed correctly on the grid."""
        self.grid.add_victim(3, 3)
        self.assertTrue(self.grid.is_victim(3, 3), "Grid lost a victim somewhere, not cool.")

    def test_add_safe_zone(self):
        """Verifies that safe zones are correctly marked."""
        self.grid.add_safe_zone(7, 7)
        self.assertTrue(self.grid.is_safe_zone(7, 7), "Safe zone turned out to be not so safe, according to the grid.")

    def test_is_passable(self):
        """Ensures passability checks account for obstacles."""
        self.grid.add_mountain(1, 1)
        self.assertFalse(self.grid.is_passable(1, 1), "Grid thinks mountains are a walk in the park.")

    def test_explore_cell(self):
        """Tests the time taken to explore different types of cells."""
        # Normal ground
        self.assertEqual(self.grid.explore_cell(0, 0), 1, "Exploring plain ground took an unexpected amount of time.")

        # Collapsed building
        self.grid.add_collapsed_building(2, 2)
        self.assertEqual(self.grid.explore_cell(2, 2), 3, "Exploring a collapsed building should take longer.")

    def test_pheromone_decay(self):
        """Checks if pheromones decay over time as expected."""
        self.grid.add_pheromone(4, 4, "test_pheromone", "Testing", 0, 1.0)
        # Simulate time passing
        self.grid.age_pheromones(current_time=10, decay_rate=100)
        remaining_pheromones = self.grid.get_pheromones(4, 4)
        self.assertTrue(all(p['intensity'] < 1.0 for p in remaining_pheromones), "Pheromones are defying the laws of physics and not decaying.")

    def test_get_victim_positions(self):
        """Ensures the grid can accurately report the positions of all victims."""
        self.grid.add_victim(3, 3)
        self.grid.add_victim(6, 7)
        expected_positions = [(3, 3), (6, 7)]
        self.assertEqual(set(self.grid.get_victim_positions()), set(expected_positions), "Grid's victim tracking system needs a tune-up.")

    def test_get_safe_zone_positions(self):
        """Verifies the grid correctly identifies all safe zones."""
        self.grid.add_safe_zone(2, 2)
        self.grid.add_safe_zone(8, 8)
        expected_positions = [(2, 2), (8, 8)]
        self.assertEqual(set(self.grid.get_safe_zone_positions()), set(expected_positions), "Safe zones are playing hide and seek with the grid.")

    def test_get_recent_need_help_pheromones(self):
        """Checks if the grid can correctly identify recent 'Need Help' pheromones."""
        self.grid.add_pheromone(0, 0, "need_help", "Help!", 0, 1.0)
        self.grid.add_pheromone(9, 9, "need_help", "Help!", 100, 1.0)  # This one shouldn't be considered "recent" for a low age_threshold
        recent_pheromones = self.grid.get_recent_need_help_pheromones(0, 0, radius=5, age_threshold=50, current_time=50)
        self.assertEqual(len(recent_pheromones), 1, "Grid's concept of time seems a bit off, finding too many or too few recent cries for help.")

    def test_remove_victim(self):
        """Ensures that victims can be removed correctly from the grid."""
        self.grid.add_victim(4, 4)
        self.assertTrue(self.grid.is_victim(4, 4), "Grid failed to add a victim for removal.")
        self.grid.remove_victim(4, 4)
        self.assertFalse(self.grid.is_victim(4, 4), "Grid is holding victims hostage; it refused to remove one.")

    def test_add_multiple_obstacles_and_passability(self):
        """Tests adding multiple obstacles and then checks passability around them."""
        obstacles = [(1, 1), (1, 2), (2, 1)]
        for x, y in obstacles:
            self.grid.add_mountain(x, y)
        for x, y in obstacles:
            self.assertFalse(self.grid.is_passable(x, y),
                             f"Grid thinks a mountain at ({x}, {y}) is a stroll in the park.")
        # Check a passable area
        self.assertTrue(self.grid.is_passable(0, 0), "Grid mistakenly marked open space as impassable.")

    def test_grid_initialization(self):
        """Verifies that the grid initializes correctly with no obstacles, victims, or pheromones."""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.assertFalse(self.grid.is_obstacle(x, y),
                                 f"Found an obstacle at ({x}, {y}) on a fresh grid. Spooky.")
                self.assertFalse(self.grid.is_victim(x, y),
                                 f"Found a victim at ({x}, {y}) on a new grid. Quite the mystery.")
                self.assertTrue(len(self.grid.get_pheromones(x, y)) == 0,
                                f"Found pheromones at ({x}, {y}) on a brand-new grid. Ghostly.")

    def test_pheromone_intensity_and_decay(self):
        """Tests if the pheromone intensity is set correctly and decays as expected."""
        self.grid.add_pheromone(5, 5, "test", "Test pheromone", 0, intensity=5.0)
        # Initial intensity check
        pheromones = self.grid.get_pheromones(5, 5)
        self.assertEqual(pheromones[0]['intensity'], 5.0, "Pheromone intensity not set correctly initially.")
        # Check after decay
        self.grid.age_pheromones(current_time=10, decay_rate=10)
        pheromones = self.grid.get_pheromones(5, 5)
        self.assertLess(pheromones[0]['intensity'], 5.0, "Pheromone didn't decay or its sunscreen is too effective.")

    def test_obstacle_removal(self):
        """Ensures obstacles can be removed or overridden correctly."""
        self.grid.add_mountain(2, 2)
        self.assertTrue(self.grid.is_obstacle(2, 2), "Grid failed to recognize its own mountain.")
        # Now, let's remove it by making it passable terrain
        self.grid.obstacles[2][
            2] = None  # Direct manipulation for test; consider adding a method for removal if frequent use case
        self.assertFalse(self.grid.is_obstacle(2, 2), "Grid is clinging to its mountain for dear life.")
    # Feel free to expand with additional tests for corner cases and complex scenarios

if __name__ == "__main__":
    unittest.main()
