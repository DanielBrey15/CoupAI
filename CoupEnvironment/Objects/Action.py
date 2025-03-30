from Objects.ActionType import ActionType
from Players.Player import Player
from Objects.Card import Card
from Objects.Move import Move
from typing import Union

class BaseAction:
    def __init__(self, action_type: ActionType, player_acting: Player):
        self.action_type = action_type
        self.player_acting = player_acting

class MoveAction(BaseAction):
    def __init__(self, player_moving: Player, move: Move, target: Player): #TODO TARGET SHOULD NOT BE NONNULLABLE
        super().__init__(ActionType.MOVE, player_moving)
        self.move= move
        self.target = target

class BlockAction(BaseAction):
    def __init__(self, player_blocking: Player, player_blocked: Player, move: Move, card_blocking: Card):
        super().__init__(ActionType.BLOCK, player_blocking)
        self.player_blocked = player_blocked
        self.move= move
        self.card_blocking = card_blocking

class CallOutAction(BaseAction):
    def __init__(self, player_calling_out: Player, player_making_move: Player, card_acting: Card):
        super().__init__(ActionType.CALL_OUT, player_calling_out)
        self.player_making_move = player_making_move
        self.card_acting= card_acting
        self.is_successfully_called_out = card_acting in player_making_move.getCards()

class LoseCardAction(BaseAction):
    def __init__(self, player_losing: Player, card_lost: Card):
        super().__init__(ActionType.LOSE_CARD, player_losing)
        self.card_lost= card_lost

class SwitchCardAction(BaseAction):
    def __init__(self, player: Player, card_lost: Card, card_gained: Card):
        super().__init__(ActionType.SWITCH_CARD, player)
        self.card_lost= card_lost
        self.card_gained= card_gained

Action = Union[MoveAction, BlockAction, CallOutAction, LoseCardAction, SwitchCardAction]

