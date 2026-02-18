# Disaster Recovery Drone Simulation

An AI-powered drone swarm simulation built with **CrewAI** and **Claude/GPT** LLMs. Autonomous drone agents coordinate search-and-rescue operations across a 100×100 grid using emergent pheromone-based communication — no direct drone-to-drone messaging.

## How It Works

Each drone is a CrewAI agent. Every simulation tick, a drone:
1. **Perceives** — reads the 8 adjacent cells (obstacles, victims, safe zones) and scans pheromone counts in a 10-cell radius around itself
2. **Decides** — the LLM receives a dynamic prompt containing the drone's perceptions and nearby pheromone counts, then chooses one movement action and optionally emits a pheromone
3. **Acts** — moves to the target cell, then explores it (rescuing victims or surveying collapsed buildings)

Pheromones decay exponentially over time (`intensity * 0.9^(age/decay_rate)`), so signals from long ago fade naturally without cleanup logic.

### Pheromone Types

| Pheromone | Color | Meaning |
|-----------|-------|---------|
| `need_help` | Cyan | Multiple victims or impassable obstacles nearby — other drones should converge |
| `area_cleared` | Pink | Surrounding area is safe and secured |
| `trail` | — | Breadcrumb left on every move (used to detect recent drone activity) |

### Grid Elements

| Element | Value | Behavior |
|---------|-------|----------|
| Empty | 0 | Passable, no cost |
| Mountain | 1 (obstacle) | **Impassable** — drones cannot enter |
| Victim | 2 | Drone rescues in 5 time units, cell becomes safe zone |
| Safe zone | 3 | Previously cleared cell |
| Collapsed building | obstacle metadata | Passable; takes 3 time units to explore |

### Visualization

The simulation produces `files/animation.mp4`:

- **Red** — drones
- **Brown** — mountains (impassable)
- **Green** — safe zones (rescued victims or explored buildings)
- **Cyan** — `need_help` pheromone locations
- **Pink** — `area_cleared` pheromone locations

## Setup

### Prerequisites

- Docker and Docker Compose, **or** Python 3.11+ with FFmpeg installed

### Configuration

Create `config.yaml` in the project root (this file is git-ignored):

```yaml
ANTHROPIC_API_KEY: your_anthropic_key_here
OPENAI_API_KEY: your_openai_key_here
OPENAI_MODEL_NAME: gpt-3.5-turbo-1106
```

The LLM used by each drone defaults to `gpt-3.5-turbo-1106`. To switch to Claude Haiku, change the `llm` parameter in `drone.py:agent_main()`.

### Run with Docker (recommended)

```bash
docker-compose up --build
```

### Run manually

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/idk_some_code/main.py
```

Output is saved to `files/animation.mp4`.

### Run tests

```bash
# Docker
docker-compose -f docker-compose.tests.yml up --build

# Manual
pytest src/tests/
```

## Simulation Parameters

All hardcoded in `src/idk_some_code/main.py:main()`:

| Parameter | Value |
|-----------|-------|
| Grid size | 100 × 100 |
| Drones | 4 (start clustered near center) |
| Victims | 300 |
| Collapsed buildings | 500 |
| Mountains | 50 |
| Time steps | 300 frames |
| Animation FPS | 30 |

## Project Structure

```
src/
├── idk_some_code/
│   ├── main.py          # Entry point, visualization, simulation loop
│   ├── drone.py         # Drone agent + CrewAI tools
│   └── grid.py          # Environment model and pheromone system
└── global_code/
    ├── singleton.py     # Config loader (reads config.yaml)
    └── helpful_functions.py
```

## License

See [LICENSE](LICENSE).
