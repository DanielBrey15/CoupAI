import sys
import random
from typing import Optional
from progress.bar import Bar
import matplotlib.pyplot as plt
from gym import spaces
from pettingzoo import AECEnv
from Objects.Card import Card
from Objects.GameLog import GameLog
from Objects.MoveWithTarget import MoveWithTarget
from Players.Player import Player
from Services.GameMethods import GameMethods
from Services.MoveLogger import MoveLogger, MoveLogEntry
from Services.PlayerUpdater import PlayerUpdater

"""
CoupEnvironment.py is my main file to run Coup. Given a number, it plays that many games of Coup
between 4 players (Players manually added in the GameMethods service).

CoupEnvironment.py uses the PlayerUpdater service to update the Coup players after each game
(Note: Only the players that are using actual models are updated. Those using heuristics are
unaffected).

Currently, the first player is an agent trained on a deep learning model while the other 3 
players use heuristics, so CoupEnvironment.py plots the first player's win percentage over
time to indicate the model's growth.

Please run "python3 CoupEnvironment.py <Number of games>"
"""
class CoupEnvironment(AECEnv):
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
        self.playerIdsRanked: list[int] = []

        self.action_spaces = {agent.id: spaces.Discrete(13) for agent in self.agents} # [Income, Foreign Aid, Coup Opp A, Coup Opp B, Coup Opp C, Tax, Steal Opp A, Steal Opp B, Steal Opp C, Assassinate Opp A, Assassinate Opp B, Assassinate Opp C, Exchange]
        self.observation_spaces = {agent.id: spaces.Discrete(1) for agent in self.agents}

    def __str__(self):
        gameStatus = "\nGame Status: [\n"
        for player in self.agents:
            gameStatus += str(player) + "\n"
        return gameStatus[:-1] + " ]"

    def reset(self, seed=32) -> None:
        deck = GameMethods.resetDeckAndPlayers(self.agents)
        self.deck: list[Card] = deck
        self.agent_selection = self.agents[0]
        self.rewards = {agent.id: 0 for agent in self.agents}
        self.dones = {agent.id: False for agent in self.agents}
        self.moveLog: list[MoveLogEntry] = []
        self.playerIdsRanked: list[int] = []

    def step(self, action, agent, actionProb) -> None:
        opps = [a for a in self.agents if a.id != agent.id]
        opps.sort(key= lambda player: (player.numCards, player.numCoins), reverse = True)
        sortedOppIds = [opp.id for opp in opps]
        oppRankToIdDictionary = {i: sortedOppIds[i] for i in range(3)}
        moveWithTarget = MoveWithTarget(action)
        move, targetId = GameMethods.splitMoveAndTarget(moveWithTarget, oppRankToIdDictionary)
        target = None if targetId is None else next(a for a in self.agents if a.id == targetId)
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

    def isBlocked(self, playerMoving, move, target = None, potentialBlockingCard = None) -> bool:
        players = self.agents
        blockingPlayer: Optional[Player] = None
        cardAIBlocksWith: Optional[Card] = None
        for player in players:
            cardAIBlocksWith = player.AIBlock(playerMoving, move, target)
            if cardAIBlocksWith:
                blockingPlayer = player
                break
        if blockingPlayer:
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
    if len(sys.argv) != 2:
        raise ValueError("Usage: python3 CoupEnvironment.py <numberOfGames>")
    numGames = int(sys.argv[1])

    env = CoupEnvironment()
    playerUpdater = PlayerUpdater(env.agents)

    # Keeping track of win percentage to visualize model's growth
    currWins: int = 0
    winPercentageOverTime: list[float] = []

    random.seed(32)
    bar = Bar('Completing games', max = numGames)

    for i in range(numGames):
        env.reset()
        for agent in env.agent_iter():
            if env.dones[agent.id]:
                action = None
                logActionProb = None
            else:
                action, logActionProb = agent.makeMove(env.agents, env.moveLog)

            env.step(action, agent, logActionProb)

            # Check if any players lost their last card and if that caused the end of the game
            newDeadPlayerIds = [p.id for p in env.agents if p.numCards == 0 and p.id not in env.playerIdsRanked]
            if len(newDeadPlayerIds) > 0:
                env.playerIdsRanked.extend(newDeadPlayerIds)
            if len(env.playerIdsRanked) == 3: # One player left - Game is over
                playerIdAlive = [p.id for p in env.agents if p.numCards > 0]
                env.playerIdsRanked.append(playerIdAlive)
                break
        playerUpdater.updatePlayers(env.moveLog, env.playerIdsRanked)

        if env.agents[0].numCards > 0:
            currWins += 1
        winPercentageOverTime.append(currWins/(i+1))

        bar.next()
    playerUpdater.storePlayerModels()
    bar.finish()
    env.close()

    plt.plot(range(100,numGames), winPercentageOverTime[100:], color='blue', marker='o', linestyle='-')
    plt.xlabel("Games played")
    plt.ylabel("Win percentage")
    plt.title("Win percentage over time")
    plt.show()
