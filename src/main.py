# main.py
from grid import Grid
from drone import Drone
from visualize import visualize_grid, visualize_grid_save_img
import numpy as np
from grid import Grid
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


def simulate_disaster_response(grid_size: Tuple[int, int], num_drones: int, num_victims: int, simulation_time: int) -> None:
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
    grid_size = (100, 100)  # Example size, adjust as needed
    num_drones = 4
    num_victims = 100  # Assuming you have a number of victims to initialize
    grid = Grid(*grid_size)

    # Initialize victims on the grid
    initialize_victims(grid, num_victims)

    drones = [Drone(grid, (grid.width // 2, grid.height // 2)) for _ in range(num_drones)]

    fig, ax = plt.subplots()
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.set_facecolor('black')

    # Fetch initial victim positions
    initial_victim_positions = np.array(grid.get_victim_positions())
    if initial_victim_positions.size > 0:
        victim_scatter = ax.scatter(initial_victim_positions[:, 0], initial_victim_positions[:, 1], s=100, color='cyan',
                                    label='Victims')
    else:
        victim_scatter = ax.scatter([], [], s=100, color='cyan', label='Victims')

    drone_positions = np.array([drone.position for drone in drones])
    drone_scatter = ax.scatter(drone_positions[:, 0], drone_positions[:, 1], s=100, color='red', label='Drones')
    # Initialize the victim scatter with actual positions
    victim_scatter = ax.scatter(initial_victim_positions[:, 0], initial_victim_positions[:, 1], s=50, color='blue',
                                label='Victims')
    safe_zone_scatter = ax.scatter([], [], s=50, color='green', label='Safe Zones')

    # For victims and safe zones, additional plotting logic will be integrated into the update function.
    def init():
        drone_scatter.set_offsets(np.empty((0, 2)))
        victim_scatter.set_offsets(np.empty((0, 2)))
        safe_zone_scatter.set_offsets(np.empty((0, 2)))
        return drone_scatter, victim_scatter, safe_zone_scatter,

    def update(frame):

        # Update drone positions based on simulation's logic
        for drone in drones:
            direction = np.random.choice(["up", "down", "left", "right"])
            drone.move(direction)
            drone.assess_and_act(frame)

        # Update drone positions on the plot
        drone_positions = np.array([drone.position for drone in drones])
        if len(drone_positions) > 0:  # Check if there are any drones to display
            drone_scatter.set_offsets(drone_positions)
        else:
            drone_scatter.set_offsets(np.empty((0, 2)))  # Avoid errors if no drones

        # Assuming grid is accessible within the update function
        victim_positions = np.array(grid.get_victim_positions())
        if len(victim_positions) > 0:  # Ensure there are victims to display
            victim_scatter.set_offsets(victim_positions)
        else:
            victim_scatter.set_offsets(np.empty((0, 2)))  # No victims to display

        # Get and update safe zone positions
        safe_zone_positions = np.array(grid.get_safe_zone_positions())
        if len(safe_zone_positions) > 0:
            safe_zone_scatter.set_offsets(safe_zone_positions)
        else:
            safe_zone_scatter.set_offsets(np.empty((0, 2)))

        return drone_scatter, victim_scatter, safe_zone_scatter,

    ani = FuncAnimation(fig, update, frames=np.arange(100), init_func=init, blit=False)

    # Save the animation
    ani.save('files/animation.mp4', writer='ffmpeg', fps=30)


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
