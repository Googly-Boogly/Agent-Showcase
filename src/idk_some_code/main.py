# main.py
import random
import sys
sys.path.append('/src')

import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from typing import List, Tuple
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

try:
    from global_code.singleton import State
except ImportError:
    from src.global_code.singleton import State

os.environ["ANTHROPIC_API_KEY"] = State.config["ANTHROPIC_API_KEY"]
try:
    from idk_some_code.drone import Drone
except ImportError:
    from drone import Drone
try:
    from idk_some_code.grid import Grid
except ImportError:
    from grid import Grid


def initialize_victims(grid: Grid, num_victims: int) -> None:
    """Randomly places a specified number of victims on the grid."""
    for _ in range(num_victims):
        x, y = np.random.randint(0, grid.width), np.random.randint(0, grid.height)
        while grid.is_obstacle(x, y) or grid.is_victim(x, y):
            x, y = np.random.randint(0, grid.width), np.random.randint(0, grid.height)
        grid.add_victim(x, y)


def simulate_disaster_response(grid_size: Tuple[int, int], num_drones: int, num_victims: int,
                               simulation_time: int) -> None:
    grid = Grid(*grid_size)
    drones: List[Drone] = [Drone(grid, (grid.width // 2, grid.height // 2)) for _ in range(num_drones)]

    initialize_victims(grid, num_victims)

    for current_time in range(simulation_time):
        for drone in drones:
            drone.agent_main()

            grid.age_pheromones(current_time, 100)


def generate_start_positions(center: Tuple[int, int], num_positions: int, spread: int) -> List[Tuple[int, int]]:
    """
    Generate random start positions within a given spread around a center.
    :param center: Central starting position (x, y)
    :param num_positions: Number of positions to generate
    :param spread: The size of the area around the center to generate positions
    :return: List of start positions
    """
    x_center, y_center = center
    return [
        (random.randint(x_center - spread, x_center + spread), random.randint(y_center - spread, y_center + spread))
        for _ in range(num_positions)
    ]

def initialize_simulation(grid_size: Tuple[int, int], num_drones: int, num_mountains: int, num_buildings: int) -> Tuple[Grid, List[Drone]]:
    """
    Set up the grid, drones, and obstacles.
    :param grid_size: Size of the grid (width, height)
    :param num_drones: Number of drones to initialize
    :param num_mountains: Number of mountains to place
    :param num_buildings: Number of buildings to place
    :return: Tuple containing the grid and list of drones
    """
    grid = Grid(*grid_size)
    initialize_obstacles(grid, num_mountains, num_buildings)
    start_position = (grid.width // 2, grid.height // 2)
    drone_positions = generate_start_positions(start_position, num_drones, 2)  # Spread of 2 allows for a 5x5 area
    drones = [Drone(grid, position) for position in drone_positions]
    return grid, drones


def setup_visualization(grid, grid_size, drones):
    """Prepare the matplotlib figure for the simulation."""
    fig, ax = plt.subplots()
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.set_facecolor('black')

    # Plotting mountains
    mountain_positions = np.array(grid.get_mountain_positions())
    if mountain_positions.size > 0:
        ax.scatter(mountain_positions[:, 0], mountain_positions[:, 1], s=100, color='brown', label='Mountains', zorder=1)

    # Plotting drones
    drone_positions = np.array([drone.position for drone in drones])
    drone_scatter = ax.scatter(drone_positions[:, 0], drone_positions[:, 1], s=100, color='red', label='Drones', zorder=4)

    # Initializing placeholders for safe zones, "Need Help", and "Area Cleared" pheromones
    safe_zone_scatter = ax.scatter([], [], s=100, color='green', label='Safe Zones', zorder=2)
    need_help_scatter = ax.scatter([], [], s=50, color='cyan', label='"Need Help" Pheromones', zorder=3)
    area_cleared_scatter = ax.scatter([], [], s=50, color='pink', label='"Area Cleared" Pheromones', zorder=3)

    ax.legend()

    return fig, ax, drone_scatter, safe_zone_scatter, need_help_scatter, area_cleared_scatter


def update_visualization(frame, grid, drones, drone_scatter, safe_zone_scatter, need_help_scatter,
                         area_cleared_scatter):
    """Update function for the animation, refreshing drone positions, safe zones, and pheromones."""

    # Parallel drone decision-making via LLM
    with ThreadPoolExecutor(max_workers=len(drones)) as executor:
        futures = [executor.submit(drone.agent_main) for drone in drones]
        for future in futures:
            future.result()  # Wait for all drones to complete

    # Sequential grid updates (cell exploration and pheromone aging)
    for drone in drones:
        drone.explore_current_cell(frame)
    grid.age_pheromones(frame, 100)

    # Update drone positions on the plot
    drone_positions = np.array([drone.position for drone in drones])
    drone_scatter.set_offsets(drone_positions)

    # Update safe zones
    safe_zone_positions = np.array(grid.get_safe_zone_positions())
    if safe_zone_positions.size > 0:
        safe_zone_scatter.set_offsets(safe_zone_positions)
    else:
        safe_zone_scatter.set_offsets(np.empty((0, 2)))
    # Update visualization for "Need Help" pheromones (similarly update for "Area Cleared" and other pheromones)
    need_help_positions = np.array([
        (x, y) for y in range(grid.height) for x in range(grid.width)
        if any(pheromone['type'] == 'need_help' for pheromone in grid.get_pheromones(x, y))
    ])
    if need_help_positions.size > 0:
        need_help_scatter.set_offsets(need_help_positions)
    else:
        need_help_scatter.set_offsets(np.empty((0, 2)))

    # Similarly update for "Area Cleared" pheromones...
    area_cleared_positions = np.array([
        (x, y) for y in range(grid.height) for x in range(grid.width)
        if any(pheromone['type'] == 'area_cleared' for pheromone in grid.get_pheromones(x, y))
    ])
    if area_cleared_positions.size > 0:
        area_cleared_scatter.set_offsets(area_cleared_positions)
    else:
        area_cleared_scatter.set_offsets(np.empty((0, 2)))

    return drone_scatter, safe_zone_scatter, need_help_scatter, area_cleared_scatter


def main():
    grid_size = (100, 100)
    num_drones = 4
    num_mountains = 50
    num_buildings = 500
    num_victims = 300
    grid, drones = initialize_simulation(grid_size, num_drones, num_mountains, num_buildings)

    initialize_victims(grid, num_victims)
    fig, ax, drone_scatter, safe_zone_scatter, need_help_scatter, area_cleared_scatter = setup_visualization(grid,
                                                                                                             grid_size,
                                                                                                             drones)

    ani = FuncAnimation(fig, update_visualization,
                        fargs=(grid, drones, drone_scatter, safe_zone_scatter, need_help_scatter, area_cleared_scatter),
                        frames=np.arange(300), blit=True)

    ani.save('files/animation.mp4', writer='ffmpeg', fps=30)
    print("Simulation complete and saved.")


def initialize_obstacles(grid: Grid, num_mountains: int, num_buildings: int) -> None:
    """Randomly place mountains and collapsed buildings on the grid."""
    # Add mountains
    for _ in range(num_mountains):
        x, y = np.random.randint(0, grid.width), np.random.randint(0, grid.height)
        grid.add_mountain(x, y)

    # Add collapsed buildings
    for _ in range(num_buildings):
        x, y = np.random.randint(0, grid.width), np.random.randint(0, grid.height)
        while not grid.is_passable(x, y):  # Ensure we don't place a building where a mountain is
            x, y = np.random.randint(0, grid.width), np.random.randint(0, grid.height)
        grid.add_collapsed_building(x, y)


if __name__ == "__main__":
    main()
