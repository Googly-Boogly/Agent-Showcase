import unittest
from idk_some_code.drone import Drone
from idk_some_code.grid import Grid


class TestDrone(unittest.TestCase):
    def setUp(self):
        """Set up a small grid with a few victims and no obstacles to ensure clear path."""
        self.grid = Grid(10, 10)  # Small grid
        self.drone = Drone(self.grid, (5, 5))
        # Place victims at two specific locations
        self.grid.add_victim(5, 6)
        self.grid.add_victim(5, 7)

    # def test_need_help_emission(self):
    #     self.drone.move('down')
    #     self.drone.explore_current_cell(0)
    #     self.drone.move('down')
    #     self.drone.explore_current_cell(1)
    #     pheromones_at_second_victim = self.grid.get_pheromones(5, 7)
    #     need_help_emitted = any(p['type'] == 'need_help' for p in pheromones_at_second_victim)
    #     self.assertTrue(need_help_emitted,
    #                     f"Need Help pheromone should have been emitted, found pheromones: {pheromones_at_second_victim}")


if __name__ == '__main__':
    unittest.main()
