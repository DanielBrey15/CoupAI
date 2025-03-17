from Objects.Move import MoveWithTarget
from Objects.Card import Card
from Players.Player import Player
from Objects.Action import MoveAction

class GameState:
    def __init__(self, currPlayer: Player, sortedOpps: list[Player]):
        self.myCards = currPlayer.numCards
        self.myCoins = currPlayer.numCoins
        self.opp1Cards = sortedOpps[0].numCards
        self.opp1Coins = sortedOpps[0].numCoins
        self.opp2Cards = sortedOpps[1].numCards
        self.opp2Coins = sortedOpps[1].numCoins
        self.opp3Cards = sortedOpps[2].numCards
        self.opp3Coins = sortedOpps[2].numCoins

class Log:
    def __init__(self, currPlayerId: int, gameState: GameState, action: MoveWithTarget, actionProb: float):
        self.playerId = currPlayerId
        self.gameState = gameState
        self.action = action
        self.actionProb = actionProb

class ActionLogger2:
    def logAction(currPlayer: Player, sortedOpps: list[Player], action: MoveWithTarget, actionProb: float, actionLog: list[Log]) -> None:
        gameState = GameState(currPlayer, sortedOpps)
        actionLog.append(Log(currPlayer.id, gameState, action, actionProb))