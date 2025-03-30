from Objects.Card import Card
from Services.InputWrapper import wrapInput

"""
Player is a Coup player class that is a parent class for other player classes within the
Players directory.

Other than being the parent class for other player classes, it is used primarily for 
human players (eventually, I will create a human player class that also extends this class).
"""
class Player:
    def __init__(self, name: str, card1: Card, card2: Card, id: int = 1):
        self.name: str = name
        self.num_coins: int = 2
        self.num_cards: int = 2
        self.cards: list[Card] = [card1, card2]
        self.dead_cards: list[Card] = []
        self.is_AI: bool = False
        self.id: int = id

    def __str__(self):
        alive_list = ', ' + ', '.join(str(card) for card in self.cards) if self.num_cards > 0 else ""
        dead_list = (', DEAD: ' +', '.join(str(card) for card in self.dead_cards)) if self.num_cards < 2 else ""
        return f"{self.name} - {self.num_cards} cards, {self.num_coins} coins{alive_list}{dead_list}"

    def resetPlayer(self, card1: Card, card2: Card):
        self.num_coins = 2
        self.num_cards = 2
        self.cards = [card1, card2]
        self.dead_cards = []
    
    def updateNumCoins(self, change) -> None:
        self.num_coins += change

    def getNumCoins(self) -> int:
        return self.num_coins

    def getNumCards(self) -> int:
        return self.num_cards
    
    def getName(self) -> str:
        return self.name
    
    def getIsAI(self) -> bool:
        return self.is_AI
    
    def getCards(self) -> list[Card]:
        return self.cards    

    def getDeadCards(self) -> list[Card]:
        return self.dead_cards 
    
    def resolveExchange(self, exchange_cards: list[Card], game) -> list[Card]:
        cards_in_hand = self.getCards()
        cards_in_hand.extend(exchange_cards)
        returned_card_1 = Card[wrapInput("First card to give back: ").upper()]
        returned_card_2 = Card[wrapInput("Second Card to give back: ").upper()]
        if(self.areReturnedCardsValid(returned_card_1, returned_card_2, cards_in_hand)):
            cards_kept = cards_in_hand
            cards_kept.remove(returned_card_1)
            cards_kept.remove(returned_card_2)
            self.cards = cards_kept
            return [returned_card_1, returned_card_2]
        else:
            print("Returned cards are invalid")
            self.resolveExchange(exchange_cards)

    def areReturnedCardsValid(self, returned_card_1: Card, returned_card_2: Card, cards_in_hand: list[Card]) -> bool:
        if(returned_card_1 in cards_in_hand and returned_card_1 in cards_in_hand):
            if(returned_card_1 != returned_card_2 or cards_in_hand.count(returned_card_1) > 1):
                return True
            else:
                return False
        else:
            return False
        
    def loseCard(self) -> None:
        self.num_cards -= 1
        card_to_die = self.chooseCardToDie()
        self.cards.remove(card_to_die)
        self.dead_cards.append(card_to_die)

    def chooseCardToDie(self) -> None:
        card_lost = Card[wrapInput("Card lost: ").upper()]
        if card_lost in self.cards:
            return card_lost
        else:
            print("Invalid choice")
            self.chooseCardToDie()
        
    def switchCard(self, card_switched_out: Card, card_gained: Card):
        self.cards.remove(card_switched_out)
        self.cards.append(card_gained)

    def callsActionOut(self):
        is_called_out_string = wrapInput(f"\n Does {self.getName()} call this action out? \n Type either Yes or No: ").capitalize()
        if is_called_out_string == "Yes":
            return True
        elif is_called_out_string == "No":
            return False
        else:
            print("Invalid answer")
            return self.callsActionOut()