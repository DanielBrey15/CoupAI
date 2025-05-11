import sys
import random
import numpy as np
from typing import Optional
from progress.bar import Bar
import matplotlib.pyplot as plt
import torch
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
        self.move_log: list[MoveLogEntry] = []
        self.game_log: list[GameLog] = []
        self.player_ids_ranked: list[int] = []

        # Actions: Income, Foreign Aid, Coup Opp A, Coup Opp B, Coup Opp C, Tax, Steal Opp A, Steal Opp B, Steal Opp C, Assassinate Opp A, Assassinate Opp B, Assassinate Opp C, Exchange
        self.action_spaces = {agent.id: spaces.Discrete(13) for agent in self.agents}
        self.observation_spaces = {agent.id: spaces.Discrete(1) for agent in self.agents}

    def __str__(self):
        game_status = "\nGame Status: [\n"
        for player in self.agents:
            game_status += str(player) + "\n"
        return game_status[:-1] + " ]"

    def reset(self) -> None:
        deck = GameMethods.resetDeckAndPlayers(self.agents)
        self.deck: list[Card] = deck
        self.agent_selection = self.agents[0]
        self.rewards = {agent.id: 0 for agent in self.agents}
        self.dones = {agent.id: False for agent in self.agents}
        self.move_log: list[MoveLogEntry] = []
        self.player_ids_ranked: list[int] = []

    def step(self, action, agent, action_prob) -> None:
        opps = [a for a in self.agents if a.id != agent.id]
        opps.sort(key= lambda player: (player.num_cards, player.num_coins), reverse = True)
        sorted_opp_ids = [opp.id for opp in opps]
        opp_rank_to_id_dictionary = {i: sorted_opp_ids[i] for i in range(3)}
        move_with_target = MoveWithTarget(action)
        move, target_id = GameMethods.splitMoveAndTarget(move_with_target, opp_rank_to_id_dictionary)
        target = None if target_id is None else next(a for a in self.agents if a.id == target_id) #CHECK
        MoveLogger.logMove(
            curr_player = agent,
            sorted_opps = opps,
            action = move_with_target,
            action_prob = action_prob,
            move_log = self.move_log
        )
        loss = GameMethods.resolveMove(GameMethods, agent, move, target, self.isBlocked, self.agents, self.deck, self.setDeck, move_log = env.move_log)
        MoveLogger.updatePreviousReward(self.move_log, loss)

        env.dones = [agent.num_cards == 0 for agent in env.agents]

        next_agent_id = (agent.id + 1) % self.num_agents
        while self.dones[next_agent_id]:
            next_agent_id = (next_agent_id + 1) % self.num_agents
        self.agent_selection = self.agents[next_agent_id]

    def isBlocked(self, player_moving, move, target = None, potential_blocking_card = None) -> bool:
        players = self.agents
        blocking_player: Optional[Player] = None
        card_AI_blocks_with: Optional[Card] = None
        for player in players:
            card_AI_blocks_with = player.AIBlock(player_moving, move, target)
            if card_AI_blocks_with:
                blocking_player = player
                break
        if blocking_player:
            if not GameMethods.isSuccessfullyCalledOut(GameMethods, card=card_AI_blocks_with, player_moving=blocking_player, players=self.agents, deck=self.deck, setDeck=self.setDeck, move_log=self.move_log):
                return True
            return False
        return False

    def setPlayers(self, new_players) -> None:
        self.players = new_players

    def setDeck(self, new_deck) -> None:
        self.deck = new_deck

    def render(self) -> None:
        print(self)

if __name__ == "__main__":
    # Note: Some things are unecessary in this file (such as the action probabilities),
    # but I am going to be using them in the near future so it doesn't make sense to remove it yet.
    if len(sys.argv) != 2:
        raise ValueError("Usage: python3 CoupEnvironment.py <numberOfGames>")
    num_games = int(sys.argv[1])

    env = CoupEnvironment()
    playerUpdater = PlayerUpdater(env.agents)

    # Keeping track of win percentage to visualize model's growth
    curr_wins: int = 0
    win_percentage_over_time: list[float] = []

    SEED = 32

    # Seed all common libraries
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    bar = Bar('Completing games', max = num_games)

    for i in range(num_games):
        env.reset()
        for agent in env.agent_iter():
            if env.dones[agent.id]:
                action = None
                log_action_prob = None
            else:
                action, log_action_prob = agent.makeMove(env.agents, env.move_log)

            env.step(action, agent, log_action_prob)

            # Check if any players lost their last card and if that caused the end of the game
            new_dead_player_IDs = [p.id for p in env.agents if p.num_cards == 0 and p.id not in env.player_ids_ranked]
            if len(new_dead_player_IDs) > 0:
                env.player_ids_ranked.extend(new_dead_player_IDs)
            if len(env.player_ids_ranked) == 3: # One player left - Game is over
                playerIdAlive = [p.id for p in env.agents if p.num_cards > 0][0]
                env.player_ids_ranked.append(playerIdAlive)
                break
            #print(f"{agent.id} move: {action}")
            #print(env)
        playerUpdater.updatePlayers(env.move_log, env.player_ids_ranked)

        if env.agents[0].num_cards > 0:
            curr_wins += 1
        win_percentage_over_time.append(curr_wins/(i+1))

        bar.next()
    playerUpdater.storePlayerModels()
    bar.finish()
    env.close()

    plt.plot(range(100,num_games), win_percentage_over_time[100:], color='blue', marker='o', linestyle='-')
    plt.xlabel("Games played")
    plt.ylabel("Win percentage")
    plt.title("Win percentage over time")
    plt.show()
