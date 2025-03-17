from Objects.ActionType import ActionType
from Players.Player import Player
from Objects.Card import Card
from Objects.Move import Move
from typing import Union

class BaseAction:
    def __init__(self, actionType: ActionType, playerActing: Player):
        self.actionType = actionType
        self.playerActing = playerActing

class MoveAction(BaseAction):
    def __init__(self, playerMoving: Player, move: Move, target: Player): #TODO TARGET SHOULD NOT BE NONNULLABLE
        super().__init__(ActionType.Move, playerMoving)
        self.move= move
        self.target = target

class BlockAction(BaseAction):
    def __init__(self, playerBlocking: Player, playerBlocked: Player, move: Move, cardBlocking: Card):
        super().__init__(ActionType.Block, playerBlocking)
        self.playerBlocked = playerBlocked
        self.move= move
        self.cardBlocking = cardBlocking

class CallOutAction(BaseAction):
    def __init__(self, playerCallingOut: Player, playerMakingMove: Player, cardActing: Card):
        super().__init__(ActionType.CallOut, playerCallingOut)
        self.playerMakingMove = playerMakingMove
        self.cardActing= cardActing
        self.isSuccessfullyCalledOut = cardActing in playerMakingMove.getCards()

class LoseCardAction(BaseAction):
    def __init__(self, playerLosing: Player, cardLost: Card):
        super().__init__(ActionType.LoseCard, playerLosing)
        self.cardLost= cardLost

class SwitchCardAction(BaseAction):
    def __init__(self, player: Player, cardLost: Card, cardGained: Card):
        super().__init__(ActionType.SwitchCard, player)
        self.cardLost= cardLost
        self.cardGained= cardGained

Action = Union[MoveAction, BlockAction, CallOutAction, LoseCardAction, SwitchCardAction]


