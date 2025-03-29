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
from math import log
import matplotlib.pyplot as plt
from Objects.GameLog import GameLog

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
    
    def setPlayers(self, newPlayers) -> None:
        self.players = newPlayers

    def setDeck(self, newDeck) -> None:
        self.deck = newDeck

    def render(self) -> None:
        print(self)

if __name__ == "__main__":
    # Note: Some things are unecessary in this file (such as the action probabilities),
    # but I am going to be using them in the near future so it doesn't make sense to remove it yet.
    env = CoupEnvironment()
    currWins: int = 0
    winPercentageOverTime: list[float] = []
    numGames = 200
    for i in range(numGames):
        env.reset()
        for agent in env.agent_iter():
            reward, done, info = env.rewards[agent.id], env.dones[agent.id], {}
            if done:
                action = None
                logActionProb = None
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

        if env.agents[0].numCards > 0:
            currWins += 1
        winPercentageOverTime.append(currWins/(i+1))

    env.close()

    plt.plot(range(100,numGames), winPercentageOverTime[100:], marker='o', linestyle='-')
    plt.xlabel("Games played")
    plt.ylabel("Win percentage")
    plt.title("Win percentage over time")
    plt.show()