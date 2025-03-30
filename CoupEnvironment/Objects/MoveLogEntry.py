from torch import Tensor
from Objects.MoveWithTarget import MoveWithTarget
from Objects.GameState import GameState

class MoveLogEntry:
    def __init__(self, curr_player_id: int, game_state: GameState, action: MoveWithTarget, action_prob: Tensor):
        self.player_id = curr_player_id
        self.game_state = game_state
        self.action = action
        self.action_prob = action_prob