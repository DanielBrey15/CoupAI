from Objects.Move import Move
from Objects.MoveWithTarget import MoveWithTarget

"""
Constants is a class that provides various constants that are used throughout
my Coup AI program.
"""
class Constants:
    ONE_HOT_ENCODED_STATE_TO_WIN_GAME = [
        0,1,0, # Player 1 has 1 card left
        0,1,0, # Player 2 has 1 card left
        1,0,0, # Player 3 has 0 cards left
        1,0,0, # Player 4 has 0 cards left
        0,0,0,0,1, # Player 1 has at least 7 coins
        0,1,0,0,0, # Player 2 has 1 coin (should be insignificant)
        0,0,1,0,0, # Player 3 has 2 coins (should be insignificant)
        1,0,0,0,0, # Player 4 has 0 coins (should be insignificant)
    ]

    ACTION_MASK_FOR_STATE_TO_WIN_GAME = [1,1,1,0,0,1,1,0,0,1,0,0,1]

    POLICY_LOSS_MULTIPLIER_BY_RANK_DICTIONARY = {
        1: -2,
        2: -1,
        3: 2,
        4: 3
    }

    LIST_OF_KILL_MOVES= [
        MoveWithTarget.COUP_PLAYER_1,
        MoveWithTarget.COUP_PLAYER_2,
        MoveWithTarget.COUP_PLAYER_3,
        MoveWithTarget.ASSASSINATE_PLAYER_1,
        MoveWithTarget.ASSASSINATE_PLAYER_2,
        MoveWithTarget.ASSASSINATE_PLAYER_3,
    ]

    NUMBER_OF_COINS_TO_STATE_BRACKET_MAPPING = {
        # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
        # Note: It's impossible to have over 12 coins
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 3,
        5: 3,
        6: 3,
        7: 4,
        8: 4,
        9: 4,
        10: 4,
        11: 4,
        12: 4
    }