from Objects.Move import Move
from Objects.Card import Card
from Players.Player import Player
from Objects.Action import Action

class ActionLogger:
    def logAction(action: Action, actionLog: list[Action]) -> None:
        actionLog.append(action)
