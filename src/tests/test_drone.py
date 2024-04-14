# Additional tests in test_drone.py
import unittest

from idk_some_code.drone import Drone
from idk_some_code.grid import Grid

class TestDroneExpanded(unittest.TestCase):
    """Expands testing for the Drone class, ensuring robustness and reliability."""

    def setUp(self) -> None:
        """Setup a consistent environment for the drone tests."""
        self.grid = Grid(10, 10)  # A cozy little grid for our drone operations
        self.drone = Drone(self.grid, (5, 5))  # Prime real estate, center of the grid

    def test_can_move_checks_obstacles(self):
        """Test that `can_move` correctly identifies impassable obstacles."""
        # Let's add a mountain in the drone's path
        self.grid.add_mountain(5, 4)  # Upward and personal
        self.assertFalse(self.drone.can_move('up'), "Drone thinks it can climb mountains. It cannot.")

    def test_explore_adds_time(self):
        """Ensure time spent is incremented correctly when exploring."""
        original_time = self.drone.time_spent
        self.drone.explore_current_cell(current_time=10)  # Time to get moving
        self.assertGreater(self.drone.time_spent, original_time, "Drone's exploration didn't eat any time. How?")

    def test_explore_marks_safe_zone(self):
        """Exploring should mark the current cell as a safe zone."""
        self.drone.explore_current_cell(current_time=0)
        x, y = self.drone.position
        self.assertTrue(self.grid.is_safe_zone(x, y), "Drone explored, but the grid didn't get the memo about safety.")

    def test_victim_rescue_resets_counters(self):
        """Rescuing a victim should reset the move counter and increment victim counter."""
        self.grid.add_victim(5, 5)
        original_victim_count = self.drone.victim_counter
        self.drone.explore_current_cell(current_time=10)
        self.assertEqual(self.drone.move_counter_since_last_victim, 0, "Drone's move counter didn't reset after a rescue.")
        self.assertEqual(self.drone.victim_counter, original_victim_count, "Drone didn't brag about the victim it just rescued.")

    # def test_need_help_emission_conditions(self):
    #     """Checks if 'Need Help' pheromone is correctly emitted when conditions are met."""
    #     self.drone.victim_counter = 2  # Found some victims
    #     self.drone.move_counter_since_last_victim = 3  # Not too many moves since last victim
    #     self.drone.evaluate_need_help(current_time=50)
    #     x, y = self.drone.position
    #     pheromones = self.grid.get_pheromones(x, y)
    #     self.assertTrue(any(p['type'] == 'need_help' for p in pheromones), "'Need Help' pheromone is missing when it clearly shouldn't be.")

    # Feel free to add more nuanced tests, such as simulating complex drone interactions, validating pheromone decay impacts, etc.


if __name__ == "__main__":
    unittest.main()
