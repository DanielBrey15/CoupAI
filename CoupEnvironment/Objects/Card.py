from enum import Enum

class Card(Enum):
    DUKE = 1
    CAPTAIN = 2
    ASSASSIN = 3
    CONTESSA = 4
    AMBASSADOR = 5

    def __str__(self):
        return self.name.capitalize()