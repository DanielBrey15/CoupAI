from Players.AIPlayer import AIPlayer
from Objects.Card import Card
from enum import Enum
from random import Random

class RiskScore(Enum):
    NoRisk = 1
    LowRisk = 2
    MediumRisk = 3
    HighRisk = 4
    SuperHighRisk = 5

class AIPlayerWithRiskScores(AIPlayer):
    def __init__(self, card1: Card, card2: Card, LieRisk: RiskScore, CallOutRisk: RiskScore, name: str = "cg32"):
        super().__init__(card1, card2, name)
        self.lieRisk = LieRisk
        self.callOutRisk = CallOutRisk

    # def callsActionOut(self):
    #     randomChance = Random.random
    #     return RiskScore

    
