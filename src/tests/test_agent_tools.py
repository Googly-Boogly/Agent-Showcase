import unittest
from unittest.mock import Mock
try:
    from idk_some_code.drone import Drone
except ImportError:
    from drone import Drone
try:
    from idk_some_code.grid import Grid
except ImportError:
    from grid import Grid

class TestDrone(unittest.TestCase):
    def setUp(self):
        # Mock the Grid to control the environment
        self.grid = Mock()
        self.grid.width = 10
        self.grid.height = 10
        self.grid.is_passable = Mock(return_value=True)
        self.grid.is_victim = Mock(return_value=False)
        self.grid.remove_victim = Mock()
        self.grid.add_pheromone = Mock()
        self.drone = Drone(grid=self.grid, start_pos=(5, 5))

    def test_move_up(self):
        self.drone.move_up()
        self.assertEqual(self.drone.position, (5, 4))
        self.grid.is_passable.assert_called_once_with(5, 4)

    def test_move_down(self):
        self.drone.move_down()
        self.assertEqual(self.drone.position, (5, 6))
        self.grid.is_passable.assert_called_once_with(5, 6)

    def test_move_left(self):
        self.drone.move_left()
        self.assertEqual(self.drone.position, (4, 5))
        self.grid.is_passable.assert_called_once_with(4, 5)

    def test_move_right(self):
        self.drone.move_right()
        self.assertEqual(self.drone.position, (6, 5))
        self.grid.is_passable.assert_called_once_with(6, 5)

    def test_emit_pheromone_need_help(self):
        self.drone.emit_pheromone("need_help", self.current_time)
        self.grid.add_pheromone.assert_called_once_with(5, 5, "need_help", "Assistance required", self.drone.time_spent)

    def test_emit_pheromone_area_cleared(self):
        self.drone.emit_pheromone("area_cleared", self.current_time)
        self.grid.add_pheromone.assert_called_once_with(5, 5, "area_cleared", "Area now under control",
                                                        self.drone.time_spent)

    def test_obstacle_blocking(self):
        # Test obstacle blocking movement
        self.grid.is_passable = Mock(return_value=False)
        self.drone.move_up()
        self.assertEqual(self.drone.position, (5, 5))  # Position should not change


if __name__ == '__main__':
    unittest.main()
