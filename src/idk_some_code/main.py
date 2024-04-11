# main.py
from idk_some_code.drone import Drone
import numpy as np
from idk_some_code.grid import Grid
from typing import List, Tuple
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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
            # Example simple behavior: Move randomly, then assess and act.
            direction = np.random.choice(["up", "down", "left", "right"])
            drone.move(direction)
            drone.assess_and_act(current_time)

            # Example of aging pheromones at a fixed rate, assuming a decay rate of 100 time units
            grid.age_pheromones(current_time, 100)

        # Optional: Add a call to a visualization function here to see the grid state


def main():
    grid_size = (100, 100)
    num_drones = 4
    grid = Grid(*grid_size)

    # Assuming functions to initialize mountains, safe zones, and possibly victims are available
    initialize_obstacles(grid, num_mountains=10, num_buildings=10)  # Placeholder function

    start_position = (grid.width // 2, grid.height // 2)  # Calculate grid center
    drones = [Drone(grid, start_position) for _ in range(num_drones)]

    fig, ax = plt.subplots()
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.set_facecolor('black')

    # Plot mountains and safe zones
    mountain_positions = np.array(grid.get_mountain_positions())  # Placeholder method
    if mountain_positions.size > 0:
        ax.scatter(mountain_positions[:, 0], mountain_positions[:, 1], s=100, color='brown', label='Mountains', zorder=1)

    drone_positions = np.array([drone.position for drone in drones])
    drone_scatter = ax.scatter(drone_positions[:, 0], drone_positions[:, 1], s=100, color='red', label='Drones', zorder=3)

    # Initialize safe zone visualization
    safe_zone_positions = np.array(grid.get_safe_zone_positions())
    if safe_zone_positions.size > 0:
        safe_zone_scatter = ax.scatter(safe_zone_positions[:, 0], safe_zone_positions[:, 1], s=100, color='green',
                                       label='Safe Zones', zorder=2)
    else:
        safe_zone_scatter = ax.scatter([], [], s=100, color='green', label='Safe Zones', zorder=2)

    drone_legend = plt.Line2D([0], [0], linestyle="none", c="red", marker='o')
    mountain_legend = plt.Line2D([0], [0], linestyle="none", c="brown", marker='o')
    safe_zone_legend = plt.Line2D([0], [0], linestyle="none", c="green", marker='o')
    ax.legend([drone_legend, mountain_legend, safe_zone_legend], ["Drones", "Mountains", "Safe Zones"], numpoints=1)

    def update(frame):
        # Update drone positions based on their logic
        for drone in drones:
            drone.assess_and_act(frame)  # Now correctly passing the current time

        # Update drone positions on the plot
        drone_positions = np.array([drone.position for drone in drones])
        drone_scatter.set_offsets(drone_positions)

        # Fetch and update safe zone positions
        safe_zone_positions = np.array(grid.get_safe_zone_positions())
        if len(safe_zone_positions) > 0:
            safe_zone_scatter.set_offsets(safe_zone_positions)
        else:
            # Handle case where there are no safe zones or safe_zone_scatter is not set up correctly
            print("No safe zones to display or scatter not initialized.")

        return drone_scatter, safe_zone_scatter,

    ani = FuncAnimation(fig, update, frames=np.arange(100), blit=True)

    # Save the animation
    ani.save('files/animation.mp4', writer='ffmpeg', fps=30)

    total_explored_area = grid.explored_cells
    total_time_spent = sum(drone.time_spent for drone in drones)

    print(f"Total area explored: {total_explored_area} cells")
    print(f"Total time spent by all drones: {total_time_spent} units")


def refined_static_victim_visualization_test():
    grid_size = (100, 100)
    num_victims = 10  # Adjust based on your setup
    grid = Grid(*grid_size)

    # Initialize victims on the grid
    initialize_victims(grid, num_victims)

    # Fetch initial victim positions
    initial_victim_positions = np.array(grid.get_victim_positions())
    print("Refined test - Initial victim positions:", initial_victim_positions)

    # Ensure the data format is correct for Matplotlib
    if initial_victim_positions.size > 0:
        x_positions, y_positions = initial_victim_positions[:, 0], initial_victim_positions[:, 1]
    else:
        x_positions, y_positions = [], []

    fig, ax = plt.subplots()
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.set_facecolor('black')

    # Increase size and adjust color for visibility
    ax.scatter(x_positions, y_positions, s=100, color='cyan', label='Victims')  # Using 'cyan' for better visibility

    plt.legend()

    plt.savefig('files/plot.png')


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
