from Players.Player import Player
import numpy as np
from Objects.MoveWithTarget import MoveWithTarget
from Constants import Constants
import torch
import torch.nn.functional as F

"""
PlayerMethods is a service that provides methods to provide info for specific players.

This includes methods to determine the actions possible for a specific player based on the state
and to collect the one hot encoded state that is currently used decide the best moves.
"""
class PlayerMethods:
    def getActionMask(curr_player: Player, players: list[Player]) -> list[np.int8]:
        action_mask = np.ones(13, dtype=np.int8)
        opps = [p for p in players if p.id != curr_player.id]
        opps.sort(key= lambda agent: (agent.num_cards, agent.num_coins), reverse = True)
        if opps[0].num_cards == 0:
            action_mask[MoveWithTarget.COUP_PLAYER_1] = 0
            action_mask[MoveWithTarget.STEAL_PLAYER_1] = 0
            action_mask[MoveWithTarget.ASSASSINATE_PLAYER_1] = 0
        if opps[1].num_cards == 0:
            action_mask[MoveWithTarget.COUP_PLAYER_2] = 0
            action_mask[MoveWithTarget.STEAL_PLAYER_2] = 0
            action_mask[MoveWithTarget.ASSASSINATE_PLAYER_2] = 0
        if opps[2].num_cards == 0:
            action_mask[MoveWithTarget.COUP_PLAYER_3] = 0
            action_mask[MoveWithTarget.STEAL_PLAYER_3] = 0
            action_mask[MoveWithTarget.ASSASSINATE_PLAYER_3] = 0

        if curr_player.num_coins < 7:
            action_mask[MoveWithTarget.COUP_PLAYER_1] = 0
            action_mask[MoveWithTarget.COUP_PLAYER_2] = 0
            action_mask[MoveWithTarget.COUP_PLAYER_3] = 0
            if curr_player.num_coins < 3:
                action_mask[MoveWithTarget.ASSASSINATE_PLAYER_1] = 0
                action_mask[MoveWithTarget.ASSASSINATE_PLAYER_2] = 0
                action_mask[MoveWithTarget.ASSASSINATE_PLAYER_3] = 0
        elif curr_player.num_coins >= 10:
            action_mask[MoveWithTarget.INCOME] = 0
            action_mask[MoveWithTarget.FOREIGN_AID] = 0
            action_mask[MoveWithTarget.TAX] = 0
            action_mask[MoveWithTarget.STEAL_PLAYER_1] = 0
            action_mask[MoveWithTarget.STEAL_PLAYER_2] = 0
            action_mask[MoveWithTarget.STEAL_PLAYER_3] = 0
            action_mask[MoveWithTarget.ASSASSINATE_PLAYER_1] = 0
            action_mask[MoveWithTarget.ASSASSINATE_PLAYER_2] = 0
            action_mask[MoveWithTarget.ASSASSINATE_PLAYER_3] = 0
            action_mask[MoveWithTarget.EXCHANGE] = 0
        
        return action_mask

    def getOneHotEncodeState(ordered_players: list[Player]):
        ordered_num_cards = [p.num_cards for p in ordered_players]
        ordered_num_coin_brackets = [Constants.NUMBER_OF_COINS_TO_STATE_BRACKET_MAPPING[p.num_coins] for p in ordered_players]
        one_hot_input_cards = torch.cat([F.one_hot(torch.tensor(i), num_classes=3) for i in ordered_num_cards])
        one_hot_input_coins = torch.cat([F.one_hot(torch.tensor(j), num_classes=5) for j in ordered_num_coin_brackets])
        all_one_hot_inputs = torch.cat([one_hot_input_cards, one_hot_input_coins]).float()
        return all_one_hot_inputs