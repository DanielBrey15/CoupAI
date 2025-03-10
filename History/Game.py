from Players.AIPlayer import AIPlayer
from Objects.Move import Move
from Objects.Card import Card
from Players.Player import Player
import copy
import random
from Services.InputWrapper import wrapInput

class Game:
    def __init__(self):
        self.players: list[Player] = self.createPlayers()
        self.deck: list[Card] = self.createDeck()
    
    def __str__(self):
        gameStatus = "\nGame Status:\n"
        for player in self.players:
            gameStatus += str(player) + "\n"
        return gameStatus[:-2] + " ]"

    def PlayGame(self):
        playerOrder = copy.copy(self.players)
        while (not self.checkGameOver(playerOrder)):
            print(self)
            playerMoving = playerOrder.pop(0)

            if not playerMoving.getIsAI():
                move = self.retrieveMove(playerMoving)
                self.resolveMove(playerMoving, move)
            else:
                print(f"{playerMoving.name}'s turn")
                aiMove = playerMoving.makeMove(self)
                print(f"{playerMoving.name} will do " + str(aiMove))
                self.resolveMove(playerMoving, aiMove)
            
            playerOrder.append(playerMoving)
            
            deadPlayer = self.checkDeaths(playerOrder)
            if deadPlayer != -1:
                playerOrder.pop(deadPlayer)
        return


    def checkGameOver(self, playerOrder): #MOVED
        return len(playerOrder) == 1

    def checkDeaths(self, playerOrder): #MOVED
        for i in range(len(playerOrder)):
            if playerOrder[i].getNumCards() == 0:
                return i
        return -1

    def isBlocked(self, playerMoving, move, target = None, potentialBlockingCard = None):
        cardCG32BlocksWith = self.getPlayerByName("cg32").AIBlock(playerMoving, move, target)
        if target:
            isBlockedString = wrapInput(f"\nDoes {target} block? \n Type either Yes or No: ").capitalize() if target != self.getPlayerByName("cg32") else "No"
        else:
            isBlockedString = wrapInput("\nDo any players block? \n Type either Yes or No: ").capitalize()
        if isBlockedString == "Yes":
            blockingPlayer = target
            blockingCard = potentialBlockingCard
            if move == Move.FOREIGNAID:
                blockingPlayer = self.getPlayerByName(wrapInput("Who blocks? "))
            elif move == Move.STEAL:
                blockingCard = Card[wrapInput("Block with what? Type either Captain or Ambassador").upper()]

            if not self.isSuccessfullyCalledOut(blockingCard, blockingPlayer):
                return True
        elif isBlockedString == "No":
            if cardCG32BlocksWith:
                print(f"\nAI blocks with {cardCG32BlocksWith}")
                if not self.isSuccessfullyCalledOut(cardCG32BlocksWith, self.getPlayerByName("cg32")):
                    return True
                return False
            return False
        else:
            print("Invalid answer")
            return self.isBlocked(playerMoving, move, target)

    def isSuccessfullyCalledOut(self, card: Card, playerMoving: Player) -> bool: #MOVED
        isCalledOutString = wrapInput("\n Do any players call this action out? \n Type either Yes or No: ").capitalize()
        if isCalledOutString == "Yes":
            callingOutPlayer = wrapInput("Who is calling out? ")
            print(f"{playerMoving.getName()} must reveal {card} \n")
            haveCard = card in playerMoving.getCards()
            if haveCard:
                self.getPlayerByName(callingOutPlayer).loseCard()
                tempDeck = self.deck
                
                # Add player's card to deck and shuffle before handing them card back
                tempDeck.append(card)
                random.shuffle(tempDeck)

                cardDrawn: Card = tempDeck.pop()
                print(f"New card gained: {str(cardDrawn)}")
                self.deck = tempDeck
                playerMoving.switchCard(cardSwitchedOut = card, cardGained = cardDrawn)
                return False
            else:
                playerMoving.loseCard()
                return True
        elif isCalledOutString == "No":
            if self.getPlayerByName("cg32").AICallOut(card):
                print(f"{playerMoving.getName()} must reveal {card} \n")
                haveCard = card in playerMoving.getCards()
                if haveCard:
                    self.getPlayerByName("cg32").loseCard()
                    return False
                else:
                    playerMoving.loseCard()
                    return True
            else:
                return False
        else:
            print("Invalid answer")
            return self.isSuccessfullyCalledOut(card, playerMoving)

    def createPlayers(self):
        if wrapInput("Auto setup: Type Yes or No: ").capitalize() == "Yes": #4 players (p1, p2, p3, CoupGod32), ai has duke and ambassador, p1 has duke and contessa, p2 has captain and ambassador, p3 has contessa and assassin
            return [Player("p1", Card.DUKE, Card.CONTESSA), Player("p2", Card.CAPTAIN, Card.AMBASSADOR), Player("p3", Card.CONTESSA, Card.ASSASSIN), AIPlayer(Card.DUKE, Card.AMBASSADOR)]
        else:
            print("Let's first add the different players \n")
            numPlayers = int(wrapInput("Num Players: "))
            #for each player, create player class and add it to an array
            players = []
            print("Add players in turn order (Ignoring me).")
            for i in range(1, numPlayers):
                name = str(wrapInput("Player " + str(i) + "'s name: "))
                card1 = Card[wrapInput("First card: ").upper()]
                card2 = Card[wrapInput("second card: ").upper()]
                player = Player(name, card1, card2) 
                players.append(player)
            #create ai player
            aiTurn = int(wrapInput("Ok which place in the order am I playing? "))
            aiCard1 = Card[wrapInput("First card: ").upper()]
            aiCard2 = Card[wrapInput("Second card: ").upper()]
            aiPlayer = AIPlayer(aiCard1, aiCard2)
            players.insert(aiTurn-1, aiPlayer)
            return players

    def resolveMove(self, player, move): #MOVED
        if move == Move.INCOME:
            player.updateNumCoins(1)
        elif move == Move.FOREIGNAID:
            if not self.isBlocked(playerMoving = player, move = Move.FOREIGNAID, potentialBlockingCard = Card.DUKE):
                player.updateNumCoins(2)
        elif move == Move.TAX:
            if not self.isSuccessfullyCalledOut(Card.DUKE, player):
                player.updateNumCoins(3)
        elif move == Move.EXCHANGE:
            if not self.isSuccessfullyCalledOut(Card.AMBASSADOR, player):
                print(f"{player.getName()} exchanges!")
                exchangeCards: list[Card] = self.deck[:2]
                cardsReturned: list[Card] = player.resolveExchange(exchangeCards, self)
                deckAfterExchanging: list[Card] = self.deck[2:]
                deckAfterExchanging.extend(cardsReturned)
                random.shuffle(deckAfterExchanging)
                self.deck = deckAfterExchanging
        elif move == Move.COUP:
            player.updateNumCoins(-7)
            target = player.acquireTarget(self)
            target.loseCard()
        elif move == Move.STEAL:
            target = player.acquireTarget(self)
            if not self.isSuccessfullyCalledOut(Card.CAPTAIN, player):
                if not self.isBlocked(playerMoving = player, move = Move.STEAL, target = target):
                    coinsStolen = min(2, target.getNumCoins())
                    player.updateNumCoins(coinsStolen)
                    target.updateNumCoins(-coinsStolen)
        elif move == Move.ASSASSINATE:
            player.updateNumCoins(-3)
            target = player.acquireTarget(self)
            if not self.isSuccessfullyCalledOut(Card.ASSASSIN, player):
                if not self.isBlocked(playerMoving = player, move = Move.ASSASSINATE, target = target, potentialBlockingCard = Card.CONTESSA):
                    target.loseCard()
        else:
            print("Shouldn't hit here")
        return

    def getPlayerByName(self, name): #MOVED
        for player in self.players:
            if player.name == name:
                return player
        return None

    def validateMove(self, player, move): #MOVED
        if move == Move.COUP:
            return player.getNumCoins() >= 7
        if move == Move.ASSASSINATE:
            return player.getNumCoins() >= 3 and player.getNumCoins() < 10
        if move in (Move.INCOME, Move.FOREIGNAID, Move.TAX, Move.EXCHANGE, Move.STEAL):
            return player.getNumCoins() < 10

    def retrieveMove(self, playerMoving):
        try:
            move = Move[wrapInput(f"\n{playerMoving.name}'s turn: ").upper()]
            if(self.validateMove(playerMoving, move)):
                return move
            else:
                print("Invalid move")
                return self.retrieveMove(playerMoving)
        except ValueError:
            raise ValueError("Quit")
        except:
            print("Invalid move")
            return self.retrieveMove(playerMoving)

    def getPlayers(self) -> list[Player]: #MOVED
        return self.players
    
    def getAllDeadCards(self) -> list[Card]: #MOVED
        deadCards = []
        for player in self.getPlayers():
            for deadCard in player.getDeadCards():
                deadCards.append(deadCard)
        return deadCards

    def createDeck(self): #MOVED
        deck: list[Card] = []
        for card in Card:
            deck.extend([card, card, card])
        for player in self.getPlayers():
            for card in player.getCards():
                deck.remove(card)
        random.shuffle(deck)
        print(f"Deck: {', '.join(str(card) for card in deck)}")
        return deck

    def getDeck(self) -> list[Card]: #MOVED
        return self.deck
    

def printIntro():
    print("Yo I'm CoupGod32 and I'm here to catch dubs. \n")
    return

with open("Game.py") as my_file:
    printIntro()
    game = Game()
    game.PlayGame()