import os
import random
from typing import Optional
from Objects.Move import Move
from Objects.MoveWithTarget import MoveWithTarget
from Objects.Card import Card
from Objects.Action import Action
from Players.Player import Player
from Services.PlayerMethods import *
from Models.PolicyNetwork import PolicyNetwork

"""
AIPlayerML is a Coup player that uses deep learning to decide what move to make on its turn.
Using the PlayerUpdater service, AIPlayerML trains its deep learning model after each game 
(if it has is_training set to True).

AIPlayerML takes in a model_file as a parameter, which may or may not already be initialized. If it is
already initialized, then the agent uses the weights stored there. Regardless, once the game playing is
over, if is_training is set to true, the PlayerUpdater service will store the new weights in the model_file
provided.
"""
class AIPlayerML(Player):
    def __init__(self, card1: Card, card2: Card, model_file: str, id: int = 1, is_training = False, name: str = "cg32"):
        super().__init__(id = id, name = name, card1 = card1, card2 =card2)
        self.is_AI: bool = True
        self.is_training = is_training
        self.model_file = model_file
        # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
        # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
        self.model = PolicyNetwork(32, 13)
        if os.path.isfile(model_file):
            self.model.load_state_dict(torch.load(model_file, weights_only=True))
        
    def makeMove(self, players: list[Player], action_log: list[Action]) -> MoveWithTarget:
        action_mask: list[np.int8] = PlayerMethods.getActionMask(self, players)
        opps = [a for a in players if a.id != self.id]
        opps.sort(key= lambda a: (a.num_cards, a.num_coins), reverse = True)
        encoded_state = PlayerMethods.getOneHotEncodeState([self, opps[0], opps[1], opps[2]])
        action_list = self.model(encoded_state)
        action_list[~torch.tensor(action_mask, dtype=torch.bool)] = float('-inf')
        action_list = F.softmax(action_list, dim=0)
        action = torch.multinomial(action_list, 1).item()
        log_action_prob = torch.log1p(action_list[action] - 1)
        return MoveWithTarget(action), log_action_prob

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