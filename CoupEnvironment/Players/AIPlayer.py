import random
from typing import Optional
from Objects.Move import Move
from Objects.MoveWithTarget import MoveWithTarget
from Objects.Card import Card
from Objects.Action import Action
from Players.Player import Player

"""
AIPlayer is a Coup player that uses heuristics to decide what move to make on its turn.
Unlike AIPlayerML, AIPlayer is not trained using the PlayerUpdater service.

The heuristics used in this player are based on a combination of greedy-style playing and
my own playstyle.
"""
class AIPlayer(Player):
    def __init__(self, card1: Card, card2: Card, id: int = 1, name: str = "cg32"):
        super().__init__(id = id, name = name, card1 = card1, card2 =card2)
        self.isAI: bool = True

        # The following properties are solely used for agents using machine learning. Otherwise they're ignored.
        self.is_training = False
        self.model = None
        self.model_file = None

    def makeMove(self, players: list[Player], action_log: list[Action]) -> MoveWithTarget:
        #Greedy: Gain coins until enough to coup/assassinate
        if self.num_coins >= 10:
            num_alive_opps = len([p for p in players if p.id != self.id and p.num_cards > 0])
            if num_alive_opps == 1:
                return MoveWithTarget.COUP_PLAYER_1, 1
            elif num_alive_opps == 2:
                return random.choice([MoveWithTarget.COUP_PLAYER_1, MoveWithTarget.COUP_PLAYER_2]), 1
            return random.choice([MoveWithTarget.COUP_PLAYER_1, MoveWithTarget.COUP_PLAYER_2, MoveWithTarget.COUP_PLAYER_3]), 1
        elif self.cards.__contains__(Card.ASSASSIN) and self.num_coins >= 3:
            num_alive_opps = len([p for p in players if p.id != self.id and p.num_cards > 0])
            if num_alive_opps == 1:
                return random.choice([MoveWithTarget.ASSASSINATE_PLAYER_1, MoveWithTarget.INCOME]), 1
            elif num_alive_opps == 2:
                return random.choice([MoveWithTarget.ASSASSINATE_PLAYER_1, MoveWithTarget.ASSASSINATE_PLAYER_2]), 1
            return random.choice([MoveWithTarget.ASSASSINATE_PLAYER_1, MoveWithTarget.ASSASSINATE_PLAYER_2, MoveWithTarget.ASSASSINATE_PLAYER_3]), 1
        elif self.cards.__contains__(Card.AMBASSADOR):
            return MoveWithTarget.EXCHANGE, 1
        elif self.cards.__contains__(Card.DUKE):
            return MoveWithTarget.TAX, 1
        else:
            return MoveWithTarget.INCOME, 1

    def AIBlock(self, player_moving, move, target) -> Optional[Card]:
        # AI will block if they can truthfully
        if target == self:
            if move == Move.ASSASSINATE and self.hasCard(Card.CONTESSA):
                return Card.CONTESSA
            elif move == Move.STEAL and self.hasCard(Card.AMBASSADOR):
                return Card.AMBASSADOR
            elif move == Move.STEAL and self.hasCard(Card.CAPTAIN):
                return Card.CAPTAIN
        elif player_moving != self and move == Move.FOREIGN_AID and self.hasCard(Card.DUKE):
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
    
    def resolveExchange(self, exchange_cards: list[Card], game) -> list[Card]:
        cards_in_hand = self.getCards()
        cards_in_hand.extend(exchange_cards)
        returned_cards = cards_in_hand
        cards_kept = self.chooseExchangeCards(cards_in_hand, game)
        for card in cards_kept:
            returned_cards.remove(card)
        if len(returned_cards) != 2:
            raise ValueError("Should return 2 cards")
        else:
            self.cards = cards_kept
            return returned_cards

    def chooseExchangeCards(self, exchange_cards: list[Card], game) -> list[Card]:
        cards_kept = []
        if Card.DUKE in exchange_cards:
            cards_kept.append(Card.DUKE)
        if Card.CAPTAIN in exchange_cards and len(cards_kept) < self.getNumCards():
            cards_kept.append(Card.CAPTAIN)
        if Card.AMBASSADOR in exchange_cards and len(cards_kept) < self.getNumCards():
            cards_kept.append(Card.AMBASSADOR)
        if Card.ASSASSIN in exchange_cards and len(cards_kept) < self.getNumCards():
            cards_kept.append(Card.ASSASSIN)
        if Card.CONTESSA in exchange_cards and len(cards_kept) < self.getNumCards():
            cards_kept.append(Card.CONTESSA)
        if len(cards_kept) != self.getNumCards():
            raise ValueError(f"Cards kept not equal to numcards: {self.getNumCards()}")
        return cards_kept
    
    def callsActionOut(self) -> bool:
        return False
