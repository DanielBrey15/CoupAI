from Players.Player import Player
import numpy as np
from Objects.MoveWithTarget import MoveWithTarget
from Constants import Constants
import torch
import torch.nn.functional as F

class PlayerMethods:
    def getActionMask(currPlayer: Player, players: list[Player]) -> list[np.int8]:
        actionMask = np.ones(13, dtype=np.int8)
        opps = [p for p in players if p.id != currPlayer.id]
        opps.sort(key= lambda agent: (agent.numCards, agent.numCoins), reverse = True)
        if opps[0].numCards == 0:
            actionMask[MoveWithTarget.COUPPLAYER1] = 0
            actionMask[MoveWithTarget.STEALPLAYER1] = 0
            actionMask[MoveWithTarget.ASSASSINATEPLAYER1] = 0
        if opps[1].numCards == 0:
            actionMask[MoveWithTarget.COUPPLAYER2] = 0
            actionMask[MoveWithTarget.STEALPLAYER2] = 0
            actionMask[MoveWithTarget.ASSASSINATEPLAYER2] = 0
        if opps[2].numCards == 0:
            actionMask[MoveWithTarget.COUPPLAYER3] = 0
            actionMask[MoveWithTarget.STEALPLAYER3] = 0
            actionMask[MoveWithTarget.ASSASSINATEPLAYER3] = 0

        if currPlayer.numCoins < 7:
            actionMask[MoveWithTarget.COUPPLAYER1] = 0
            actionMask[MoveWithTarget.COUPPLAYER2] = 0
            actionMask[MoveWithTarget.COUPPLAYER3] = 0
            if currPlayer.numCoins < 3:
                actionMask[MoveWithTarget.ASSASSINATEPLAYER1] = 0
                actionMask[MoveWithTarget.ASSASSINATEPLAYER2] = 0
                actionMask[MoveWithTarget.ASSASSINATEPLAYER3] = 0
        elif currPlayer.numCoins >= 10:
            actionMask[MoveWithTarget.INCOME] = 0
            actionMask[MoveWithTarget.FOREIGNAID] = 0
            actionMask[MoveWithTarget.TAX] = 0
            actionMask[MoveWithTarget.STEALPLAYER1] = 0
            actionMask[MoveWithTarget.STEALPLAYER2] = 0
            actionMask[MoveWithTarget.STEALPLAYER3] = 0
            actionMask[MoveWithTarget.ASSASSINATEPLAYER1] = 0
            actionMask[MoveWithTarget.ASSASSINATEPLAYER2] = 0
            actionMask[MoveWithTarget.ASSASSINATEPLAYER3] = 0
            actionMask[MoveWithTarget.EXCHANGE] = 0
        
        return actionMask

    def getOneHotEncodeState(orderedPlayers: list[Player]):
        orderedNumCards = [p.numCards for p in orderedPlayers]
        orderedNumCoinBrackets = [Constants.NUMBEROFCOINSTOSTATEBRACKETMAPPING[p.numCoins] for p in orderedPlayers]
        oneHotInputsCards = torch.cat([F.one_hot(torch.tensor(i), num_classes=3) for i in orderedNumCards])
        oneHotInputsCoins = torch.cat([F.one_hot(torch.tensor(j), num_classes=5) for j in orderedNumCoinBrackets])
        allOneHotInputs = torch.cat([oneHotInputsCards, oneHotInputsCoins]).float()
        return allOneHotInputs