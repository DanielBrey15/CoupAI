import numpy as np
from gym import spaces
from Players.AIPlayer import AIPlayer
from Objects.Card import Card
from Objects.Move import Move
from Objects.Move import MoveWithTarget
from typing import Optional, Tuple
from Services.GameMethods import *
from Objects.Action import *
from Services.ActionLogger2 import ActionLogger2, Log
from pettingzoo import AECEnv
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from math import log
import matplotlib.pyplot as plt

class CoupEnvironment(AECEnv):
    metadata = {
        "render_modes": ["human"],
        "name": "coupEnvironment",
    }

    def __str__(self):
        gameStatus = "\nGame Status: [\n"
        for player in self.agents:
            gameStatus += str(player) + "\n"
        return gameStatus[:-1] + " ]"

    def __init__(self, numPlayers = 4):
        super().__init__()
        deck, agents = GameMethods.createDeckAndPlayers()
        self.agents: list[AIPlayer] =  agents
        self.deck: list[Card] = deck
        self.possible_agents = self.agents[:]
        self.agent_selection = self.agents[0]
        self.rewards = {agent.id: 0 for agent in self.agents}
        self.dones = {agent.id: False for agent in self.agents}
        self.actionLog: list[Log] = []

        self.action_spaces = {agent.id: spaces.Discrete(13) for agent in self.agents} # [Income, Foreign Aid, Coup Opp A, Coup Opp B, Coup Opp C, Tax, Steal Opp A, Steal Opp B, Steal Opp C, Assassinate Opp A, Assassinate Opp B, Assassinate Opp C, Exchange]
        self.observation_spaces = {agent.id: spaces.Discrete(1) for agent in self.agents}

    def reset(self, seed=None, options=None) -> None:
        deck, agents = GameMethods.createDeckAndPlayers()
        self.agents: list[AIPlayer] =  agents
        self.deck: list[Card] = deck
        self.agent_selection = self.agents[0]
        self.rewards = {agent.id: 0 for agent in self.agents}
        self.dones = {agent.id: False for agent in self.agents}
        self.actionLog: list[Log] = []

    def splitMoveAndTarget(self, moveWithTarget: MoveWithTarget, oppDict: dict[int, int]) -> Tuple[Move, (int | None)]:
        targetDict = {
            MoveWithTarget.INCOME: (Move.INCOME, None),
            MoveWithTarget.FOREIGNAID: (Move.FOREIGNAID, None),
            MoveWithTarget.COUPPLAYER1: (Move.COUP, 0),
            MoveWithTarget.COUPPLAYER2: (Move.COUP, 1),
            MoveWithTarget.COUPPLAYER3: (Move.COUP, 2),
            MoveWithTarget.TAX: (Move.TAX, None),
            MoveWithTarget.STEALPLAYER1: (Move.STEAL, 0),
            MoveWithTarget.STEALPLAYER2: (Move.STEAL, 1),
            MoveWithTarget.STEALPLAYER3: (Move.STEAL, 2),
            MoveWithTarget.ASSASSINATEPLAYER1: (Move.ASSASSINATE, 0),
            MoveWithTarget.ASSASSINATEPLAYER2: (Move.ASSASSINATE, 1),
            MoveWithTarget.ASSASSINATEPLAYER3: (Move.ASSASSINATE, 2),
            MoveWithTarget.EXCHANGE: (Move.EXCHANGE, None)
        }
        move, targetOppRank = targetDict[moveWithTarget]
        return (move, None) if targetOppRank == None else (move, oppDict[targetOppRank])
        

    def step(self, action, agent, actionProb) -> None:
        opps = [a for a in self.agents if a.id != agent.id]
        opps.sort(key= lambda agent: (agent.numCards, agent.numCoins), reverse = True)
        sortedOppIds = [opp.id for opp in opps]
        print(sortedOppIds)
        oppRankToIdDictionary = {i: sortedOppIds[i] for i in range(3)}
        moveWithTarget = MoveWithTarget(action)
        move, targetId = self.splitMoveAndTarget(moveWithTarget, oppRankToIdDictionary)
        target = None if targetId == None else [agent for agent in self.agents if agent.id == targetId][0]
        # ActionLogger.logAction(
        #     action= MoveAction(
        #         playerMoving=currPlayer,
        #         move= move,
        #         target=None
        #     ),
        #     actionLog=self.actionLog)
        ActionLogger2.logAction(
            currPlayer = agent,
            sortedOpps = opps,
            action = moveWithTarget,
            actionProb = actionProb,
            actionLog = self.actionLog 
        )
        GameMethods.resolveMove2(GameMethods, agent, move, target, self.isBlocked, self.agents, self.deck, self.setDeck, actionLog=self.actionLog)

        env.dones = [agent.numCards == 0 for agent in env.agents]

        nextAgentId = (agent.id + 1) % self.num_agents
        while self.dones[nextAgentId]:
            nextAgentId = (nextAgentId + 1) % self.num_agents
        self.agent_selection = self.agents[nextAgentId]
        return
    
    def isBlocked(self, playerMoving, move, target = None, potentialBlockingCard = None) -> bool:
        players = self.agents
        blockingPlayer: Optional[AIPlayer] = None
        cardAIBlocksWith: Optional[Card] = None
        for player in players:
            cardAIBlocksWith = player.AIBlock(playerMoving, move, target)
            if(cardAIBlocksWith):
                blockingPlayer = player
                break
        if blockingPlayer:
            print(f"\n{blockingPlayer.name} blocks with {cardAIBlocksWith}")
            if not GameMethods.isSuccessfullyCalledOut(GameMethods, card=cardAIBlocksWith, playerMoving=blockingPlayer, players=self.agents, deck=self.deck, setDeck=self.setDeck, actionLog=self.actionLog):
                return True
            return False
        return False
    
    def setPlayers(self, newPlayers) -> None:
        self.players = newPlayers

    def setDeck(self, newDeck) -> None:
        self.deck = newDeck

    def render(self) -> None:
        print(self)


class PolicyNetwork(nn.Module):
    def __init__(self, numStateVars, numActionOptions):
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(numStateVars, 128),
            nn.ReLU(),
            nn.Linear(128, numActionOptions),
        )

    def forward(self, x):
        return self.fc(x)


def computeDiscountedRewards(numMoves, gamma=0.99):
    discountedRewards = []
    for r in reversed(range(numMoves)):
        discountedRewards.append(gamma**r)
    return discountedRewards

def mapNumCoinsToBracket(numCoins: int) -> int:
    # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
    # Note: It's impossible to have over 13 coins
    numCoinsMapping = {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 3,
        5: 3,
        6: 3,
        7: 4,
        8: 4,
        9: 4,
        10: 4,
        11: 4,
        12: 4,
        13: 4
    }
    return numCoinsMapping[numCoins]

def getOneHotEncodeState(orderedPlayers: list[Player]):
    orderedNumCards = [p.numCards for p in orderedPlayers]
    orderedNumCoinBrackets = [mapNumCoinsToBracket(p.numCoins) for p in orderedPlayers]
    oneHotInputsCards = torch.cat([F.one_hot(torch.tensor(i), num_classes=3) for i in orderedNumCards]) #).float()
    oneHotInputsCoins = torch.cat([F.one_hot(torch.tensor(j), num_classes=5) for j in orderedNumCoinBrackets])
    allOneHotInputs = torch.cat([oneHotInputsCards, oneHotInputsCoins]).float()
    return allOneHotInputs


if __name__ == "__main__":
    env = CoupEnvironment()
    # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
    # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
    policyNet = PolicyNetwork(32, 13)
    optimizer = optim.Adam(policyNet.parameters(), lr=1e-2)
    currWins: int = 0
    winPercentageOverTime: list[float] = []
    numGames = 10000
    for i in range(numGames):
        env.reset()
        for agent in env.agent_iter():
            reward, done, info = env.rewards[agent.id], env.dones[agent.id], {}
            if done:
                action = None
                actionProb = None
            else:
                if agent.id == 0:
                    actionMask: list[np.int8] = GameMethods.getActionMask(agent, env.agents)
                    opps = [a for a in env.agents if a.id != agent.id]
                    opps.sort(key= lambda a: (a.numCards, a.numCoins), reverse = True)
                    encodedState = getOneHotEncodeState([agent, opps[0], opps[1], opps[2]])
                    actionList = policyNet(encodedState)
                    actionList[~torch.tensor(actionMask, dtype=torch.bool)] = float('-inf')
                    actionList = F.softmax(actionList, dim=0)
                    print(f"Action list: {actionList}")
                    action = torch.multinomial(actionList, 1).item()
                    actionProb = actionList[action].item()
                else:
                    action = agent.makeMove(env.agents, env.actionLog)
                    actionProb = 1 # Shouldn't affect

            env.step(action, agent, actionProb)
            env.render()

            if [a.numCards for a in env.agents if a.id == 0][0] == 0: #If p0 is out, collect their ranking and end
                p0Place = len([a for a in env.agents if a.numCards > 0]) + 1
                break

            if len([True for d in env.dones if not d]) == 1: #If only one player is left, it is p0 based on above condition
                p0Place = 1
                break 
        p0Moves = [a for a in env.actionLog if a.playerId == 0]
        p0NumberOfKills = len([a for a in p0Moves if a.action in [
            MoveWithTarget.COUPPLAYER1,
            MoveWithTarget.COUPPLAYER2,
            MoveWithTarget.COUPPLAYER3,
            MoveWithTarget.ASSASSINATEPLAYER1,
            MoveWithTarget.ASSASSINATEPLAYER2,
            MoveWithTarget.ASSASSINATEPLAYER3]])
        print(f"Number of p0 kills: {p0NumberOfKills}")
        
        policyLoss = [reward * -log(action.actionProb) for reward, action in zip(computeDiscountedRewards(len(p0Moves)), p0Moves)]
        policLossKillCountConstant = 1 - p0NumberOfKills # Killing less than one card is punished, killing more than one is rewarded
        policyLossRankMultiplierDict = {
            1: -2,
            2: -1,
            3: 2,
            4: 3
        }
        policyMultiplierOverall = policyLossRankMultiplierDict[p0Place] + policLossKillCountConstant
        policyLoss = [p*policyMultiplierOverall for p in policyLoss]

        if env.agents[0].numCards > 0:
            currWins += 1
        winPercentageOverTime.append(currWins/(i+1))

        optimizer.zero_grad()
        policyLoss = torch.tensor(policyLoss, dtype=torch.float32, requires_grad=True).sum()
        print(f"policy loss =: {policyLoss}")
        policyLoss.backward()
        optimizer.step()
    
    env.close()

    #Test States
    oneHotEncodedStateCoupAvailable = [
        0,0,1,
        0,0,1,
        0,0,1,
        0,0,1,
        0,0,0,0,1,
        0,0,1,0,0,
        0,1,0,0,0,
        1,0,0,0,0]
    print(f"Action list for start of game: {F.softmax(policyNet(torch.Tensor(oneHotEncodedStateCoupAvailable)), dim=0)}")
    
    oneHotEncodedStateAbleToEndGame = [
        0,1,0,
        0,1,0,
        1,0,0,
        1,0,0,
        0,0,0,0,1,
        0,1,0,0,0,
        0,0,1,0,0,
        1,0,0,0,0]
    actionList = policyNet(torch.Tensor(oneHotEncodedStateAbleToEndGame))
    actionList[~torch.tensor([1,1,1,0,0,1,1,0,0,1,0,0,1], dtype=torch.bool)] = float('-inf')
    print(f"Action list for game ending move: {F.softmax(actionList, dim=0)}")

    

    plt.plot(range(numGames), winPercentageOverTime, marker='o', linestyle='-')
    plt.xlabel("Games played")
    plt.ylabel("Win percentage")
    plt.title("Win percentage over time")
    plt.show()