from Objects.Action import Action

class ActionLogger:
    def logAction(action: Action, actionLog: list[Action]) -> None:
        actionLog.append(action)
