from torch import Tensor
from Objects.MoveWithTarget import MoveWithTarget
from Objects.GameState import GameState
from Objects.MoveLogEntry import MoveLogEntry
from Players.Player import Player

"""
MoveLogger is a service that logs all of the moves taken in a game, which can be used for
training player models or making game decisions.

For example, players may not want to steal from a player who most likely can block their stealing
action, or they may want to reward themselves for killing more opponent's cards.
"""
class MoveLogger:
    def logMove(curr_player: Player, sorted_opps: list[Player], action: MoveWithTarget, action_prob: Tensor, move_log: list[MoveLogEntry]) -> None:
        game_state = GameState(curr_player, sorted_opps)
        move_log.append(MoveLogEntry(curr_player.id, game_state, action, action_prob))

    def updatePreviousReward(move_log: list[MoveLogEntry], _reward: float):
        move_log[-1].reward = _reward