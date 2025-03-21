from enum import IntEnum

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