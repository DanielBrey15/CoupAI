from Players.AIPlayer import AIPlayer
from Services.MoveLogger import MoveLogEntry
from Constants import Constants
from Services.GameMethods import *
import torch
import torch.optim as optim
from torch.optim import adam

"""
PlayerUpdater is a service that provides functionality to update the models of the
agents that are currently in training.

This includes methods to update players after each game as well as store those models when
the current round of training is completed.
"""
class PlayerUpdater:
    def __init__(self, agents: list[AIPlayer]):
        self.players_training: list[int] = [agent.id for agent in agents if agent.is_training]
        self.player_models: dict = {agent.id: agent.model for agent in agents if agent.is_training}
        self.player_optimizers: dict[int, adam.Adam] = {agent.id: optim.Adam(self.player_models[agent.id].parameters(), lr=1e-4) for agent in agents if agent.is_training}
        self.player_model_files: dict = {agent.id: agent.model_file for agent in agents if agent.is_training}
        
    def updatePlayers(self, move_log: list[MoveLogEntry], player_IDs_ranked: list[int]):
        for agent_ID in self.players_training:
            agent_moves = [a for a in move_log if a.player_id == agent_ID]
            agent_first_move = agent_moves[0] # Remove later -- May not need it now that rewards were created throughout
            agent_number_of_kills = len([a for a in agent_moves if a.action in Constants.LIST_OF_KILL_MOVES])
            rewards = torch.tensor(GameMethods.computeDiscountedRewards(agent_moves), dtype=torch.float32, device=agent_first_move.action_prob.device) #, device=logActionProb.device
            policy_loss = torch.stack([reward * action.action_prob for reward, action in zip(rewards, agent_moves)]).sum()
            policy_loss_kill_count_constant = 1 - agent_number_of_kills # Killing less than one card is punished, killing more than one is rewarded
            policy_multiplier_overall = torch.tensor(Constants.POLICY_LOSS_MULTIPLIER_BY_RANK_DICTIONARY[4-player_IDs_ranked[agent_ID]] + policy_loss_kill_count_constant, dtype=torch.float32, device=policy_loss.device)
            policy_loss = policy_multiplier_overall + policy_loss

            optimizer = self.player_optimizers[agent_ID]
            optimizer.zero_grad()
            policy_loss.backward()
            optimizer.step()

    def storePlayerModels(self):
        for agent_ID in self.players_training:
            torch.save(self.player_models[agent_ID].state_dict(), self.player_model_files[agent_ID])
