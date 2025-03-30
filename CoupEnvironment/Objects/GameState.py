from Players.Player import Player

class GameState:
    def __init__(self, curr_player: Player, sorted_opps: list[Player]):
        self.my_cards = curr_player.num_cards
        self.myCoins = curr_player.num_coins
        self.opp_1_cards = sorted_opps[0].num_cards
        self.opp_1_coins = sorted_opps[0].num_coins
        self.opp_2_cards = sorted_opps[1].num_cards
        self.opp_2_coins = sorted_opps[1].num_coins
        self.opp_3_cards = sorted_opps[2].num_cards
        self.opp_3_coins = sorted_opps[2].num_coins