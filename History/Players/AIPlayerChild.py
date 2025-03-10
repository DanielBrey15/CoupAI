from Players.AIPlayer import AIPlayer
from Objects.Card import Card

class AIPlayerChild(AIPlayer):
    def __init__(self, card1: Card, card2: Card, name: str = "cg32"):
        super().__init__(card1, card2, name)