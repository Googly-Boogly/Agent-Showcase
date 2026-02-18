# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A disaster recovery drone swarm simulation showcasing agentic behaviors. Autonomous drones navigate a 100x100 grid environment, coordinating via pheromone-based communication (not direct messaging) to locate and assist victims. Built on **CrewAI** and **Claude AI (Anthropic)**.

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
OPENAI_MODEL_NAME: gpt-3.5-turbo-1106
```

This is loaded by `src/global_code/singleton.py` (`State` singleton) and injected into environment variables at startup.

## Architecture

### Simulation Flow (`src/idk_some_code/main.py`)
The main loop is driven by `matplotlib.animation.FuncAnimation` (300 frames). Each frame calls `update_visualization()`, which calls `drone.agent_main()` for each drone. `explore_current_cell()` is called inside `agent_main()` implicitly through the drone's action; pheromone aging is handled per tick.

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
- `agent_main()` creates a **new CrewAI Agent + Task + Crew per timestep** — there is no persistent agent state between ticks
- **Current LLM**: `gpt-3.5-turbo-1106` (the `llm=self.ClaudeHaiku` line is commented out). To switch, set the `llm` param in `agent_main()`.
- `max_iter=3`, `max_execution_time=2`, plus a hard `time.sleep(3)` after each crew kickoff — each drone takes ~5+ seconds per tick
- `drone_state['perceptions']`: adjacent cells only (visibility=1), updated by `update_perceptions()`
- Pheromone awareness: `get_pheromones_square()` with visibility=10 in `agent_main()`
- Pheromone cooldowns: 30 time units for both `need_help` and `area_cleared`
- `assess_and_act()` is legacy random-movement code, replaced by `agent_main()`

### CrewAI Tools (defined at bottom of `drone.py`)
Six `BaseTool` subclasses hold a reference to their parent `Drone` instance: `MoveEastTool`, `MoveWestTool`, `MoveNorthTool`, `MoveSouthTool`, `EmitNeedHelpTool`, `EmitAreaClearedTool`. They are instantiated fresh each tick inside `agent_main()`.

### Key Design Pattern
Drones coordinate **emergently** through pheromones on the grid — there is no direct drone-to-drone messaging. The LLM reads pheromone context in its prompt and decides how to respond.

## Gotchas

- Grid indexing is `[y][x]` everywhere — mixing this up causes silent out-of-bounds bugs
- The `simulate_disaster_response()` function in `main.py` is unused; actual execution goes through `FuncAnimation` → `update_visualization()`
- `time.sleep(3)` in `drone.py:agent_main()` makes real-time simulation very slow; remove or reduce it for faster iteration during development
- `config.yaml` must exist before import — `singleton.py` loads it at module import time, not lazily

## Simulation Parameters (hardcoded in `main.py:main()`)
- Grid: 100×100
- Drones: 4 (spawned within ±2 cells of center)
- Victims: 300
- Collapsed buildings: 500
- Mountains: 50
- Time steps (frames): 300
