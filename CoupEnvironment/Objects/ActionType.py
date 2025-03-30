from enum import Enum

class ActionType(Enum):
    MOVE = 1
    BLOCK = 2
    CALL_OUT = 3
    LOSE_CARD = 4
    SWITCH_CARD = 5

    def __str__(self):
        return self.name.capitalize()