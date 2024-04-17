# main.py
import sys
sys.path.append('/src')

import os

import numpy as np
from typing import List, Tuple
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
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
            # Example simple behavior: Move randomly, then assess and act.
            direction = np.random.choice(["up", "down", "left", "right"])
            drone.move(direction)
            drone.assess_and_act(current_time)

            # Example of aging pheromones at a fixed rate, assuming a decay rate of 100 time units
            grid.age_pheromones(current_time, 100)

        # Optional: Add a call to a visualization function here to see the grid state


def initialize_simulation(grid_size, num_drones, num_mountains, num_buildings):
    """Set up the grid, drones, and obstacles."""
    grid = Grid(*grid_size)
    initialize_obstacles(grid, num_mountains, num_buildings)
    start_position = (grid.width // 2, grid.height // 2)
    drones = [Drone(grid, start_position) for _ in range(num_drones)]
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

    # Simulate drone actions and update positions
    for drone in drones:
        drone.assess_and_act(frame)  # Assuming this method updates the drone's position

    # Update drone positions on the plot
    drone_positions = np.array([drone.position for drone in drones])
    drone_scatter.set_offsets(drone_positions)

    safe_zone_positions = np.array(grid.get_safe_zone_positions())
    safe_zone_scatter.set_offsets(safe_zone_positions)
    # Update visualization for "Need Help" pheromones (similarly update for "Area Cleared" and other pheromones)
    need_help_positions = np.array([
        (x, y) for y in range(grid.height) for x in range(grid.width)
        if any(pheromone['type'] == 'need_help' for pheromone in grid.get_pheromones(x, y))
    ])
    if need_help_positions.size > 0:
        # Need help pheromone emitted
        # print('hello')
        need_help_scatter.set_offsets(need_help_positions)
    else:
        need_help_scatter.set_offsets(np.empty((0, 2)))

    # Similarly update for "Area Cleared" pheromones...
    area_cleared_positions = np.array([
        (x, y) for y in range(grid.height) for x in range(grid.width)
        if any(pheromone['type'] == 'area_cleared' for pheromone in grid.get_pheromones(x, y))
    ])
    if area_cleared_positions.size > 0:
        # print("area cleared pheromone emitted at: ", area_cleared_positions, "at time: ", frame)
        area_cleared_scatter.set_offsets(area_cleared_positions)
    else:
        area_cleared_scatter.set_offsets(np.empty((0, 2)))

    # Don't forget to refresh or update other elements like safe zones if they change over time

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
    # ClaudeHaiku = ChatAnthropic(model="claude-3-haiku-20240307")
    # drone_agent = Agent(
    #     role='Drone in a disaster recovery mission',
    #     goal='Decide the best action based on the current situation',
    #     backstory=f"""
    # You are a world-renowned drone pilot expert deployed in a disaster-struck area to assist in search and rescue operations. Your primary goal is to locate and assist victims while ensuring the area's safety. You can communicate with other drones using pheromones to coordinate efforts.
    # """,
    #     verbose=True,
    #     allow_delegation=False,
    #     tools=[],
    #     llm=ClaudeHaiku
    # )
    # drone_task = Task(
    #     description="""Decide the best action based on the current situation""",
    #     expected_output="Either emit a pheromone and move or just move",
    #     agent=drone_agent
    # )
    # crew = Crew(
    #     agents=[drone_agent],
    #     tasks=[drone_task],
    #     verbose=2,  # You can set it to 1 or 2 to different logging levels
    # )
    # result = crew.kickoff()
    # print(result)
    main()
