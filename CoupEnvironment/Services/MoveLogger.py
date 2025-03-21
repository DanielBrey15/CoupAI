from Objects.MoveWithTarget import MoveWithTarget
from Players.Player import Player
from torch import Tensor

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

class MoveLogEntry:
    def __init__(self, currPlayerId: int, gameState: GameState, action: MoveWithTarget, actionProb: Tensor):
        self.playerId = currPlayerId
        self.gameState = gameState
        self.action = action
        self.actionProb = actionProb

class MoveLogger:
    def logMove(currPlayer: Player, sortedOpps: list[Player], action: MoveWithTarget, actionProb: Tensor, moveLog: list[MoveLogEntry]) -> None:
        gameState = GameState(currPlayer, sortedOpps)
        moveLog.append(MoveLogEntry(currPlayer.id, gameState, action, actionProb))