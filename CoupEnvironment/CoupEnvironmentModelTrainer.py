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
        self.move_log: list[MoveLogEntry] = []
        self.game_log: list[GameLog] = []

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
        self.move_log: list[MoveLogEntry] = []

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
            move_log = self.move_log 
        )
        GameMethods.resolveMove(GameMethods, agent, move, target, self.isBlocked, self.agents, self.deck, self.setDeck, move_log = env.move_log)

        env.dones = [agent.numCards == 0 for agent in env.agents]

        nextAgentId = (agent.id + 1) % self.num_agents
        while self.dones[nextAgentId]:
            nextAgentId = (nextAgentId + 1) % self.num_agents
        self.agent_selection = self.agents[nextAgentId]
        return
    
    def isBlocked(self, player_moving, move, target = None, potential_blocking_card = None) -> bool:
        players = self.agents
        blocking_player: Optional[Player] = None
        card_AI_blocks_with: Optional[Card] = None
        for player in players:
            card_AI_blocks_with = player.AIBlock(player_moving, move, target)
            if(card_AI_blocks_with):
                blocking_player = player
                break
        if blocking_player:
            print(f"\n{blocking_player.name} blocks with {card_AI_blocks_with}")
            if not GameMethods.isSuccessfullyCalledOut(GameMethods, card=card_AI_blocks_with, player_moving=blocking_player, players=self.agents, deck=self.deck, setDeck=self.setDeck, move_log=self.move_log):
                return True
            return False
        return False
    
    def logGame(self, game_num: int, rank: int, num_kills: int, policy_loss: float, chance_of_coup_in_game_winning_state: float, chance_of_assassinate_in_game_winning_state: float):
        self.game_log.append(GameLog(game_num, rank, num_kills, policy_loss, chance_of_coup_in_game_winning_state, chance_of_assassinate_in_game_winning_state))

    def logGameDataInCSV(self, win_percentage: float) -> None:
        with open("CSVs/GameData.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f"### Training new model - Win Percentage: {win_percentage*100}%"])
            writer.writerow({
                "game_num": "game_num",
                "Rank": "Rank",
                "num_kills": "num_kills",
                "policy_loss": "policy_loss",
                "chance_of_coup_in_game_winning_state": "chance_of_coup_in_game_winning_state",
                "chance_of_assassinate_in_game_winning_state": "chance_of_assassinate_in_game_winning_state",
            }.values())
            for game in env.game_log:
                writer.writerow({
                "game_num": game.game_num,
                "Rank": game.rank,
                "num_kills": game.num_kills,
                "policy_loss": game.policy_loss,
                "chance_of_coup_in_game_winning_state": game.chance_of_coup_in_game_winning_state,
                "chance_of_assassinate_in_game_winning_state": game.chance_of_assassinate_in_game_winning_state,
            }.values())
        return

    def setPlayers(self, new_players) -> None:
        self.players = new_players

    def setDeck(self, new_deck) -> None:
        self.deck = new_deck

    def render(self) -> None:
        print(self)

if __name__ == "__main__":
    env = CoupEnvironmentModelTrainer()

    # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
    # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
    policy_net = PolicyNetwork(32, 13)

    policy_net.load_state_dict(torch.load("ModelFiles/Model1.pt", weights_only=True))
    optimizer = optim.Adam(policy_net.parameters(), lr=1e-4)

    # Keeping track of win percentage to visualize model's growth
    curr_wins: int = 0
    win_percentage_over_time: list[float] = []

    num_games = 20
    for i in range(num_games):
        env.reset()
        for agent in env.agent_iter():
            reward, done, info = env.rewards[agent.id], env.dones[agent.id], {}
            if done:
                action = None
                log_action_prob = None
            else:
                if agent.id == 0:
                    action_mask: list[np.int8] = PlayerMethods.getActionMask(agent, env.agents)
                    opps = [a for a in env.agents if a.id != agent.id]
                    opps.sort(key= lambda a: (a.numCards, a.numCoins), reverse = True)
                    encoded_state = PlayerMethods.getOneHotEncodeState([agent, opps[0], opps[1], opps[2]])
                    action_list = policy_net(encoded_state)
                    action_list[~torch.tensor(action_mask, dtype=torch.bool)] = float('-inf')
                    action_list = F.softmax(action_list, dim=0)
                    action = torch.multinomial(action_list, 1).item()
                    log_action_prob = torch.log1p(action_list[action] - 1)
                else:
                    action = agent.makeMove(env.agents, env.move_log)
                    log_action_prob = torch.tensor(1) # Shouldn't affect

            env.step(action, agent, log_action_prob)
            env.render()

            if [a.numCards for a in env.agents if a.id == 0][0] == 0: #If p0 is out, collect their ranking and end
                p0_place = len([a for a in env.agents if a.numCards > 0]) + 1
                break

            if len([True for d in env.dones if not d]) == 1: #If only one player is left, it is p0 based on above condition
                p0_place = 1
                break 
        p0_moves = [a for a in env.move_log if a.playerId == 0]
        p0_number_of_kills = len([a for a in p0_moves if a.action in Constants.LIST_OF_KILL_MOVES])
        
        rewards = torch.tensor(GameMethods.computeDiscountedRewards(len(p0_moves)), dtype=torch.float32, device=log_action_prob.device)
        policy_loss = torch.stack([reward * action.actionProb for reward, action in zip(rewards, p0_moves)]).sum()
        policLossKillCountConstant = 1 - p0_number_of_kills # Killing less than one card is punished, killing more than one is rewarded
        
        policyMultiplierOverall = torch.tensor(Constants.POLICY_LOSS_MULTIPLIER_BY_RANK_DICTIONARY[p0_place] + policLossKillCountConstant, dtype=torch.float32, device=policy_loss.device)
        policy_loss = policyMultiplierOverall * policy_loss

        if env.agents[0].numCards > 0:
            curr_wins += 1
        win_percentage_over_time.append(curr_wins/(i+1))

        optimizer.zero_grad()

        action_list_test_case = policy_net(torch.Tensor(Constants.ONE_HOT_ENCODED_STATE_TO_WIN_GAME))
        action_list_test_case[~torch.tensor(Constants.ACTION_MASK_FOR_STATE_TO_WIN_GAME, dtype=torch.bool)] = float('-inf')
        action_list_test_case = F.softmax(action_list_test_case, dim=0)
        chance_of_coup_in_game_winning_state, chance_of_assassinate_in_game_winning_state = (0,0)
        env.logGame(
            game_num = i,
            rank = p0_place,
            num_kills = p0_number_of_kills,
            policy_loss = policy_loss.item(),
            chance_of_coup_in_game_winning_state = action_list_test_case[MoveWithTarget.COUPPLAYER1].item(),
            chance_of_assassinate_in_game_winning_state = action_list_test_case[MoveWithTarget.ASSASSINATEPLAYER1].item(),
        )

        policy_loss.backward()
        optimizer.step()

    env.logGameDataInCSV(curr_wins/num_games)
    env.close()

    torch.save(policy_net.state_dict(), "ModelFiles/Model1.pt")

    plt.plot(range(100,num_games), win_percentage_over_time[100:], marker='o', linestyle='-')
    plt.xlabel("Games played")
    plt.ylabel("Win percentage")
    plt.title("Win percentage over time")
    plt.show()


