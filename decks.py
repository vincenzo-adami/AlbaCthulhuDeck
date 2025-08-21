import random

def create_deck():
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
    deck += ["JOKER1", "JOKER2"]
    random.shuffle(deck)
    return deck

def draw_card(player):
    deck = player["deck"]
    pile = player["pile"]
    if not deck:
        return None
    card = deck.pop(0)
    pile.append(card)
    # rimescola se esce asso di picche
    if card == "A♠":
        deck.extend(pile)
        random.shuffle(deck)
        player["pile"].clear()
    return card
