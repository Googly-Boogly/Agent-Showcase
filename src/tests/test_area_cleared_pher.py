import unittest
try:
    from idk_some_code.drone import Drone
except ImportError:
    from drone import Drone
try:
    from idk_some_code.grid import Grid
except ImportError:
    from grid import Grid


class TestAreaClearedPheromone(unittest.TestCase):
    def setUp(self):
        # Set up a 10x10 grid
        self.grid = Grid(10, 10)
        # Start the drone at position (5, 5)
        self.drone = Drone(self.grid, (5, 5))
        self.drone.start_time = 0  # Start time set for the start of the simulation

    def test_area_cleared_pheromone_emission(self):
        # Simulate clearing around the drone
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                self.grid.add_safe_zone(5 + dx, 5 + dy)

        # Move the drone to allow for pheromone check
        self.drone.move("right")  # Move drone to ensure it's still in a controlled area
        self.drone.move("left")  # Move back to original position

        # Simulate time to pass the cooldown period
        current_time = self.drone.area_cleared_cooldown + 1
        self.drone.evaluate_area_cleared(current_time)

        # Check if the "Area Cleared" pheromone was emitted correctly
        pheromones = self.grid.get_pheromones(5, 5)
        self.assertTrue(any(p['type'] == 'area_cleared' for p in pheromones),
                        "Area Cleared pheromone should be emitted.")

    def test_no_pheromone_when_conditions_not_met(self):
        # Ensure no pheromones are emitted if not enough safe zones
        self.grid.add_safe_zone(5, 5)  # Only one safe zone at the drone's position
        current_time = self.drone.area_cleared_cooldown + 1
        self.drone.evaluate_area_cleared(current_time)

        pheromones = self.grid.get_pheromones(5, 5)
        self.assertFalse(any(p['type'] == 'area_cleared' for p in pheromones),
                         "Area Cleared pheromone should not be emitted.")


if __name__ == "__main__":
    unittest.main()
