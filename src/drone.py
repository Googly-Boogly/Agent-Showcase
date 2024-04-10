# drone.py
import numpy as np

from grid import Grid
from typing import Tuple


class Drone:
    def __init__(self, grid: Grid, start_pos: Tuple[int, int]) -> None:
        self.grid = grid
        self.position = start_pos
        self.time_spent = 0

    def explore_current_cell(self) -> None:
        """Explores the current cell, adjusting time spent based on obstacles."""
        x, y = self.position
        explore_time = self.grid.explore_cell(x, y)
        self.time_spent += explore_time

        # If exploring a collapsed building, check for victims
        obstacle = self.grid.obstacles[y][x]
        if obstacle and obstacle['type'] == 'collapsed_building':
            if self.grid.is_victim(x, y):
                # Simulate additional time to assist victim in collapsed building
                self.time_spent += 5  # Arbitrary value, adjust as needed

    def assess_and_act(self, current_time: int) -> None:
        """Randomly decide an action, with a simple sense of surroundings."""
        if np.random.rand() > 0.5:  # Randomly decide to move or stay
            directions = ['up', 'down', 'left', 'right']
            possible_moves = [d for d in directions if self.can_move(d)]
            if possible_moves:  # If there are any possible moves
                self.move(np.random.choice(possible_moves))

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
