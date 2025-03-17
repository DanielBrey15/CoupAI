from enum import Enum

class ActionType(Enum):
    Move = 1
    Block = 2
    CallOut = 3
    LoseCard = 4
    SwitchCard = 5

    def __str__(self):
        return self.name.capitalize()