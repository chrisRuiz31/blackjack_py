import pygame
import random
HEARTS = 'hearts'
DIAMONDS = 'diamonds'
SPADES = 'spades'
CLUBS = 'clubs'
RANKS = {'J':11, 'Q':12, 'K':13, 'A':14}

class Player:
    """This holds the player's properties such as hand"""
    def __init__(self, hand):
        if hand == None:
            self.hand = []
        else:
            self.hand = hand
        self.hand_amount = len(self.hand)
        self.winning_hand = []

    def pop_from_player(self, amount):
        from_hand = []
        if len(self.hand) > 0:
            for i in range(amount):
                card = self.hand.pop()
                self.hand_amount -= 1
                from_hand.append(card)
            return from_hand
        else:
            print("Sorry but the deck is empty")
    
    def add(self, cards):
        for card in cards:
            self.hand.append(card)
            self.hand_amount += 1

    def insert(self, cards):
        for card in cards:
            self.hand.insert(0, card)
            self.hand_amount += 1
    

class Card:
    """This class creates a card object and can be used to display the rank and suit. """
    
    def __init__(self, rank, suit, back=True):
        self.rank = rank
        self.suit = suit
        self.img_file = f"{self.suit}_{self.rank}.png"
        self.show_back = back
        self.back_file = ["back_dark.png", "back_light.png"]
        self.card_str = f"{self.suit} {self.rank}"

        if self.rank in RANKS:
            self.rank = RANKS[self.rank]
    
    def __str__(self):
        return self.card_str
    
    def access_rank(self):
        return self.rank
    
    def access_suit(self):
        return self.suit
    
    def return_path(self):
        path = f"cards/{self.img_file}"
        return path


class Game_Deck:
    """This is the Deck class, where it will generate
    and store the cards based on rank and suit."""
    def __init__(self):
        self.game_deck = []

    def generateDeck(self):
        for suit in (CLUBS, DIAMONDS, HEARTS, SPADES):
            for rank in range(2, 11):
                self.game_deck.append(Card(rank, suit))
            for rank in ('A', 'J', 'K', 'Q'):
                self.game_deck.append(Card(rank, suit))
        
        """
        For debugging purposes

        for i, card in enumerate(self.deck):
            example = self.deck[i]
            example.load_file()
        """
    def shuffle(self):
        random.shuffle(self.game_deck)
        
    
    def pop_from_deck(self, amount):
        from_deck = []
        if len(self.game_deck) > 0:
            for i in range(amount):
                card = self.game_deck.pop()
                from_deck.append(card)
            return from_deck
        else:
            print("Sorry but the deck is empty")



def testing():
    x = Game_Deck()
    x.generateDeck()

if __name__ == '__testing__':
    testing()