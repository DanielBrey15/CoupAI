from Objects.Move import Move
from Objects.MoveWithTarget import MoveWithTarget
from Objects.Card import Card
from Objects.MoveLogEntry import MoveLogEntry
from Players.Player import Player
from Players.AIPlayer import AIPlayer
from Players.AIPlayerML import AIPlayerML
import random
from Objects.Action import *
from typing import Tuple
from Objects.GameLog import GameLog

"""
GameMethods is a service that provides methods to update the Coup game.

Along with others, this includes methods used to check if anyone calls out an action,
blocks an action, and setting up the game
"""
class GameMethods:
    def isSuccessfullyCalledOut(
        self,
        card: Card,
        player_moving: Player,
        players: list[Player],
        deck: list[Card],
        setDeck,
        move_log: list[GameLog]) -> bool:

        is_called_out = False
        player_calling_out = None
        for player in players:
            if(player.getName() != player_moving.getName()):
                if(player.callsActionOut()):
                    is_called_out = True
                    player_calling_out = player
                    break
        if not is_called_out:
            return False
        else:
            have_card = card in player_moving.getCards()
            if have_card:
                player_calling_out.loseCard()
                temp_deck = deck
                
                # Add player_moving's card to deck and shuffle before handing them card back
                temp_deck.append(card)
                random.shuffle(temp_deck)

                cards_drawn: Card = temp_deck.pop()
                setDeck(temp_deck)
                player_moving.switchCard(card_switched_out = card, card_gained = cards_drawn)
                return False
            else:
                player_moving.loseCard()
                return True
        
    def resolveMove(self,
        player: Player,
        move: Move,
        target: Player | None,
        isBlocked,
        players: list[Player],
        deck: list[Card],
        setDeck,
        move_log: list[GameLog]) -> int:

        loss = 1

        if move == Move.INCOME:
            player.updateNumCoins(1)
        elif move == Move.FOREIGN_AID:
            if not isBlocked(player_moving = player, move = Move.FOREIGN_AID, potential_blocking_card = Card.DUKE):
                player.updateNumCoins(2)
            else:
                loss += 10
        elif move == Move.TAX:
            if not self.isSuccessfullyCalledOut(self, card=Card.DUKE, player_moving=player, players=players, deck=deck, setDeck=setDeck, move_log=move_log):
                player.updateNumCoins(3)
        elif move == Move.EXCHANGE:
            if not self.isSuccessfullyCalledOut(self, card=Card.AMBASSADOR, player_moving=player, players=players, deck=deck, setDeck=setDeck, move_log=move_log):
                exchangeCards: list[Card] = deck[:2]
                cardsReturned: list[Card] = player.resolveExchange(exchangeCards, self)
                deck_after_exchanging: list[Card] = deck[2:]
                deck_after_exchanging.extend(cardsReturned)
                random.shuffle(deck_after_exchanging)
                setDeck(deck_after_exchanging)
        elif move == Move.COUP:
            player.updateNumCoins(-7)
            target.loseCard()
        elif move == Move.STEAL:
            if not self.isSuccessfullyCalledOut(self, card=Card.CAPTAIN, player_moving=player, players=players, deck=deck, setDeck=setDeck, move_log=move_log):
                if not isBlocked(player_moving = player, move = Move.STEAL, target = target):
                    coins_stolen = min(2, target.getNumCoins())
                    player.updateNumCoins(coins_stolen)
                    target.updateNumCoins(-coins_stolen)
                else:
                    loss += 10
        elif move == Move.ASSASSINATE:
            player.updateNumCoins(-3)
            if not self.isSuccessfullyCalledOut(self, card=Card.ASSASSIN, player_moving=player, players=players, deck=deck, setDeck=setDeck, move_log=move_log):
                if not isBlocked(player_moving = player, move = Move.ASSASSINATE, target = target, potential_blocking_card = Card.CONTESSA):
                    target.loseCard()
                else:
                    loss += 10
        else:
            print("Shouldn't hit here")
        return loss
    
    def getPlayerByName(self, name: str) -> Player:
        for player in self.players:
            if player.name == name:
                return player
        return None
        
    def getPlayers(self) -> list[Player]:
        return self.players
    
    def createDeck(players: list[Player]) -> list[Card]:
        deck: list[Card] = []
        for card in Card:
            deck.extend([card, card, card])
        for player in players:
            for card in player.getCards():
                deck.remove(card)
        random.shuffle(deck)
        return deck
    
    def createDeckAndPlayers():
        players: list[Player] = []
        deck: list[Card] = []
        for card in Card:
            deck.extend([card, card, card])
        random.shuffle(deck)
        p_cards, deck = deck[:2], deck[2:]
        players.append(AIPlayerML(card1 = p_cards[0], card2 = p_cards[1], model_file="ModelFiles/Model4.pt", is_training = True, id = 0, name = "p0"))
        for p in range(1,4):
            p_cards, deck = deck[:2], deck[2:]
            players.append(AIPlayer(card1 = p_cards[0], card2 = p_cards[1], id = p, name = f"p{p}"))
        return deck, players
    
    def resetDeckAndPlayers(players: list[Player]):
        deck: list[Card] = []
        for card in Card:
            deck.extend([card, card, card])
        random.shuffle(deck)
        for p in players:
            p_cards, deck = deck[:2], deck[2:]
            p.resetPlayer(p_cards[0], p_cards[1])
        return deck

    def getDeck(self) -> list[Card]:
        return self.deck

    def computeDiscountedRewards(_moves: list[MoveLogEntry], gamma=0.99):
        discounted_rewards = []
        for i, _move in enumerate(reversed(_moves)):
            discounted_rewards.append(_move.reward * gamma**i)
        return discounted_rewards
    
    def computeDiscountedRewardsOLD(num_moves, gamma=0.99): #Remove later -- used in CoupEnvironmentModelTrainer, which is outdated
        discounted_rewards = []
        for r in reversed(range(num_moves)):
            discounted_rewards.append(gamma**r)
        return discounted_rewards

    def splitMoveAndTarget(move_with_target: MoveWithTarget, opp_dict: dict[int, int]) -> Tuple[Move, (int | None)]:
        target_dict = {
            MoveWithTarget.INCOME: (Move.INCOME, None),
            MoveWithTarget.FOREIGN_AID: (Move.FOREIGN_AID, None),
            MoveWithTarget.COUP_PLAYER_1: (Move.COUP, 0),
            MoveWithTarget.COUP_PLAYER_2: (Move.COUP, 1),
            MoveWithTarget.COUP_PLAYER_3: (Move.COUP, 2),
            MoveWithTarget.TAX: (Move.TAX, None),
            MoveWithTarget.STEAL_PLAYER_1: (Move.STEAL, 0),
            MoveWithTarget.STEAL_PLAYER_2: (Move.STEAL, 1),
            MoveWithTarget.STEAL_PLAYER_3: (Move.STEAL, 2),
            MoveWithTarget.ASSASSINATE_PLAYER_1: (Move.ASSASSINATE, 0),
            MoveWithTarget.ASSASSINATE_PLAYER_2: (Move.ASSASSINATE, 1),
            MoveWithTarget.ASSASSINATE_PLAYER_3: (Move.ASSASSINATE, 2),
            MoveWithTarget.EXCHANGE: (Move.EXCHANGE, None)
        }
        move, target_opp_rank = target_dict[move_with_target]
        return (move, None) if target_opp_rank == None else (move, opp_dict[target_opp_rank])