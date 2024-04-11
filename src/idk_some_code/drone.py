# drone.py
import numpy as np
from typing import Tuple, Dict

try:
    from idk_some_code.grid import Grid
except ImportError:
    from grid import Grid


class Drone:
    def __init__(self, grid: Grid, start_pos: Tuple[int, int]) -> None:
        self.grid = grid
        self.position = start_pos
        self.time_spent = 0
        self.victim_counter = 0
        self.move_counter_since_last_victim = 0
        self.drone_state: Dict[str, any] = {
            "position": start_pos,
            "perceptions": {
                "N": None,
                "S": None,
                "E": None,
                "W": None,
                "NE": None,
                "NW": None,
                "SE": None,
                "SW": None,
            },
            # Add more state components as needed, e.g., battery level
        }

    def explore_current_cell(self, current_time: int) -> None:
        """Explores the current cell, adjusting time spent based on obstacles, marks it as a safe zone, and manages pheromone emission."""
        x, y = self.position
        explore_time = self.grid.explore_cell(x, y)
        self.time_spent += explore_time

        # Drop a trail pheromone to mark the path
        self.grid.add_pheromone(x, y, "trail", "Path marked by drone", self.time_spent)

        # If exploring a collapsed building, check for victims
        obstacle = self.grid.obstacles[y][x]
        if obstacle and obstacle['type'] == 'collapsed_building':
            if self.grid.is_victim(x, y):
                self.grid.saved_victims += 1
                # Emit "victim_found" pheromone with higher intensity to signal discovery
                self.grid.add_pheromone(x, y, "victim_found", "Victim located here", self.time_spent, intensity=2.0)
                # Simulate additional time to assist victim in collapsed building
                self.time_spent += 5  # Arbitrary value, adjust as needed
                self.grid.remove_victim(x, y)
                # Evaluate for "Need Help" pheromone emission
                self.evaluate_need_help(current_time)

        # Regardless of whether there was an obstacle, once explored, mark the cell as a safe zone
        self.grid.add_safe_zone(x, y)

        # Attempt to emit an "Area Cleared" pheromone if conditions are met
        self.evaluate_area_cleared(current_time)

    def assess_and_act(self, current_time: int) -> None:
        """Randomly decide an action, with a simple sense of surroundings."""
        if np.random.rand() > 0.5:  # Randomly decide to move or stay
            directions = ['up', 'down', 'left', 'right']
            possible_moves = [d for d in directions if self.can_move(d)]
            if possible_moves:  # If there are any possible moves
                self.move(np.random.choice(possible_moves))
        self.explore_current_cell(current_time)

    def can_move(self, direction: str) -> bool:
        """Check if a move in the given direction is possible."""
        next_x, next_y = self.position
        if direction == "up":
            next_y -= 1
        elif direction == "down":
            next_y += 1
        elif direction == "left":
            next_x -= 1
        elif direction == "right":
            next_x += 1

        return 0 <= next_x < self.grid.width and 0 <= next_y < self.grid.height and self.grid.is_passable(next_x,
                                                                                                          next_y)

    def move(self, direction: str) -> None:
        """Moves the drone in the specified direction, if possible."""
        if direction == "up" and self.can_move("up"):
            self.position = (self.position[0], self.position[1] - 1)
            self.update_state()
        elif direction == "down" and self.can_move("down"):
            self.position = (self.position[0], self.position[1] + 1)
            self.update_state()
        elif direction == "left" and self.can_move("left"):
            self.position = (self.position[0] - 1, self.position[1])
            self.update_state()
        elif direction == "right" and self.can_move("right"):
            self.position = (self.position[0] + 1, self.position[1])
            self.update_state()
        else:
            # Let's humorously acknowledge an unsuccessful move
            print("This drone attempted a dance move it hasn't quite mastered yet.")

    def evaluate_area_cleared(self, current_time: int) -> None:
        """Evaluates and possibly emits an 'Area Cleared' pheromone based on the defined conditions."""
        x, y = self.position
        # Adjust these parameters as needed
        radius = 5  # Search radius for 'Need Help' pheromones and other drones
        age_threshold = 10  # Turns since 'Need Help' was emitted

        recent_need_help_pheromones = self.grid.get_recent_need_help_pheromones(x, y, radius, age_threshold, current_time)
        if recent_need_help_pheromones and not self.grid.check_for_drone_activity(x, y, radius):
            # Conditions met for emitting 'Area Cleared' if no additional victims found and no other drones are actively working in the area
            self.grid.add_pheromone(x, y, "area_cleared", "Area now under control", current_time)

    def evaluate_need_help(self, current_time: int) -> None:
        """
        Evaluates conditions to decide on emitting a 'Need Help' pheromone, based on the discovery of victims in close proximity
        within a short timeframe.
        """
        # Parameters to adjust according to simulation needs
        victim_proximity_limit = 4  # Number of moves within which finding another victim triggers 'Need Help'
        recent_victim_count = 2     # Number of victims found within the proximity limit to trigger 'Need Help'

        if self.move_counter_since_last_victim <= victim_proximity_limit and self.victim_counter >= recent_victim_count:
            self.grid.add_pheromone(self.position[0], self.position[1], "need_help", "Assistance required", current_time)
            # Reset counters after emitting 'Need Help' pheromone
            self.victim_counter = 0
            self.move_counter_since_last_victim = 0

    def update_state(self) -> None:
        """Updates the drone's state based on its surroundings and pheromones within its visibility range."""
        x, y = self.position
        self.drone_state["position"] = (x, y)

        # Use the new get_pheromones_square method to update perceptions based on the current position
        visibility_range = 5  # Define as needed
        self.drone_state["perceptions"] = self.grid.get_pheromones_square(self.position, visibility_range)

