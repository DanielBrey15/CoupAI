from enum import Enum

class Move(Enum):
    INCOME = 1
    FOREIGNAID = 2
    COUP = 3
    TAX = 4
    STEAL = 5
    ASSASSINATE = 6
    EXCHANGE = 7

    def __str__(self):
        return self.name.capitalize()