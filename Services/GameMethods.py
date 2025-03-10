from Objects.Move import Move
from Objects.Card import Card
from Players.Player import Player
from Players.AIPlayerWhoTargetsBasedOnActions import AIPlayerWhoTargetsBasedOnActions
from Services.InputWrapper import wrapInput
import random
from Objects.Action import *
from Services.ActionLogger import ActionLogger

class GameMethods:
    def checkGameOver(players: list[Player]) -> bool:
        return len(players) == 1

    def checkDeaths(playerOrder: list[Player]):
        for i in range(len(playerOrder)):
            if playerOrder[i].getNumCards() == 0:
                return i
        return -1
    
    def isSuccessfullyCalledOut(
        self,
        card: Card,
        playerMoving: Player,
        players: list[Player],
        deck: list[Card],
        setDeck,
        actionLog: list[Action]) -> bool:

        isCalledOut = False
        playerCallingOut = None
        for player in players:
            if(player.getName() != playerMoving.getName()):
                if(player.callsActionOut()):
                    ActionLogger.logAction(
                        action=CallOutAction(
                            playerActing=playerMoving,
                            playerCallingOut=player,
                            cardActing=card),
                        actionLog=actionLog)
                    isCalledOut = True
                    playerCallingOut = player
                    break
        if not isCalledOut:
            return False
        else:
            haveCard = card in playerMoving.getCards()
            if haveCard:
                playerCallingOut.loseCard()
                tempDeck = deck
                
                # Add playerMoving's card to deck and shuffle before handing them card back
                tempDeck.append(card)
                random.shuffle(tempDeck)

                cardDrawn: Card = tempDeck.pop()
                print(f"New card gained: {str(cardDrawn)}")
                setDeck(tempDeck)
                playerMoving.switchCard(cardSwitchedOut = card, cardGained = cardDrawn)
                return False
            else:
                playerMoving.loseCard()
                return True
        
    def resolveMove(self,
        player: Player,
        move: Move,
        isBlocked: bool,
        players: list[Player],
        deck: list[Card],
        setDeck, #TODO - what is function?
        actionLog: list[Action]) -> None:

        if move == Move.INCOME:
            player.updateNumCoins(1)
        elif move == Move.FOREIGNAID:
            if not isBlocked(playerMoving = player, move = Move.FOREIGNAID, potentialBlockingCard = Card.DUKE):
                player.updateNumCoins(2)
        elif move == Move.TAX:
            if not self.isSuccessfullyCalledOut(self, card=Card.DUKE, playerMoving=player, players=players, deck=deck, setDeck=setDeck, actionLog=actionLog):
                player.updateNumCoins(3)
        elif move == Move.EXCHANGE:
            if not self.isSuccessfullyCalledOut(self, card=Card.AMBASSADOR, playerMoving=player, players=players, deck=deck, setDeck=setDeck, actionLog=actionLog):
                print(f"{player.getName()} exchanges!")
                exchangeCards: list[Card] = deck[:2]
                cardsReturned: list[Card] = player.resolveExchange(exchangeCards, self)
                deckAfterExchanging: list[Card] = deck[2:]
                deckAfterExchanging.extend(cardsReturned)
                random.shuffle(deckAfterExchanging)
                setDeck(deckAfterExchanging)
        elif move == Move.COUP:
            player.updateNumCoins(-7)
            target = player.acquireTarget(players, Move.COUP, actionLog)
            target.loseCard()
        elif move == Move.STEAL:
            target = player.acquireTarget(players, Move.STEAL, actionLog)
            if not self.isSuccessfullyCalledOut(self, card=Card.CAPTAIN, playerMoving=player, players=players, deck=deck, setDeck=setDeck, actionLog=actionLog):
                if not isBlocked(playerMoving = player, move = Move.STEAL, target = target):
                    coinsStolen = min(2, target.getNumCoins())
                    player.updateNumCoins(coinsStolen)
                    target.updateNumCoins(-coinsStolen)
        elif move == Move.ASSASSINATE:
            player.updateNumCoins(-3)
            target = player.acquireTarget(players, Move.ASSASSINATE, actionLog)
            if not self.isSuccessfullyCalledOut(self, card=Card.ASSASSIN, playerMoving=player, players=players, deck=deck, setDeck=setDeck, actionLog=actionLog):
                if not isBlocked(playerMoving = player, move = Move.ASSASSINATE, target = target, potentialBlockingCard = Card.CONTESSA):
                    target.loseCard()
        else:
            print("Shouldn't hit here")
        return
    
    def getPlayerByName(self, name: str) -> Player:
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def validateMove(self, player: Player, move: Move) -> bool:
        if move == Move.COUP:
            return player.getNumCoins() >= 7
        if move == Move.ASSASSINATE:
            return player.getNumCoins() >= 3 and player.getNumCoins() < 10
        if move in (Move.INCOME, Move.FOREIGNAID, Move.TAX, Move.EXCHANGE, Move.STEAL):
            return player.getNumCoins() < 10
        
    def getPlayers(self) -> list[Player]:
        return self.players
    
    # def getAllDeadCards(players) -> list[Card]:
    #     deadCards = []
    #     for player in self.getPlayers():
    #         for deadCard in player.getDeadCards():
    #             deadCards.append(deadCard)
    #     return deadCards
    
    def createDeck(players: list[Player]) -> list[Card]:
        deck: list[Card] = []
        for card in Card:
            deck.extend([card, card, card])
        for player in players:
            for card in player.getCards():
                deck.remove(card)
        random.shuffle(deck)
        print(f"Deck: {', '.join(str(card) for card in deck)}")
        return deck
    
    def createDeckAndPlayers():
        players: list[Player] = []
        deck: list[Card] = []
        for card in Card:
            deck.extend([card, card, card])
        random.shuffle(deck)
        for p in range(4):
            pCards, deck = deck[:2], deck[2:]
            players.append(AIPlayerWhoTargetsBasedOnActions(pCards[0], pCards[1], f"p{p}"))
        return deck, players


    def getDeck(self) -> list[Card]:
        return self.deck