import random

# Semi con emoji
suits = ["♠️", "♥️", "♦️", "♣️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def create_deck(include_jokers=True):
    """Crea un nuovo mazzo di carte. Include i jolly se richiesto."""
    deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
    if include_jokers:
        deck.append("Jolly Nero 🃏⚫")
        deck.append("Jolly Rosso 🃏🔴")
    return deck

def shuffle_deck(deck):
    """Mescola il mazzo"""
    random.shuffle(deck)

def draw_cards(deck, num=1):
    """Pesca num carte dal mazzo"""
    drawn = []
    for _ in range(num):
        if deck:
            card = deck.pop(0)
            drawn.append(card)
            # Se è asso di picche, rimischia automaticamente
            if card == "A♠️":
                deck.append(card)
                shuffle_deck(deck)
        else:
            break
    return drawn
