from Players.AIPlayer import AIPlayer
from Players.AIPlayer2 import AIPlayer2
from Players.AIPlayerWhoTargetsBasedOnActions import AIPlayerWhoTargetsBasedOnActions
from Objects.Card import Card
from Objects.Move import Move
import copy
from typing import Optional
from Services.InputWrapper import wrapInput
from Services.GameMethods import *
from Objects.Action import *
from Services.ActionLogger import ActionLogger
import csv

class AIGame:
    def __init__(self):
        deck, players = GameMethods.createDeckAndPlayers()
        self.players: list[AIPlayer] =  players #self.createPlayers()
        self.deck: list[Card] = deck #GameMethods.createDeck(self.players)
        self.actionLog: list[Action] = []

    def __str__(self):
        gameStatus = "\nGame Status: [\n"
        for player in self.players:
            gameStatus += str(player) + "\n"
        return gameStatus[:-1] + " ]"

    def PlayGame(self):
        playerOrder = copy.copy(self.players)
        while (not GameMethods.checkGameOver(playerOrder)):
            print(self)
            playerMoving = playerOrder.pop(0)

            move = playerMoving.makeMove(self.players, self.actionLog)
            print(f"{playerMoving.name} will do " + str(move))
            ActionLogger.logAction(
                action= MoveAction(
                    playerMoving=playerMoving,
                    move= move,
                    target=None
                ),
                actionLog=self.actionLog)
            GameMethods.resolveMove(GameMethods, playerMoving, move, self.isBlocked, self.players, self.deck, self.setDeck, actionLog=self.actionLog)
            
            playerOrder.append(playerMoving)
            
            deadPlayer = GameMethods.checkDeaths(playerOrder)
            if deadPlayer != -1:
                playerOrder.pop(deadPlayer)
        return

    def isBlocked(self, playerMoving, move, target = None, potentialBlockingCard = None):
        players = self.players
        blockingPlayer: Optional[AIPlayer] = None
        cardAIBlocksWith: Optional[Card] = None
        for player in players:
            cardAIBlocksWith = player.AIBlock(playerMoving, move, target)
            if(cardAIBlocksWith):
                blockingPlayer = player
                break
        if blockingPlayer:
            print(f"\n{blockingPlayer.name} blocks with {cardAIBlocksWith}")
            ActionLogger.logAction(
                action=BlockAction(
                    playerBlocking=blockingPlayer,
                    playerBlocked=playerMoving,
                    move=move,
                    cardBlocking=cardAIBlocksWith),
                actionLog=self.actionLog)
            if move == Move.STEAL:
                self.logStealDataInCSV(
                    playerActing=playerMoving,
                    targetPlayer=blockingPlayer,
                    isBlocked=True
                )
            if not GameMethods.isSuccessfullyCalledOut(GameMethods, card=cardAIBlocksWith, playerMoving=blockingPlayer, players=self.players, deck=self.deck, setDeck=self.setDeck, actionLog=self.actionLog):
                return True
            return False
        if move == Move.STEAL:
            self.logStealDataInCSV(
                playerActing=playerMoving,
                targetPlayer=target,
                isBlocked=False
            )
        return False

    def createPlayers(self):
        if wrapInput("Auto setup: Type Yes or No: ").capitalize() == "Yes": #4 players (p1, p2, p3, CoupGod32), ai has duke and ambassador, p1 has duke and contessa, p2 has captain and ambassador, p3 has contessa and assassin
            return [AIPlayerWhoTargetsBasedOnActions(Card.DUKE, Card.CONTESSA, "p1"), AIPlayerWhoTargetsBasedOnActions(Card.CAPTAIN, Card.CAPTAIN, "p2"), AIPlayerWhoTargetsBasedOnActions(Card.CONTESSA, Card.ASSASSIN, "p3"), AIPlayerWhoTargetsBasedOnActions(Card.DUKE, Card.CAPTAIN, "p4")]
        else: #Add else if for random setup
            print("Add the different players \n")
            numPlayers = int(input("Num Players: "))
            #for each player, create player class and add it to an array
            players = []
            print("Add players in turn order (Ignoring me).")
            for i in range(1, numPlayers+1):
                name = "p" + i
                card1 = Card[wrapInput("First card: ").upper()]
                card2 = Card[wrapInput("second card: ").upper()]
                player = AIPlayer(card1, card2, name)
                players.append(player)
            return players
        
    def setPlayers(self, newPlayers):
        self.players = newPlayers

    def setDeck(self, newDeck):
        self.deck = newDeck

    def logStealDataInCSV(self, playerActing: Player, targetPlayer: Player, isBlocked: bool):
        moveActions = [a for a in self.actionLog if a.actionType == ActionType.Move]
        targetMoveActions = [a for a in moveActions if a.playerActing == targetPlayer]
        blockStealActions = [a for a in moveActions if a.actionType == ActionType.Block and a.move == Move.STEAL]
        with open("CSVs/StealData.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow({
                "TotIM": len([a for a in moveActions if a.move == Move.INCOME]),
                "TotFAM": len([a for a in moveActions if a.move == Move.FOREIGNAID]),
                "TotCM": len([a for a in moveActions if a.move == Move.COUP]),
                "TotTM": len([a for a in moveActions if a.move == Move.TAX]),
                "TotSM": len([a for a in moveActions if a.move == Move.STEAL]),
                "TotAM": len([a for a in moveActions if a.move == Move.ASSASSINATE]),
                "TotEM": len([a for a in moveActions if a.move == Move.EXCHANGE]),
                "TotBSM": len(blockStealActions),
                "TotCards": sum([player.getNumCards() for player in self.players]),
                "TarIM": len([a for a in targetMoveActions if a.move == Move.INCOME]),
                "TarFAM": len([a for a in targetMoveActions if a.move == Move.FOREIGNAID]),
                "TarCM": len([a for a in targetMoveActions if a.move == Move.COUP]),
                "TarTM": len([a for a in targetMoveActions if a.move == Move.TAX]),
                "TarSM": len([a for a in targetMoveActions if a.move == Move.STEAL]),
                "TarAM": len([a for a in targetMoveActions if a.move == Move.ASSASSINATE]),
                "TarEM": len([a for a in targetMoveActions if a.move == Move.EXCHANGE]),
                "TarBSM": len([a for a in blockStealActions if a.playerActing == targetPlayer]),
                "TarCards": targetPlayer.getNumCards(),
                "TarCoins": targetPlayer.getNumCoins(),
                "MyCards": playerActing.getNumCards(),
                "MyCoins": playerActing.getNumCoins(),
                "IsBlocked": isBlocked
            }.values())
        return

with open("AIGame.py") as my_file:
    game = AIGame()
    game.PlayGame()