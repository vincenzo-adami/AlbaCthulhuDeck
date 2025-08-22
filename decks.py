import random

def create_deck():
    semi = ["♠️","♥️","♦️","♣️"]
    valori = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    deck = [f"{v}{s}" for s in semi for v in valori]
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck
