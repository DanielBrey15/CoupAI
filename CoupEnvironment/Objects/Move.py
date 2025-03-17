from enum import Enum, IntEnum

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
    
class MoveWithTarget(IntEnum):
    INCOME = 0
    FOREIGNAID = 1
    COUPPLAYER1 = 2
    COUPPLAYER2 = 3
    COUPPLAYER3 = 4
    TAX = 5
    STEALPLAYER1 = 6
    STEALPLAYER2 = 7
    STEALPLAYER3 = 8
    ASSASSINATEPLAYER1 = 9
    ASSASSINATEPLAYER2 = 10
    ASSASSINATEPLAYER3 = 11
    EXCHANGE = 12

    def __str__(self):
        return self.name.capitalize()