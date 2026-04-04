# Architecture

## Overview

The simulation runs a 100×100 grid environment with 4 autonomous drone agents. Each drone uses an LLM (via CrewAI) to decide its next action every tick. Drones coordinate indirectly through pheromones left on the grid — there is no direct drone-to-drone messaging.

## Execution Flow

```
main() → FuncAnimation (300 frames)
    └── update_visualization(frame)
            ├── ThreadPoolExecutor
            │     ├── drone[0].agent_main()  ─┐
            │     ├── drone[1].agent_main()   ├─ parallel LLM calls
            │     ├── drone[2].agent_main()   │
            │     └── drone[3].agent_main()  ─┘
            ├── drone[n].explore_current_cell(frame)  (sequential)
            └── grid.age_pheromones(frame)
```

`agent_main()` calls are parallelized across threads. Grid mutation (victim rescue, pheromone aging) is sequential to avoid races.

## Per-Tick Decision Loop (`drone.agent_main`)

1. **Check busy** — if the drone is mid-rescue (5-turn lockout), skip the tick
2. **Update perceptions** — scan 8 adjacent cells for obstacles, victims, safe zones, pheromones
3. **Get pheromone context** — bucket all pheromones within a 10-cell radius into 8 cardinal directions
4. **Anti-stuck check** — detect oscillation; if stuck, inject a CRITICAL WARNING with suggested unvisited directions into the LLM prompt
5. **Build prompt** — assemble backstory with perceptions, pheromone counts, and the last 10 entries from `action_history` (persistent memory)
6. **Run CrewAI crew** — LLM chooses a tool (move or emit pheromone), `max_iter=3`
7. **Hard anti-stuck fallback** — if the LLM didn't move the drone out of an oscillation, force a random unvisited direction
8. **Record action** — append to `action_history` for future ticks

## File Structure

```
src/
├── idk_some_code/
│   ├── main.py          # Entry point, FuncAnimation loop, parallelization
│   ├── drone.py         # Drone class: perception, decision loop, movement
│   ├── agent_tools.py   # CrewAI BaseTool subclasses (6 tools)
│   └── grid.py          # Grid, obstacles, victims, pheromone system
└── global_code/
    ├── singleton.py     # State singleton — loads config.yaml at import time
    └── helpful_functions.py  # load_config, logging utilities
```

## Grid Model (`grid.py`)

The grid has three parallel data structures, all indexed `[y][x]`:

| Structure | Type | Contents |
|-----------|------|----------|
| `grid` | `np.ndarray` (int) | 0=empty, 1=obstacle marker, 2=victim, 3=safe_zone |
| `obstacles` | 2D list of dicts | `None`, `{'type': 'mountain'}`, or `{'type': 'collapsed_building', 'explored': bool}` |
| `pheromones` | 3D list of dicts | `[{'type', 'message', 'timestamp', 'intensity'}, ...]` per cell |

Mountains set both `grid[y][x] = 1` and `obstacles[y][x] = {'type': 'mountain'}`. The `is_passable()` check reads from `obstacles`, not `grid`.

## Agent Tools (`agent_tools.py`)

Six `BaseTool` subclasses, each holding a reference to a `Drone` instance:

| Tool | Action |
|------|--------|
| `MoveNorthTool` | Calls `drone.move_up()` |
| `MoveSouthTool` | Calls `drone.move_down()` |
| `MoveEastTool` | Calls `drone.move_right()` |
| `MoveWestTool` | Calls `drone.move_left()` |
| `EmitNeedHelpTool` | Emits `need_help` pheromone at current position |
| `EmitAreaClearedTool` | Emits `area_cleared` pheromone at current position |

Tools are instantiated fresh each tick inside `agent_main()` and passed to the CrewAI `Agent`. Every movement also emits a `trail` pheromone automatically.

## Anti-Stuck System

Two-layer approach:

1. **Prompt-level**: `is_stuck()` checks the last 6 positions in `visited_cells_history` (maxlen=20). If ≤2 unique positions, the LLM prompt gets a CRITICAL WARNING with `get_unvisited_directions()` output.

2. **Hard fallback**: After the crew runs, if the drone is still stuck and position hasn't changed, `agent_main()` forces `move()` to a random unvisited direction.

## Persistent Memory

`action_history` is a list on each `Drone` that records a one-line entry every tick (position before/after, forced moves). The last 10 entries are injected into the agent backstory as "Recent Action History", giving the LLM cross-tick continuity without a persistent agent object.

CrewAI's `memory=True` on the `Crew` enables within-tick short-term memory for multi-step reasoning.

## Thread Safety

`agent_main()` runs in parallel threads. Safety properties:
- **Grid reads**: multiple threads reading different cells — safe
- **Pheromone appends**: `list.append()` is atomic under Python's GIL — safe
- **Position updates**: each drone writes only its own `self.position` — safe
- **Victim rescue / safe zone marking** (`explore_current_cell`): runs sequentially after all threads complete — safe
