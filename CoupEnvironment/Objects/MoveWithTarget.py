from enum import IntEnum

class MoveWithTarget(IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    COUP_PLAYER_1 = 2
    COUP_PLAYER_2 = 3
    COUP_PLAYER_3 = 4
    TAX = 5
    STEAL_PLAYER_1 = 6
    STEAL_PLAYER_2 = 7
    STEAL_PLAYER_3 = 8
    ASSASSINATE_PLAYER_1 = 9
    ASSASSINATE_PLAYER_2 = 10
    ASSASSINATE_PLAYER_3 = 11
    EXCHANGE = 12

    def __str__(self):
        return self.name.capitalize()