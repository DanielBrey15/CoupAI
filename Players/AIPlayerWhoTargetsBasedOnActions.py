from Players.AIPlayer import AIPlayer
from Objects.Card import Card
from enum import Enum
from Objects.Move import Move
from Objects.Action import *
from collections import defaultdict
import tensorflow as tf
import pandas as pd

class AIPlayerWhoTargetsBasedOnActions(AIPlayer):
    def __init__(self, card1: Card, card2: Card, name: str = "cg32"):
        super().__init__(card1, card2, name)

    def acquireTarget(self, players: list[Player], move: Move, actionLog: list[Action]):
        # if move == Move.STEAL:
        #     playersTargettable = [p for p in players if p.getNumCards() > 0 and p.getName() != self.getName()]
        #     filteredTargets = [p for p in playersTargettable if not self.playerUsedAmbassadorOrCaptain(p, actionLog)]
        #     if(len(filteredTargets) > 0):
        #         return self.findPlayerLeftWithMostCoins(filteredTargets)
        #     else:
        #         return self.findPlayerLeftWithMostCoins(playersTargettable)
        if move == Move.STEAL:
            #iterate through targettable players (who have 2 or more coins), find vals, and plug them into model. return player with lowest value
            playersTargettable = [p for p in players if p.getNumCards() > 0 and p.getNumCoins() > 1 and p.getName() != self.getName()]
            if len(playersTargettable) == 0:
                return self.findPlayerLeftWithMostCoins(players)
            if len(playersTargettable) == 1:
                return playersTargettable[0]
            model = tf.keras.models.load_model("ModelScripts/stealModel1.keras")
            target: Player | None = None
            targetChance: float = 1
            #find totals
            totalMoveCountDict = defaultdict(int)
            moveActions = [a for a in actionLog if a.actionType == ActionType.Move]
            for moveAction in moveActions:
                totalMoveCountDict[moveAction.move] += 1
            blockStealActions = [a for a in actionLog if a.actionType == ActionType.Block and a.move == Move.STEAL]
            numTotalBlockStealActions = len(blockStealActions)
            totalCardsLeft = sum([p.getNumCards() for p in players])
            myCards = self.getNumCards()
            myCoins = self.getNumCoins()
            for p in playersTargettable:
                playerMoveActions = [a for a in moveActions if a.playerActing == p]
                playerMoveCountDict = defaultdict(int)
                for playerMoveAction in playerMoveActions:
                    playerMoveCountDict[playerMoveAction.move] += 1
                numPlayerBlockStealActions = len([a for a in blockStealActions if a.playerActing == p])
                playerNumCardsLeft = p.getNumCards()
                playerNumCoins = p.getNumCoins()
                modelInput = [
                    totalMoveCountDict[Move.INCOME], #Total Income moves
                    totalMoveCountDict[Move.FOREIGNAID], #Total Foreign Aid moves
                    totalMoveCountDict[Move.COUP], #Total Coup moves
                    totalMoveCountDict[Move.TAX], #Total Tax moves
                    totalMoveCountDict[Move.STEAL], #Total Steal moves
                    totalMoveCountDict[Move.ASSASSINATE], #Total Assassinate moves
                    totalMoveCountDict[Move.EXCHANGE], #Total Exchange moves
                    numTotalBlockStealActions, #Total Block Steal actions
                    totalCardsLeft, #Total cards left
                    playerMoveCountDict[Move.INCOME], #Target player's Income moves
                    playerMoveCountDict[Move.FOREIGNAID], #Target player's Foreign Aid moves
                    playerMoveCountDict[Move.COUP], #Target player's Coup moves
                    playerMoveCountDict[Move.TAX], #Target player's Tax moves
                    playerMoveCountDict[Move.STEAL], #Target player's Steal moves
                    playerMoveCountDict[Move.ASSASSINATE], #Target player's Assassinate moves
                    playerMoveCountDict[Move.EXCHANGE], #Target player's Exchange moves
                    numPlayerBlockStealActions, #Target player's Block Steal actions
                    playerNumCardsLeft, #Target player's cards left
                    playerNumCoins, #Target player's coins
                    myCards, #My cards
                    myCoins #My coins
                ]
                prediction = model.predict(pd.DataFrame([modelInput]))
                print(prediction)
                if prediction <= targetChance:
                    targetChance = prediction
                    target = p
            return target
        elif move == Move.ASSASSINATE or move == Move.COUP:
            return self.findPlayerLeftWithMostCoins(players)
        else:
            raise ValueError(f"Move {move} shouldn't be acquiring a target")
    
    def makeMove(self, players: list[Player], actionLog: list[Action]):
        playersTargettable = [p for p in players if p.getNumCards() > 0 and p.getName() != self.getName()]
        anyPossibleStealTargets = len([p for p in playersTargettable if not self.playerUsedAmbassadorOrCaptain(p, actionLog)]) > 0
        if self.numCoins >= 10:
            return Move.COUP
        elif self.cards.__contains__(Card.ASSASSIN) and self.numCoins >= 3:
            return Move.ASSASSINATE
        elif self.cards.__contains__(Card.DUKE):
            return Move.TAX
        elif self.cards.__contains__(Card.CAPTAIN) and anyPossibleStealTargets:
            return Move.STEAL
        elif self.cards.__contains__(Card.AMBASSADOR):
            return Move.EXCHANGE
        else:
            return Move.INCOME
        
    
    def playerUsedAmbassadorOrCaptain(self, player: Player, actionLog: list[Action]) -> bool:
        playerActions: list[Action] = [a for a in actionLog if a.playerActing == player]
        playerBlockStealActions: list[Action] = [a for a in playerActions if
                                               a.actionType == ActionType.Block
                                               and a.move == Move.STEAL]
        playerStealBlockerMoveActions: list[Action] = [a for a in playerActions if
                                           a.actionType == ActionType.Move
                                           and a.move in {Move.EXCHANGE, Move.STEAL} ]
        return len(playerBlockStealActions) > 0 # We care about this, but not yet: or len(playerStealBlockerMoveActions) > 0