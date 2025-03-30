import numpy as np
from gym import spaces
from Players.Player import Player
from Objects.Card import Card
from Objects.MoveWithTarget import MoveWithTarget
from Objects.Action import *
from typing import Optional
from Services.GameMethods import *
from Services.MoveLogger import MoveLogger, MoveLogEntry
from pettingzoo import AECEnv
import torch
import torch.optim as optim
import torch.nn.functional as F
from math import log
import matplotlib.pyplot as plt
from Objects.GameLog import GameLog
import csv
from Constants import Constants
from Models.PolicyNetwork import PolicyNetwork
from Services.PlayerMethods import PlayerMethods

"""
CoupEnvironmentModelTrainer.py is a script used to run Coup and train a deep learning model.
Given a number, it plays that many games of Coup between 4 players (Players manually added in the GameMethods service).
It also updates the model bewtween games to hopefully strengthen the trained player.

The first player is an agent trained on a deep learning model while the other 3 players use
heuristics, so CoupEnvironment.py plots the first player's win percentage over time to indicate the model's growth.

Currently, I am using CoupEnvironment.py since it is more flexible to train multiple players.
Please check out that file for the most up to date work.
"""
class CoupEnvironmentModelTrainer(AECEnv):
    def __init__(self):
        super().__init__()
        deck, agents = GameMethods.createDeckAndPlayers()
        self.agents: list[Player] =  agents
        self.deck: list[Card] = deck
        self.possible_agents = self.agents[:]
        self.agent_selection = self.agents[0]
        self.rewards = {agent.id: 0 for agent in self.agents}
        self.dones = {agent.id: False for agent in self.agents}
        self.moveLog: list[MoveLogEntry] = []
        self.gameLog: list[GameLog] = []

        self.action_spaces = {agent.id: spaces.Discrete(13) for agent in self.agents} # [Income, Foreign Aid, Coup Opp A, Coup Opp B, Coup Opp C, Tax, Steal Opp A, Steal Opp B, Steal Opp C, Assassinate Opp A, Assassinate Opp B, Assassinate Opp C, Exchange]
        self.observation_spaces = {agent.id: spaces.Discrete(1) for agent in self.agents}

    def __str__(self):
        gameStatus = "\nGame Status: [\n"
        for player in self.agents:
            gameStatus += str(player) + "\n"
        return gameStatus[:-1] + " ]"

    def reset(self, seed=32, options=None) -> None:
        random.seed(seed)
        deck = GameMethods.resetDeckAndPlayers(self.agents)
        self.deck: list[Card] = deck
        self.agent_selection = self.agents[0]
        self.rewards = {agent.id: 0 for agent in self.agents}
        self.dones = {agent.id: False for agent in self.agents}
        self.moveLog: list[MoveLogEntry] = []

    def step(self, action, agent, actionProb) -> None:
        opps = [a for a in self.agents if a.id != agent.id]
        opps.sort(key= lambda agent: (agent.numCards, agent.numCoins), reverse = True)
        sortedOppIds = [opp.id for opp in opps]
        oppRankToIdDictionary = {i: sortedOppIds[i] for i in range(3)}
        moveWithTarget = MoveWithTarget(action)
        move, targetId = GameMethods.splitMoveAndTarget(moveWithTarget, oppRankToIdDictionary)
        target = None if targetId == None else [agent for agent in self.agents if agent.id == targetId][0]
        MoveLogger.logMove(
            currPlayer = agent,
            sortedOpps = opps,
            action = moveWithTarget,
            actionProb = actionProb,
            moveLog = self.moveLog 
        )
        GameMethods.resolveMove(GameMethods, agent, move, target, self.isBlocked, self.agents, self.deck, self.setDeck, moveLog = env.moveLog)

        env.dones = [agent.numCards == 0 for agent in env.agents]

        nextAgentId = (agent.id + 1) % self.num_agents
        while self.dones[nextAgentId]:
            nextAgentId = (nextAgentId + 1) % self.num_agents
        self.agent_selection = self.agents[nextAgentId]
        return
    
    def isBlocked(self, playerMoving, move, target = None, potentialBlockingCard = None) -> bool:
        players = self.agents
        blockingPlayer: Optional[Player] = None
        cardAIBlocksWith: Optional[Card] = None
        for player in players:
            cardAIBlocksWith = player.AIBlock(playerMoving, move, target)
            if(cardAIBlocksWith):
                blockingPlayer = player
                break
        if blockingPlayer:
            print(f"\n{blockingPlayer.name} blocks with {cardAIBlocksWith}")
            if not GameMethods.isSuccessfullyCalledOut(GameMethods, card=cardAIBlocksWith, playerMoving=blockingPlayer, players=self.agents, deck=self.deck, setDeck=self.setDeck, moveLog=self.moveLog):
                return True
            return False
        return False
    
    def logGame(self, gameNum: int, rank: int, numKills: int, policyLoss: float, chanceofCoupInGameWinningState: float, chanceofAssassinateInGameWinningState: float):
        self.gameLog.append(GameLog(gameNum, rank, numKills, policyLoss, chanceofCoupInGameWinningState, chanceofAssassinateInGameWinningState))

    def logGameDataInCSV(self, winPercentage: float) -> None:
        with open("CSVs/GameData.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f"### Training new model - Win Percentage: {winPercentage*100}%"])
            writer.writerow({
                "GameNum": "GameNum",
                "Rank": "Rank",
                "NumKills": "NumKills",
                "PolicyLoss": "PolicyLoss",
                "ChanceOfCoupInGameWinningState": "ChanceOfCoupInGameWinningState",
                "ChanceOfAssassinateInGameWinningState": "ChanceOfAssassinateInGameWinningState",
            }.values())
            for game in env.gameLog:
                writer.writerow({
                "GameNum": game.gameNum,
                "Rank": game.rank,
                "NumKills": game.numKills,
                "PolicyLoss": game.policyLoss,
                "ChanceOfCoupInGameWinningState": game.chanceOfCoupInGameWinningState,
                "ChanceOfAssassinateInGameWinningState": game.chanceOfAssasssinateInGameWinningState,
            }.values())
        return

    def setPlayers(self, newPlayers) -> None:
        self.players = newPlayers

    def setDeck(self, newDeck) -> None:
        self.deck = newDeck

    def render(self) -> None:
        print(self)

if __name__ == "__main__":
    env = CoupEnvironmentModelTrainer()

    # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
    # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
    policyNet = PolicyNetwork(32, 13)

    policyNet.load_state_dict(torch.load("ModelFiles/Model1.pt", weights_only=True))
    optimizer = optim.Adam(policyNet.parameters(), lr=1e-4)

    # Keeping track of win percentage to visualize model's growth
    currWins: int = 0
    winPercentageOverTime: list[float] = []

    numGames = 20
    for i in range(numGames):
        env.reset()
        for agent in env.agent_iter():
            reward, done, info = env.rewards[agent.id], env.dones[agent.id], {}
            if done:
                action = None
                logActionProb = None
            else:
                if agent.id == 0:
                    actionMask: list[np.int8] = PlayerMethods.getActionMask(agent, env.agents)
                    opps = [a for a in env.agents if a.id != agent.id]
                    opps.sort(key= lambda a: (a.numCards, a.numCoins), reverse = True)
                    encodedState = PlayerMethods.getOneHotEncodeState([agent, opps[0], opps[1], opps[2]])
                    actionList = policyNet(encodedState)
                    actionList[~torch.tensor(actionMask, dtype=torch.bool)] = float('-inf')
                    actionList = F.softmax(actionList, dim=0)
                    action = torch.multinomial(actionList, 1).item()
                    logActionProb = torch.log1p(actionList[action] - 1)
                else:
                    action = agent.makeMove(env.agents, env.moveLog)
                    logActionProb = torch.tensor(1) # Shouldn't affect

            env.step(action, agent, logActionProb)
            env.render()

            if [a.numCards for a in env.agents if a.id == 0][0] == 0: #If p0 is out, collect their ranking and end
                p0Place = len([a for a in env.agents if a.numCards > 0]) + 1
                break

            if len([True for d in env.dones if not d]) == 1: #If only one player is left, it is p0 based on above condition
                p0Place = 1
                break 
        p0Moves = [a for a in env.moveLog if a.playerId == 0]
        p0NumberOfKills = len([a for a in p0Moves if a.action in Constants.LISTOFKILLMOVES])
        
        rewards = torch.tensor(GameMethods.computeDiscountedRewards(len(p0Moves)), dtype=torch.float32, device=logActionProb.device)
        policyLoss = torch.stack([reward * action.actionProb for reward, action in zip(rewards, p0Moves)]).sum()
        policLossKillCountConstant = 1 - p0NumberOfKills # Killing less than one card is punished, killing more than one is rewarded
        
        policyMultiplierOverall = torch.tensor(Constants.POLICYLOSSMULTIPLERBYRANKDICTIONARY[p0Place] + policLossKillCountConstant, dtype=torch.float32, device=policyLoss.device)
        policyLoss = policyMultiplierOverall * policyLoss

        if env.agents[0].numCards > 0:
            currWins += 1
        winPercentageOverTime.append(currWins/(i+1))

        optimizer.zero_grad()

        actionListTestCase = policyNet(torch.Tensor(Constants.ONEHOTENCODEDSTATETOWINGAME))
        actionListTestCase[~torch.tensor(Constants.ACTIONMASKFORSTATETOWINGAME, dtype=torch.bool)] = float('-inf')
        actionListTestCase = F.softmax(actionListTestCase, dim=0)
        chanceofCoupInGameWinningState, chanceofAssassinateInGameWinningState = (0,0)
        env.logGame(
            gameNum = i,
            rank = p0Place,
            numKills = p0NumberOfKills,
            policyLoss = policyLoss.item(),
            chanceofCoupInGameWinningState = actionListTestCase[MoveWithTarget.COUPPLAYER1].item(),
            chanceofAssassinateInGameWinningState = actionListTestCase[MoveWithTarget.ASSASSINATEPLAYER1].item(),
        )

        policyLoss.backward()
        optimizer.step()

    env.logGameDataInCSV(currWins/numGames)
    env.close()

    torch.save(policyNet.state_dict(), "ModelFiles/Model1.pt")

    plt.plot(range(100,numGames), winPercentageOverTime[100:], marker='o', linestyle='-')
    plt.xlabel("Games played")
    plt.ylabel("Win percentage")
    plt.title("Win percentage over time")
    plt.show()


