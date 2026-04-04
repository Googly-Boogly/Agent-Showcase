# Disaster Recovery Drone Simulation

An AI-powered drone swarm simulation built with **CrewAI 1.13.0** and **gpt-5-mini**. Autonomous drone agents coordinate search-and-rescue operations across a 100×100 grid using emergent pheromone-based communication — no direct drone-to-drone messaging.

## How It Works

Each drone is a CrewAI agent. Every simulation tick, all drones run **in parallel**:

1. **Perceives** — reads the 8 adjacent cells (obstacles, victims, safe zones) and scans pheromone counts in a 10-cell radius
2. **Remembers** — the last 10 actions from `action_history` are injected into the LLM prompt for cross-tick continuity
3. **Decides** — the LLM receives a dynamic prompt with perceptions, nearby pheromone counts, and memory, then chooses one movement action and optionally emits a pheromone
4. **Acts** — moves to the target cell, then explores it (rescuing victims or surveying collapsed buildings)

If a drone gets stuck oscillating between the same cells, it receives a `CRITICAL WARNING` in its prompt with suggested unvisited directions. If the LLM still doesn't escape, a hard override forces movement to an unvisited cell.

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

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for full setup instructions.

### Quick Start

1. Create `config.yaml` in the project root:
   ```yaml
   ANTHROPIC_API_KEY: your_anthropic_key_here
   OPENAI_API_KEY: your_openai_key_here
   OPENAI_MODEL_NAME: gpt-5-mini
   ```

2. Run with Docker:
   ```bash
   docker-compose up --build
   ```

   Or manually:
   ```bash
   pip install -r requirements.txt
   python src/idk_some_code/main.py
   ```

Output is saved to `files/animation.mp4`.

### Run Tests

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
| Drones | 4 (start clustered near center, run in parallel) |
| Victims | 300 |
| Collapsed buildings | 500 |
| Mountains | 50 |
| Time steps | 300 frames |
| Animation FPS | 30 |

## Project Structure

```
src/
├── idk_some_code/
│   ├── main.py          # Entry point, FuncAnimation loop, parallel execution
│   ├── drone.py         # Drone agent: perception, memory, anti-stuck logic
│   ├── agent_tools.py   # CrewAI BaseTool subclasses (6 tools)
│   └── grid.py          # Environment model and pheromone system
└── global_code/
    ├── singleton.py     # Config loader (reads config.yaml at import time)
    └── helpful_functions.py  # load_config, logging utilities
docs/
├── ARCHITECTURE.md      # Detailed architecture and data flow
├── INSTALLATION.md      # Setup and LLM configuration guide
└── PHEROMONES.md        # Pheromone system internals
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — execution flow, data structures, thread safety
- [Pheromones](docs/PHEROMONES.md) — pheromone types, decay, emergent coordination
- [Installation](docs/INSTALLATION.md) — setup, LLM switching

## License

See [LICENSE](LICENSE).
