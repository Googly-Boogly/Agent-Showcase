# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A disaster recovery drone swarm simulation showcasing agentic behaviors. Autonomous drones navigate a 100x100 grid environment, coordinating via pheromone-based communication (not direct messaging) to locate and assist victims. Built on **CrewAI 1.13.0** and **OpenAI (gpt-5-mini)**.

## Commands

### Run the simulation
```bash
# Docker (recommended)
docker-compose up --build

# Manual
python src/idk_some_code/main.py
```

### Run tests
```bash
# Docker
docker-compose -f docker-compose.tests.yml up --build

# Manual
pytest src/tests/

# Single test file
pytest src/tests/test_drone.py
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Requirements
- Python 3.11+
- FFmpeg (for MP4 animation output)
- `config.yaml` in project root (git-ignored) with API keys

## Configuration

Create `config.yaml` in the project root:
```yaml
ANTHROPIC_API_KEY: your_key_here
OPENAI_API_KEY: your_key_here
OPENAI_MODEL_NAME: gpt-5-mini
```

This is loaded by `src/global_code/singleton.py` (`State` singleton) and injected into environment variables at startup.

## Architecture

### Simulation Flow (`src/idk_some_code/main.py`)
The main loop is driven by `matplotlib.animation.FuncAnimation` (300 frames). Each frame calls `update_visualization()`, which:
1. Runs `drone.agent_main()` for all drones **in parallel** via `ThreadPoolExecutor` (LLM decision + movement)
2. Calls `drone.explore_current_cell(frame)` sequentially for each drone (victim rescue / building exploration)
3. Calls `grid.age_pheromones(frame)` to decay pheromone intensities

Output: `files/animation.mp4` (30 fps via FFmpeg)

### Grid (`src/idk_some_code/grid.py`)
- 100×100 numpy array indexed as `grid[y][x]`: 0=empty, 1=obstacle, 2=victim, 3=safe_zone
- **Important**: all grid structures use `[y][x]` ordering, not `[x][y]`
- `obstacles` is a 2D list (not numpy) storing dicts: `{'type': 'mountain'}` or `{'type': 'collapsed_building', 'explored': bool}`
- Mountains (`type='mountain'`) are **impassable**; collapsed buildings are passable but cost 3 time units to explore
- `pheromones` is a 3D list of dicts: `{'type', 'message', 'timestamp', 'intensity'}`
- Pheromone decay: `intensity * 0.9^(age/decay_rate)` — pheromones are removed when intensity reaches 0
- `get_pheromones_square(position, visibility=10)` returns pheromones bucketed by relative cardinal direction

### Drone Agent (`src/idk_some_code/drone.py`)
- `agent_main()` creates a **new CrewAI Agent + Task + Crew per timestep** — no persistent CrewAI agent state between ticks
- **Current LLM**: `gpt-5-mini` — set via `llm="gpt-5-mini"` in the Agent constructor
- `max_iter=3`, `max_execution_time=10` — no artificial sleep delay
- **Persistent memory**: `action_history` list records what the drone did each tick; last 10 entries are injected into the LLM prompt for cross-tick continuity
- **Anti-stuck logic**: `is_stuck()` detects oscillation (same 2 cells in last 6 moves); `get_unvisited_directions()` suggests new paths; if the LLM fails to unstick, a hard override forces movement to an unvisited cell
- `drone_state['perceptions']`: adjacent cells only (visibility=1), updated by `update_perceptions()`
- Pheromone awareness: `get_pheromones_square()` with visibility=10 in `agent_main()`
- Pheromone cooldowns: 30 time units for both `need_help` and `area_cleared`
- `assess_and_act()` is legacy random-movement code, replaced by `agent_main()`
- CrewAI `memory=True` enabled on the Crew for within-tick short-term memory

### CrewAI Tools (`src/idk_some_code/agent_tools.py`)
Six `BaseTool` subclasses (from `crewai.tools`) hold a reference to their parent `Drone` instance: `MoveEastTool`, `MoveWestTool`, `MoveNorthTool`, `MoveSouthTool`, `EmitNeedHelpTool`, `EmitAreaClearedTool`. They are instantiated fresh each tick inside `agent_main()`.

### Key Design Pattern
Drones coordinate **emergently** through pheromones on the grid — there is no direct drone-to-drone messaging. The LLM reads pheromone context in its prompt and decides how to respond.

## Gotchas

- Grid indexing is `[y][x]` everywhere — mixing this up causes silent out-of-bounds bugs
- The `simulate_disaster_response()` function in `main.py` is unused; actual execution goes through `FuncAnimation` → `update_visualization()`
- `config.yaml` must exist before import — `singleton.py` loads it at module import time, not lazily
- Drone `agent_main()` runs in parallel via threads — grid writes (pheromone append) are safe under Python's GIL, but avoid adding non-thread-safe grid mutations

## Simulation Parameters (hardcoded in `main.py:main()`)
- Grid: 100×100
- Drones: 4 (spawned within ±2 cells of center)
- Victims: 300
- Collapsed buildings: 500
- Mountains: 50
- Time steps (frames): 300
