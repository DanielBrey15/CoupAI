class GameLog:
    def __init__(self, gameNum: int, rank: int, numKills: int, policyLoss: float, chanceofCoupInGameWinningState: float, chanceOfAssassinateInGameWinningState: float):
        self.gameNum = gameNum
        self.rank = rank
        self.numKills = numKills
        self.policyLoss = policyLoss
        self.chanceOfCoupInGameWinningState = chanceofCoupInGameWinningState
        self.chanceOfAssasssinateInGameWinningState = chanceOfAssassinateInGameWinningState
