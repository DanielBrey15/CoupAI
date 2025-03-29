from Objects.Move import Move
from Objects.MoveWithTarget import MoveWithTarget
from Objects.Card import Card
from Objects.Action import Action
from Players.Player import Player
import random
from typing import Optional
from Services.PlayerMethods import *
from Models.PolicyNetwork import PolicyNetwork
import os

class AIPlayerML(Player):
    def __init__(self, card1: Card, card2: Card, modelFile: str, id: int = 1, isTraining = False, name: str = "cg32"):
        super().__init__(id = id, name = name, card1 = card1, card2 =card2)
        self.isAI: bool = True
        self.isTraining = isTraining
        self.modelFile = modelFile
        # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
        # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
        self.model = PolicyNetwork(32, 13)
        if os.path.isfile(modelFile):
            self.model.load_state_dict(torch.load(modelFile, weights_only=True)) #"ModelFiles/Model1.pt"

    def makeMove2(self, players: list[Player], actionLog: list[Action]) -> MoveWithTarget:
        #Greedy: Gain coins until enough to coup/assassinate
        if self.numCoins >= 10:
            numOpps = len([p for p in players if p.id != self.id])
            if numOpps == 1:
                return MoveWithTarget.COUPPLAYER1
            elif numOpps == 2:
                return random.choice([MoveWithTarget.COUPPLAYER1, MoveWithTarget.COUPPLAYER2])
            return random.choice([MoveWithTarget.COUPPLAYER1, MoveWithTarget.COUPPLAYER2, MoveWithTarget.COUPPLAYER3])
        elif self.cards.__contains__(Card.ASSASSIN) and self.numCoins >= 3:
            numOpps = len([p for p in players if p.id != self.id])
            if numOpps == 1:
                return MoveWithTarget.ASSASSINATEPLAYER1
            elif numOpps == 2:
                return random.choice([MoveWithTarget.ASSASSINATEPLAYER1, MoveWithTarget.ASSASSINATEPLAYER2])
            return random.choice([MoveWithTarget.ASSASSINATEPLAYER1, MoveWithTarget.ASSASSINATEPLAYER2, MoveWithTarget.ASSASSINATEPLAYER3])
        elif self.cards.__contains__(Card.AMBASSADOR):
            return MoveWithTarget.EXCHANGE
        elif self.cards.__contains__(Card.DUKE):
            return MoveWithTarget.TAX
        else:
            return MoveWithTarget.INCOME
        
    def makeMove(self, players: list[Player], actionLog: list[Action]) -> MoveWithTarget:
        actionMask: list[np.int8] = PlayerMethods.getActionMask(self, players)
        opps = [a for a in players if a.id != self.id]
        opps.sort(key= lambda a: (a.numCards, a.numCoins), reverse = True)
        encodedState = PlayerMethods.getOneHotEncodeState([self, opps[0], opps[1], opps[2]])
        actionList = self.model(encodedState)
        actionList[~torch.tensor(actionMask, dtype=torch.bool)] = float('-inf')
        actionList = F.softmax(actionList, dim=0)
        action = torch.multinomial(actionList, 1).item()
        logActionProb = torch.log1p(actionList[action] - 1)
        return MoveWithTarget(action), logActionProb

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