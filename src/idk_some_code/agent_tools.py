from crewai_tools import BaseTool


class MoveEastTool(BaseTool):
    name: str = "Move East"
    description: str = "Tool to move the drone east."

    def __init__(self, drone):
        super().__init__()
        self.drone = drone

    def _run(self):
        self.drone.move_right()
        return "Moved east"


class MoveWestTool(BaseTool):
    name: str = "Move West"
    description: str = "Tool to move the drone west."

    def __init__(self, drone):
        super().__init__()
        self.drone = drone

    def _run(self):
        self.drone.move_left()
        return "Moved West"


class MoveNorthTool(BaseTool):
    name: str = "Move North"
    description: str = "Tool to move the drone north."

    def __init__(self, drone):
        super().__init__()
        self.drone = drone

    def _run(self):
        self.drone.move_up()
        return "Moved north"


class MoveSouthTool(BaseTool):
    name: str = "Move South"
    description: str = "Tool to move the drone south."

    def __init__(self, drone):
        super().__init__()
        self.drone = drone

    def _run(self):
        self.drone.move_down()
        return "Moved south"


class EmitNeedHelpTool(BaseTool):
    name: str = "Emit Need Help"
    description: str = "Tool to emit 'Need Help' pheromone."

    def __init__(self, drone):
        super().__init__()
        self.drone = drone

    def _run(self):
        self.drone.emit_need_help_tool()
        return "Emitted 'Need Help'"


class EmitAreaClearedTool(BaseTool):
    name: str = "Emit Area Cleared"
    description: str = "Tool to emit 'Area Cleared' pheromone."

    def __init__(self, drone):
        super().__init__()
        self.drone = drone

    def _run(self):
        self.drone.emit_area_cleared_tool()
        return "Emitted 'Area Cleared'"