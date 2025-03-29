from Players.AIPlayer import AIPlayer
from Services.MoveLogger import MoveLogEntry
from Constants import Constants
from Services.GameMethods import *
import torch
import torch.optim as optim
from torch.optim import adam

class PlayerUpdater:
    def __init__(self, agents: list[AIPlayer]):
        self.playersTraining: list[int] = [agent.id for agent in agents if agent.isTraining]
        self.playerModels: dict = {agent.id: agent.model for agent in agents if agent.isTraining}
        self.playerOptimizers: dict[int, adam.Adam] = {agent.id: optim.Adam(self.playerModels[agent.id].parameters(), lr=1e-4) for agent in agents if agent.isTraining}
        self.playerModelFiles: dict = {agent.id: agent.modelFile for agent in agents if agent.isTraining}
        
    def updatePlayers(self, moveLog: list[MoveLogEntry]):
        for agentId in self.playersTraining:
            agentMoves = [a for a in moveLog if a.playerId == agentId]
            agentNumberOfKills = len([a for a in agentMoves if a.action in Constants.LISTOFKILLMOVES])
            rewards = torch.tensor(GameMethods.computeDiscountedRewards(len(agentMoves)), dtype=torch.float32) #, device=logActionProb.device
            policyLoss = torch.stack([reward * action.actionProb for reward, action in zip(rewards, agentMoves)]).sum()
            policLossKillCountConstant = 1 - agentNumberOfKills # Killing less than one card is punished, killing more than one is rewarded
            policyMultiplierOverall = torch.tensor(Constants.POLICYLOSSMULTIPLERBYRANKDICTIONARY[p0Place] + policLossKillCountConstant, dtype=torch.float32, device=policyLoss.device)
            policyLoss = policyMultiplierOverall * policyLoss

            optimizer = self.playerOptimizers[agentId]
            optimizer.zero_grad()
            policyLoss.backward()
            optimizer.step()

    def storePlayerModels(self):
        for agentId in self.playersTraining:
            torch.save(self.playerModels[agentId].state_dict(), self.playerModelFiles[agentId])

