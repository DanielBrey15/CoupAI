from Objects.Move import Move
from Objects.Card import Card
from Objects.Action import Action
from Players.Player import Player
from typing import Optional, List

class AIPlayer2(Player):
    def __init__(self, card1: Card, card2: Card, name: str = "cg32"):
        super().__init__(name, card1, card2)
        self.isAI: bool = True

    def makeMove(self, players: list[Player], actionLog: list[Action]) -> Move:
        #Greedy: Gain coins until enough to kill
        if self.numCoins >= 10:
            return Move.COUP
        elif self.cards.__contains__(Card.ASSASSIN) and self.numCoins >= 3:
            return Move.ASSASSINATE
        elif self.cards.__contains__(Card.AMBASSADOR):
            return Move.EXCHANGE
        elif self.cards.__contains__(Card.DUKE):
            return Move.TAX
        else:
            return Move.INCOME

    def acquireTarget(self, players: List[Player]) -> Player:
        return self.findPlayerLeftWithMostCoins(players)

    def findPlayerLeftWithMostCoins(self, players: List[Player]) -> Player:
        playersTargettable = filter(lambda p: len(p.cards) > 0 and p.getName() != self.getName(), players)
        target = None
        targetCoins = -1
        for player in playersTargettable:
            if player.getNumCoins() > targetCoins:
                target = player
                targetCoins = player.getNumCoins()
        return target

    def AIBlock(self, playerMoving, move, target) -> Optional[Card]:
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
        if Card.CAPTAIN in exchangeCards:
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