# visualize.py
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from grid import Grid
from drone import Drone


def visualize_grid_save_img(grid: Grid, save_path: str = "./grid_visualization.png") -> None:
    plt.imshow(grid.grid, cmap="viridis")
    plt.colorbar(ticks=[0, 1, 2, 3], label=["Empty", "Obstacle", "Victim", "Safe Zone"])
    plt.savefig(save_path)  # Save the figure instead of showing it
    print(f"Grid visualization saved to {save_path}")


def visualize_grid(grid: Grid, drones: List[Drone]) -> None:
    # Create a figure and axis for the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Display the grid
    # Note: Adjust the color map and normalization for your specific grid values and pheromone intensity levels
    cmap = plt.cm.viridis
    norm = plt.Normalize(0, 3)  # Assuming grid values are in the range 0-3 for empty, obstacle, victim, safe zone
    ax.imshow(grid.grid, cmap=cmap, norm=norm)

    # Overlay pheromones, assuming they have an intensity that can modify their transparency or color
    for y in range(grid.height):
        for x in range(grid.width):
            for pheromone in grid.get_pheromones(x, y):
                if pheromone['type'] == 'Area Cleared':
                    circle = plt.Circle((x, y), 0.3, color='blue', alpha=min(pheromone['intensity'], 1))
                    ax.add_artist(circle)
                elif pheromone['type'] == 'Need Help':
                    circle = plt.Circle((x, y), 0.3, color='red', alpha=min(pheromone['intensity'], 1))
                    ax.add_artist(circle)

    # Plot drones
    drone_x = [drone.position[0] for drone in drones]
    drone_y = [drone.position[1] for drone in drones]
    ax.scatter(drone_x, drone_y, s=100, c='yellow', label='Drones')

    # Customize the plot
    ax.set_xticks(np.arange(-.5, grid.width, 1), minor=True)
    ax.set_yticks(np.arange(-.5, grid.height, 1), minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", size=0)
    plt.legend()

    # Show the plot
    plt.show()
