# grid.py
import numpy as np
from typing import List, Tuple, Dict

class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.grid: np.ndarray = np.zeros((height, width), dtype=int)
        # Initialize a structure to hold obstacle information
        self.obstacles: np.ndarray = np.empty((height, width), dtype=object)
        for y in range(height):
            for x in range(width):
                # Each cell starts with no obstacle
                self.obstacles[y, x] = None
        # Adding a pheromone layer, where each cell can hold multiple pheromones
        self.pheromones: np.ndarray = np.empty((height, width), dtype=object)
        for y in range(height):
            for x in range(width):
                self.pheromones[y, x] = []

    def add_obstacle(self, x: int, y: int) -> None:
        self.grid[y][x] = 1

    def add_victim(self, x: int, y: int) -> None:
        self.grid[y][x] = 2

    def add_safe_zone(self, x: int, y: int) -> None:
        self.grid[y][x] = 3

    def is_obstacle(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def is_victim(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 2

    def is_safe_zone(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 3

    def get_pheromones(self, x: int, y: int) -> List[Dict]:
        """Returns a list of pheromones in the specified location."""
        return self.pheromones[y, x]

    def add_pheromone(self, x: int, y: int, pheromone_type: str, message: str, timestamp: int, intensity: float = 1.0) -> None:
        """Adds a pheromone with an intensity that can decay over time."""
        self.pheromones[y, x].append({
            'type': pheromone_type,
            'message': message,
            'timestamp': timestamp,
            'intensity': intensity
        })

    def age_pheromones(self, current_time: int, decay_rate: int, decay_function=lambda x: x - 0.1) -> None:
        """Ages pheromones based on the current time, reducing their intensity according to the decay_function."""
        for y in range(self.height):
            for x in range(self.width):
                updated_pheromones = []
                for pheromone in self.pheromones[y, x]:
                    age = current_time - pheromone['timestamp']
                    new_intensity = decay_function(pheromone['intensity']) * (1 - age / decay_rate)
                    if new_intensity > 0:  # Only keep pheromones with positive intensity
                        pheromone['intensity'] = new_intensity
                        updated_pheromones.append(pheromone)
                self.pheromones[y, x] = updated_pheromones

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

    def explore_cell(self, x: int, y: int) -> int:
        """Returns the time taken to explore a cell. Mountains can't be explored."""
        obstacle = self.obstacles[y][x]
        if obstacle is None:
            return 1  # Time taken to explore an empty cell
        elif obstacle['type'] == 'collapsed_building' and not obstacle['explored']:
            obstacle['explored'] = True  # Mark as explored
            return 3  # Arbitrary time, adjust based on your simulation's scale
        return 0  # For mountains, or if a collapsed building was already explored
