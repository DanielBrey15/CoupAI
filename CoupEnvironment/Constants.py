from Objects.Move import Move, MoveWithTarget

class Constants:
    ONEHOTENCODEDSTATETOWINGAME = [
        0,1,0,
        0,1,0,
        1,0,0,
        1,0,0,
        0,0,0,0,1,
        0,1,0,0,0,
        0,0,1,0,0,
        1,0,0,0,0,
    ]

    ACTIONMASKFORSTATETOWINGAME = [1,1,1,0,0,1,1,0,0,1,0,0,1]

    POLICYLOSSMULTIPLERBYRANKDICTIONARY = {
        1: -2,
        2: -1,
        3: 2,
        4: 3
    }

    LISTOFKILLMOVES= [
        MoveWithTarget.COUPPLAYER1,
        MoveWithTarget.COUPPLAYER2,
        MoveWithTarget.COUPPLAYER3,
        MoveWithTarget.ASSASSINATEPLAYER1,
        MoveWithTarget.ASSASSINATEPLAYER2,
        MoveWithTarget.ASSASSINATEPLAYER3,
    ]

    NUMBEROFCOINSTOSTATEBRACKETMAPPING = {
        # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
        # Note: It's impossible to have over 13 coins
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
        12: 4,
        13: 4
    }