# Note: Used previously to store data in a csv to track model growth
class GameLog:
    def __init__(self, game_num: int, rank: int, num_kills: int, policy_loss: float, chance_of_coup_in_game_winning_state: float, chance_of_assassinate_in_game_winning_state: float):
        self.game_num = game_num
        self.rank = rank
        self.num_kills = num_kills
        self.policy_loss = policy_loss
        self.chance_of_coup_in_game_winning_state = chance_of_coup_in_game_winning_state
        self.chance_of_assassinate_in_game_winning_state = chance_of_assassinate_in_game_winning_state
