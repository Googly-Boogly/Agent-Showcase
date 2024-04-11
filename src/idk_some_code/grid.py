# grid.py
import numpy as np
from typing import List, Tuple, Dict, Optional


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.grid: np.ndarray = np.zeros((height, width), dtype=int)
        # Initialize a structure to hold obstacle information
        self.obstacles: List[List[Optional[Dict]]] = [[None for _ in range(width)] for _ in range(height)]
        # Adding a pheromone layer, with clearer initialization
        self.pheromones: List[List[List[Dict]]] = [[[] for _ in range(width)] for _ in range(height)]
        self.explored_cells = 0
        self.saved_victims: int = 0

    def add_obstacle(self, x: int, y: int) -> None:
        self.grid[y][x] = 1

    def add_victim(self, x: int, y: int) -> None:
        self.grid[y][x] = 2

    def add_safe_zone(self, x: int, y: int) -> None:
        self.explored_cells += 1
        self.grid[y][x] = 3

    def is_obstacle(self, x: int, y: int) -> bool:
        if self.obstacles[y][x] is not None:
            return True
        return False

    def is_victim(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 2

    def is_safe_zone(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 3

    def get_pheromones(self, x: int, y: int) -> List[Dict]:
        """Returns a list of pheromones in the specified location."""
        return self.pheromones[y][x]

    def remove_victim(self, x: int, y: int) -> None:
        """Mark a cell as no longer containing a victim."""
        if self.is_victim(x, y):
            self.grid[y][x] = 0

    def add_pheromone(self, x: int, y: int, pheromone_type: str, message: str, timestamp: int,
                      intensity: float = 1.0) -> None:
        """Adds a pheromone with a specific type to a cell."""
        self.pheromones[y][x].append({
            'type': pheromone_type,
            'message': message,
            'timestamp': timestamp,
            'intensity': intensity
        })

    def pheromone_decay_function(self, intensity: float, age: int, decay_rate: float) -> float:
        """Calculate the new intensity of a pheromone based on its age and a decay rate."""
        return intensity * 0.9 ** (age / decay_rate)

    def age_pheromones(self, current_time: int, decay_rate: float = 100) -> None:
        """Ages pheromones based on the current time, reducing their intensity according to the decay function."""
        for y in range(self.height):
            for x in range(self.width):
                self.pheromones[y][x] = [
                    {**pheromone, 'intensity': self.pheromone_decay_function(pheromone['intensity'],
                                                                             current_time - pheromone['timestamp'],
                                                                             decay_rate)}
                    for pheromone in self.pheromones[y][x] if
                    self.pheromone_decay_function(pheromone['intensity'], current_time - pheromone['timestamp'],
                                                  decay_rate) > 0
                ]

    def get_victim_positions(self) -> List[Tuple[int, int]]:
        """Returns a list of coordinates for all victims."""
        return [(x, y) for y in range(self.height) for x in range(self.width) if self.is_victim(x, y)]

    def get_safe_zone_positions(self) -> List[Tuple[int, int]]:
        """Returns a list of coordinates for all safe zones."""
        return [(x, y) for y in range(self.height) for x in range(self.width) if self.is_safe_zone(x, y)]

    def decay_pheromones(self) -> None:
        """Decays the pheromones on the grid to simulate the passage of time."""
        decay_factor = 0.95  # Example decay rate
        for y in range(self.height):
            for x in range(self.width):
                for pheromone in self.pheromones[y][x]:
                    pheromone['intensity'] *= decay_factor

    def add_mountain(self, x: int, y: int) -> None:
        """Mark a cell as a mountain, impassable."""
        self.obstacles[y][x] = {'type': 'mountain'}

    def add_collapsed_building(self, x: int, y: int) -> None:
        """Mark a cell as a collapsed building, harder to explore."""
        self.obstacles[y][x] = {'type': 'collapsed_building', 'explored': False}

    def is_passable(self, x: int, y: int) -> bool:
        """Check if a cell is passable (not a mountain)."""
        obstacle = self.obstacles[y][x]
        return obstacle is None or obstacle['type'] != 'mountain'

    def get_mountain_positions(self) -> List[Tuple[int, int]]:
        """Returns a list of coordinates for all mountains."""
        return [(x, y) for y in range(self.height) for x in range(self.width) if
                self.obstacles[y][x] and self.obstacles[y][x]['type'] == 'mountain']

    def explore_cell(self, x: int, y: int) -> int:
        """Returns the time taken to explore a cell, considering various obstacles."""
        obstacle = self.obstacles[y][x]
        if obstacle is None:
            return 1  # Time taken to explore an empty cell
        elif obstacle['type'] == 'collapsed_building' and not obstacle.get('explored', False):
            obstacle['explored'] = True  # Mark as explored
            return 3  # Exploring a collapsed building requires more effort
        elif obstacle['type'] == 'mountain':
            return 0  # Mountains are impassable, thus cannot be explored
        return 1  # Default exploration time for any other condition

    def get_recent_need_help_pheromones(self, x: int, y: int, radius: int, age_threshold: int, current_time: int) -> \
            List[Dict]:
        """
        Returns recent 'Need Help' pheromones within a specified radius and age threshold.
        :param x: X-coordinate of the center point
        :param y: Y-coordinate of the center point
        :param radius: Search radius around the (x, y) point
        :param age_threshold: Age threshold for considering a pheromone recent
        :param current_time: Current simulation time for age calculation
        :return: A list of recent 'Need Help' pheromones
        """
        recent_pheromones = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    for pheromone in self.pheromones[ny][nx]:
                        if pheromone['type'] == 'need_help' and current_time - pheromone['timestamp'] <= age_threshold:
                            recent_pheromones.append(pheromone)
        return recent_pheromones

    def check_for_drone_activity(self, x: int, y: int, radius: int) -> bool:
        """Checks for recent drone activity (trail pheromones) within a specified radius."""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if any(pheromone['type'] == 'trail' for pheromone in self.pheromones[ny][nx]):
                        return True
        return False
