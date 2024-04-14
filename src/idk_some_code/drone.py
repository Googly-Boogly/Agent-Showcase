# drone.py
from collections import deque

import numpy as np
from typing import Tuple, Dict

try:
    from idk_some_code.grid import Grid
except ImportError:
    from grid import Grid


class Drone:
    def __init__(self, grid: Grid, start_pos: Tuple[int, int], start_time: int = 0) -> None:
        self.grid = grid
        self.position = start_pos
        self.time_spent = 0
        self.victim_counter = 0
        self.move_counter_since_last_victim = 0
        self.visited_cells_history = deque(maxlen=4)
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
        self.help_threshold = 2  # Number of unique cells with victims before emitting "Need Help"
        self.last_help_time = 0  # Tracks the last time "Need Help" was emitted
        self.help_cooldown = 30  # Time units to wait before "Need Help" can be emitted again
        self.area_cleared_cooldown = 30
        self.start_time = start_time
        self.last_area_cleared_time = 0  # Initialize the last time the 'Area Cleared' was emitted
        self.area_cleared_cooldown = 30  # Time units to wait before 'Area Cleared' can be emitted again

    def explore_current_cell(self, current_time: int) -> None:
        x, y = self.position
        if self.grid.is_victim(x, y):
            print(f"Commencing assistance for victim at ({x}, {y}).")
            self.grid.saved_victims += 1
            # self.grid.add_pheromone(x, y, "victim_found", "Victim located here", self.time_spent, intensity=2.0)
            self.time_spent += 5  # Additional time to assist victim
            self.evaluate_need_help(current_time)
            self.grid.remove_victim(x, y)
        self.grid.add_safe_zone(x, y)

    def assess_and_act(self, current_time: int) -> None:
        """Randomly decide an action, with a simple sense of surroundings."""
        if np.random.rand() > 0.5:  # Randomly decide to move or stay
            directions = ['up', 'down', 'left', 'right']
            possible_moves = [d for d in directions if self.can_move(d)]
            if possible_moves:  # If there are any possible moves
                self.move(np.random.choice(possible_moves))
        self.explore_current_cell(current_time)
        self.evaluate_area_cleared(current_time)

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
        self.update_visited_history(self.position)

    def evaluate_area_cleared(self, current_time: int) -> None:
        print(f"Evaluating area cleared at {self.position}, time: {current_time}")
        time_since_last_cleared = current_time - self.last_area_cleared_time
        if self.area_cleared_conditions_met(current_time) and time_since_last_cleared >= self.area_cleared_cooldown:
            print(f"Emitting 'Area Cleared' at {self.position} at time {current_time}.")
            self.grid.add_pheromone(self.position[0], self.position[1], "area_cleared", "Area now under control",
                                    current_time)
            self.last_area_cleared_time = current_time  # Update the last emission time
        else:
            if not self.area_cleared_conditions_met(current_time):
                print(f"Conditions not met for 'Area Cleared' at {self.position} at time {current_time}.")
            else:
                print(
                    f"'Area Cleared' cooldown in effect. Time remaining: {self.area_cleared_cooldown - time_since_last_cleared} units.")

    def update_state(self) -> None:
        """Updates the drone's state based on its surroundings and pheromones within its visibility range."""
        x, y = self.position
        self.drone_state["position"] = (x, y)

        # Use the new get_pheromones_square method to update perceptions based on the current position
        visibility_range = 5  # Define as needed
        self.drone_state["perceptions"] = self.grid.get_pheromones_square(self.position, visibility_range)

    def update_visited_history(self, new_position: Tuple[int, int]) -> None:
        """Update the history of visited cells with the new position."""
        if not self.visited_cells_history or self.visited_cells_history[-1] != new_position:
            self.visited_cells_history.append(new_position)

    def evaluate_need_help(self, current_time: int) -> None:
        # print(f"Evaluating need for help at {current_time}, visited cells: {self.visited_cells_history}")
        print(f"Current Time: {current_time}, Last Help Time: {self.last_help_time}, Cooldown: {self.help_cooldown}")
        if len(set(self.visited_cells_history)) >= self.help_threshold:
            last_emission_time = current_time - self.last_help_time
            print(f"Time since last help: {last_emission_time}, cooldown: {self.help_cooldown}")
            if last_emission_time > self.help_cooldown:
                print("Emitting 'Need Help' pheromone.")
                self.grid.add_pheromone(self.position[0], self.position[1], "need_help", "Assistance required",
                                        current_time)
                self.last_help_time = current_time
                self.visited_cells_history.clear()

    def area_cleared_conditions_met(self, current_time: int) -> bool:
        """Check conditions such as sufficient time elapsed and a minimum area being safe."""
        time_since_start = current_time - self.start_time
        if time_since_start < self.area_cleared_cooldown:
            return False
        return self.sufficient_area_cleared()

    def sufficient_area_cleared(self) -> bool:
        """Check if a sufficient surrounding area is cleared."""
        x, y = self.position
        safe_count = 0

        for dx in range(-2, 3):  # Check a larger area for robustness
            for dy in range(-2, 3):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                    if self.grid.is_safe_zone(nx, ny):
                        safe_count += 1
        required_safe_zones = 5  # Example threshold
        print(f"Safe count at ({x}, {y}): {safe_count}, required: {required_safe_zones}")
        return safe_count >= required_safe_zones

