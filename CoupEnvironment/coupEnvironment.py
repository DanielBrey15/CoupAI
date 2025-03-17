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
        opps.sort(key= lambda agent: (agent.numCards, agent.numCoins))
        sortedOppIds = [opp.id for opp in opps]
        oppRankToIdDictionary = {i: sortedOppIds[i] for i in range(3)}
        moveWithTarget = MoveWithTarget(action)
        move, targetId = self.splitMoveAndTarget(moveWithTarget, oppRankToIdDictionary)
        target = None if targetId == None else self.agents[targetId]
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

if __name__ == "__main__":
    env = CoupEnvironment()
    policyNet = PolicyNetwork(8, 13)
    optimizer = optim.Adam(policyNet.parameters(), lr=1e-3)
    for i in range(1000):
        env.reset()

        for agent in env.agent_iter():
            reward, done, info = env.rewards[agent.id], env.dones[agent.id], {}
            if done:
                action = None
                actionProb = None
            else:
                actionMask: list[np.int8] = GameMethods.getActionMask(agent, env.agents)
                opps = [a for a in env.agents if a.id != agent.id]
                opps.sort(key= lambda a: (a.numCards, a.numCoins))
                state = torch.tensor([agent.numCards, agent.numCoins, opps[0].numCards, opps[0].numCoins, opps[1].numCards, opps[1].numCoins, opps[2].numCards, opps[2].numCoins]).float()
                actionList = policyNet(state)
                print("actionList before softmax")
                print(actionList)
                actionList[~torch.tensor(actionMask, dtype=torch.bool)] = float('-inf')
                actionList = F.softmax(actionList, dim=0)
                print("actionList after softmax")
                print(actionList)
                action = torch.multinomial(actionList, 1).item()
                print(agent.id)
                print(MoveWithTarget(action))
                print(actionList[action].item())
                actionProb = actionList[action].item()

            env.step(action, agent, actionProb)
            env.render()

            if len([True for d in env.dones if not d]) == 1:
                break
        p0Moves = [a for a in env.actionLog if a.playerId == 0]
        policyLoss = [reward * -log(action.actionProb) for reward, action in zip(computeDiscountedRewards(len(p0Moves)), p0Moves)]
            
        if env.agents[0].numCards > 0:
            policyLoss = [-p for p in policyLoss]
        optimizer.zero_grad()
        policyLoss = torch.tensor(policyLoss, dtype=torch.float32, requires_grad=True).sum()
        policyLoss.backward()
        optimizer.step()
 
    env.close()