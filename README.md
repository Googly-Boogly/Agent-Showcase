# Disaster Recovery Drone Simulation
### Overview

This project simulates a team of drones navigating through a disaster recovery environment. The simulation models drones as agents within a grid, allowing for complex interactions such as pheromone detection, obstacle navigation, and area coverage. It's designed to explore the coordination and efficiency of drone swarms in disaster scenarios.
Components

    main.py: Entry point for running simulations. Coordinates the setup, execution, and visualization of drone activities within the environment.
    grid.py: Defines the simulation's environment. The grid includes features like obstacles and pheromones, simulating real-world conditions the drones may encounter.
    drone.py: Models individual drone behavior. Includes properties such as position and methods for movement and interaction with the grid.
    Dockerfile: Configures the Python environment for running the simulation, ensuring consistency across different setups.
    docker-compose.yml: Facilitates deployment of the simulation, allowing for easy scaling and integration with other services.

Getting Started

    Ensure Docker and Docker Compose are installed on your system.
    Clone the project repository to your local machine.
    Navigate to the project directory and build the Docker container:

    docker-compose up --build

    The simulation will run inside the container, with output and visualizations indicating the drones' performance and behavior within the simulated disaster recovery environment.

### License

Specify your project's license here, which determines how others can use and contribute to your project.