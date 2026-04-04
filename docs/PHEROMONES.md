# Pheromone System

Pheromones are the sole communication channel between drones. There is no direct messaging — drones leave chemical signals on the grid that other drones detect when they pass through the area.

## Pheromone Types

| Type | Emitted By | Meaning | LLM Guidance |
|------|-----------|---------|--------------|
| `trail` | Every move | Marks recent drone path | Used to detect whether an area is already being worked |
| `need_help` | LLM decision | Multiple victims or obstacles nearby | Other drones should converge on this direction |
| `area_cleared` | LLM decision | Surrounding area is secured | Signals `need_help` has been resolved; drones should spread out |

## Data Structure

Each cell holds a list of pheromone dicts:

```python
{
    'type': 'need_help',       # str
    'message': 'Assistance required',  # str
    'timestamp': 42,           # int — simulation tick when emitted
    'intensity': 1.0           # float — starts at 1.0, decays over time
}
```

## Decay

Intensity decays exponentially each tick:

```
new_intensity = intensity * 0.9 ^ (age / decay_rate)
```

With `decay_rate=100`, a pheromone at half-life (~73 ticks) has intensity ≈ 0.5. Pheromones are removed from the list when intensity reaches 0.

`grid.age_pheromones(current_time, decay_rate=100)` is called once per frame in `update_visualization()`.

## Spatial Awareness

Drones read pheromones from a **10-cell radius** around their position, bucketed into 8 cardinal directions (N, S, E, W, NE, NW, SE, SW) via `grid.get_pheromones_square()`. The LLM sees counts per direction per type:

```
North: {'need_help': 2, 'area_cleared': 0}
South: {'need_help': 0, 'area_cleared': 1}
...
```

Trail pheromones are excluded from the LLM prompt (counted but not reported) to reduce noise.

## Emission Cooldowns

To prevent pheromone spam:

| Type | Cooldown |
|------|----------|
| `need_help` | 30 ticks |
| `area_cleared` | 30 ticks |
| `trail` | No cooldown (emitted on every move) |

## Emergent Coordination

Because pheromones decay and drones respond to their directional gradient, the swarm exhibits emergent behaviors without any central planner:

- **Convergence**: A `need_help` signal draws nearby drones toward a victim cluster
- **Spreading**: `area_cleared` signals reduce the attractiveness of already-covered zones, nudging drones outward
- **Path following**: `trail` pheromones let drones sense where others have recently been, enabling loose division of territory
