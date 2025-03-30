from Objects.Card import Card
from Services.InputWrapper import wrapInput

class Player:
    def __init__(self, name: str, card1: Card, card2: Card, id: int = 1):
        self.name: str = name
        self.numCoins: int = 2
        self.numCards: int = 2
        self.cards: list[Card] = [card1, card2]
        self.deadCards: list[Card] = []
        self.isAI: bool = False
        self.id: int = id

    def __str__(self):
        aliveList = ', ' + ', '.join(str(card) for card in self.cards) if self.numCards > 0 else ""
        deadList = (', DEAD: ' +', '.join(str(card) for card in self.deadCards)) if self.numCards < 2 else ""
        return f"{self.name} - {self.numCards} cards, {self.numCoins} coins{aliveList}{deadList}"

    def resetPlayer(self, card1: Card, card2: Card):
        self.numCoins = 2
        self.numCards = 2
        self.cards = [card1, card2]
        self.deadCards = []
    
    def updateNumCoins(self, change) -> None:
        self.numCoins += change

    def getNumCoins(self) -> int:
        return self.numCoins

    def getNumCards(self) -> int:
        return self.numCards
    
    def getName(self) -> str:
        return self.name
    
    def getIsAI(self) -> bool:
        return self.isAI
    
    def getCards(self) -> list[Card]:
        return self.cards    

    def getDeadCards(self) -> list[Card]:
        return self.deadCards 
    
    def resolveExchange(self, exchangeCards: list[Card], game) -> list[Card]:
        cardsInHand = self.getCards()
        cardsInHand.extend(exchangeCards)
        returnedCard1 = Card[wrapInput("First card to give back: ").upper()]
        returnedCard2 = Card[wrapInput("Second Card to give back: ").upper()]
        if(self.areReturnedCardsValid(returnedCard1, returnedCard2, cardsInHand)):
            cardsKept = cardsInHand
            cardsKept.remove(returnedCard1)
            cardsKept.remove(returnedCard2)
            self.cards = cardsKept
            return [returnedCard1, returnedCard2]
        else:
            print("Returned cards are invalid")
            self.resolveExchange(exchangeCards)

    def areReturnedCardsValid(self, returnedCard1: Card, returnedCard2: Card, cardsInHand: list[Card]) -> bool:
        if(returnedCard1 in cardsInHand and returnedCard1 in cardsInHand):
            if(returnedCard1 != returnedCard2 or cardsInHand.count(returnedCard1) > 1):
                return True
            else:
                return False
        else:
            return False
        
    def loseCard(self) -> None:
        self.numCards -= 1
        cardToDie = self.chooseCardToDie()
        self.cards.remove(cardToDie)
        self.deadCards.append(cardToDie)

    def chooseCardToDie(self) -> None:
        cardLost = Card[wrapInput("Card lost: ").upper()]
        if cardLost in self.cards:
            return cardLost
        else:
            print("Invalid choice")
            self.chooseCardToDie()
        
    def switchCard(self, cardSwitchedOut: Card, cardGained: Card):
        self.cards.remove(cardSwitchedOut)
        self.cards.append(cardGained)

    def callsActionOut(self):
        isCalledOutString = wrapInput(f"\n Does {self.getName()} call this action out? \n Type either Yes or No: ").capitalize()
        if isCalledOutString == "Yes":
            return True
        elif isCalledOutString == "No":
            return False
        else:
            print("Invalid answer")
            return self.callsActionOut()