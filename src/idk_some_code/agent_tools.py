# agent_tools.py
from typing import Any

from crewai.tools import BaseTool
from pydantic import Field


class MoveEastTool(BaseTool):
    name: str = "Move East"
    description: str = "Tool to move the drone east."
    drone: Any = Field(..., description="Drone instance")

    def __init__(self, drone):
        super().__init__(drone=drone)

    def _run(self) -> str:
        return self.drone.move_right()


class MoveWestTool(BaseTool):
    name: str = "Move West"
    description: str = "Tool to move the drone west."
    drone: Any = Field(..., description="Drone instance")

    def __init__(self, drone):
        super().__init__(drone=drone)

    def _run(self) -> str:
        return self.drone.move_left()


class MoveNorthTool(BaseTool):
    name: str = "Move North"
    description: str = "Tool to move the drone north."
    drone: Any = Field(..., description="Drone instance")

    def __init__(self, drone):
        super().__init__(drone=drone)

    def _run(self) -> str:
        return self.drone.move_up()


class MoveSouthTool(BaseTool):
    name: str = "Move South"
    description: str = "Tool to move the drone south."
    drone: Any = Field(..., description="Drone instance")

    def __init__(self, drone):
        super().__init__(drone=drone)

    def _run(self) -> str:
        return self.drone.move_down()


class EmitNeedHelpTool(BaseTool):
    name: str = "Emit Need Help"
    description: str = "Tool to emit 'Need Help' pheromone to request assistance from other drones."
    drone: Any = Field(..., description="Drone instance")

    def __init__(self, drone):
        super().__init__(drone=drone)

    def _run(self) -> str:
        return self.drone.emit_need_help_tool()


class EmitAreaClearedTool(BaseTool):
    name: str = "Emit Area Cleared"
    description: str = "Tool to emit 'Area Cleared' pheromone to indicate the area is safe."
    drone: Any = Field(..., description="Drone instance")

    def __init__(self, drone):
        super().__init__(drone=drone)

    def _run(self) -> str:
        return self.drone.emit_area_cleared_tool()
