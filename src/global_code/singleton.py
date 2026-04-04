
from global_code.helpful_functions import load_config


class State:
    """
    Singleton class for storing the state of the simulation.
    """

    config: dict = load_config()

    def __init__(self):
        self._state = None
