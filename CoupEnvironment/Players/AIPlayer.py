from Objects.Move import Move
from Objects.MoveWithTarget import MoveWithTarget
from Objects.Card import Card
from Objects.Action import Action
from Objects.ActionType import ActionType
from Players.Player import Player
import random
from typing import Optional, List

class AIPlayer(Player):
    def __init__(self, card1: Card, card2: Card, id: int = 1, isTraining = False, name: str = "cg32"):
        super().__init__(id = id, name = name, card1 = card1, card2 =card2)
        self.isAI: bool = True
        self.isTraining = isTraining

    def makeMove(self, players: list[Player], actionLog: list[Action]) -> MoveWithTarget:
        #Greedy: Gain coins until enough to coup/assassinate
        if self.numCoins >= 10:
            numAliveOpps = len([p for p in players if p.id != self.id and p.numCards > 0])
            if numAliveOpps == 1:
                return MoveWithTarget.COUPPLAYER1
            elif numAliveOpps == 2:
                return random.choice([MoveWithTarget.COUPPLAYER1, MoveWithTarget.COUPPLAYER2])
            return random.choice([MoveWithTarget.COUPPLAYER1, MoveWithTarget.COUPPLAYER2, MoveWithTarget.COUPPLAYER3])
        elif self.cards.__contains__(Card.ASSASSIN) and self.numCoins >= 3:
            numAliveOpps = len([p for p in players if p.id != self.id and p.numCards > 0])
            if numAliveOpps == 1:
                return random.choice([MoveWithTarget.ASSASSINATEPLAYER1, MoveWithTarget.INCOME])
            elif numAliveOpps == 2:
                return random.choice([MoveWithTarget.ASSASSINATEPLAYER1, MoveWithTarget.ASSASSINATEPLAYER2])
            return random.choice([MoveWithTarget.ASSASSINATEPLAYER1, MoveWithTarget.ASSASSINATEPLAYER2, MoveWithTarget.ASSASSINATEPLAYER3])
        elif self.cards.__contains__(Card.AMBASSADOR):
            return MoveWithTarget.EXCHANGE
        elif self.cards.__contains__(Card.DUKE):
            return MoveWithTarget.TAX
        else:
            return MoveWithTarget.INCOME

    def AIBlock(self, playerMoving, move, target) -> Optional[Card]:
        # AI will block if they can truthfully
        if target == self:
            if move == Move.ASSASSINATE and self.hasCard(Card.CONTESSA):
                return Card.CONTESSA
            elif move == Move.STEAL and self.hasCard(Card.AMBASSADOR):
                return Card.AMBASSADOR
            elif move == Move.STEAL and self.hasCard(Card.CAPTAIN):
                return Card.CAPTAIN
        elif playerMoving != self and move == Move.FOREIGNAID and self.hasCard(Card.DUKE):
            return Card.DUKE
        return None

    def hasCard(self, card) -> bool:
        return card in self.cards

    def hasTwoOfCard(self, card) -> bool:
        if self.getNumCards() == 2:
            return self.cards[0] == card and self.cards[1] == card
        else: 
            return False
        
    def chooseCardToDie(self) -> Card:
        if self.hasCard(Card.CONTESSA):
            return Card.CONTESSA
        if self.hasCard(Card.CAPTAIN):
            return Card.CAPTAIN
        if self.hasCard(Card.AMBASSADOR):
            return Card.AMBASSADOR
        if self.hasCard(Card.ASSASSIN):
            return Card.ASSASSIN
        return Card.DUKE
    
    def resolveExchange(self, exchangeCards: list[Card], game) -> list[Card]:
        cardsInHand = self.getCards()
        cardsInHand.extend(exchangeCards)
        print(f"Cards in hand: {', '.join(str(card) for card in cardsInHand)}")
        returnedCards = cardsInHand
        cardsKept = self.chooseExchangeCards(cardsInHand, game)
        for card in cardsKept:
            returnedCards.remove(card)
        if len(returnedCards) != 2:
            raise ValueError("Should return 2 cards")
        else:
            print(f"{self.getName()} keeps {', '.join(str(card) for card in cardsKept)}")
            self.cards = cardsKept
            return returnedCards

    def chooseExchangeCards(self, exchangeCards: list[Card], game) -> list[Card]:
        cardsKept = []
        if Card.DUKE in exchangeCards:
            cardsKept.append(Card.DUKE)
        if Card.CAPTAIN in exchangeCards and len(cardsKept) < self.getNumCards():
            cardsKept.append(Card.CAPTAIN)
        if Card.AMBASSADOR in exchangeCards and len(cardsKept) < self.getNumCards():
            cardsKept.append(Card.AMBASSADOR)
        if Card.ASSASSIN in exchangeCards and len(cardsKept) < self.getNumCards():
            cardsKept.append(Card.ASSASSIN)
        if Card.CONTESSA in exchangeCards and len(cardsKept) < self.getNumCards():
            cardsKept.append(Card.CONTESSA)
        if len(cardsKept) != self.getNumCards():
            raise ValueError(f"Cards kept not equal to numcards: {self.getNumCards()}")
        return cardsKept
    
    def callsActionOut(self) -> bool:
        return False
        #return random.random() < 0.05