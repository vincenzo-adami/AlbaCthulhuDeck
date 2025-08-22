import random
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("TOKEN")  # Puoi continuare a passarlo da Railway come variabile d'ambiente

intents = discord.Intents.default()
intents.message_content = True  # necessario se vuoi leggere i messaggi
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Mazzi e scarti per utente ---
decks = {}   # user_id -> mazzo
discards = {}  # user_id -> carte scartate

# --- Semi con emoji ---
suits = {
    "cuori": "♥️",
    "quadri": "♦️",
    "fiori": "♣️",
    "picche": "♠️"
}

# --- Creazione mazzo ---
def create_deck():
    deck = []
    for suit, emoji in suits.items():
        for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]:
            deck.append(f"{rank}{emoji}")
    # aggiungi jolly
    deck.append("Jolly🟥")
    deck.append("Jolly⬛")
    random.shuffle(deck)
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)

# --- Utility ---
def get_user_deck(user_id):
    if user_id not in decks:
        decks[user_id] = create_deck()
    if user_id not in discards:
        discards[user_id] = []
    return decks[user_id]

# --- Comandi slash ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} è pronto!")

# /pesca
@bot.tree.command(name="pesca", description="Pesca una carta")
async def pesca(interaction: discord.Interaction):
    user_id = interaction.user.id
    deck = get_user_deck(user_id)
    if not deck:
        deck = create_deck()
        decks[user_id] = deck

    card = deck.pop(0)
    # asso di picche rimischia
    if card == f"A{suits['picche']}":
        shuffle_deck(deck)
    # jolly non si rimischiano
    if card.startswith("Jolly"):
        discards[user_id].insert(0, card)
    else:
        discards[user_id].append(card)

    await interaction.response.send_message(f"Hai pescato: {card}")

# /pescax (numero variabile)
@bot.tree.command(name="pescax", description="Pesca più carte")
@app_commands.describe(numero="Numero di carte da pescare")
async def pescax(interaction: discord.Interaction, numero: int):
    user_id = interaction.user.id
    deck = get_user_deck(user_id)
    if not deck:
        deck = create_deck()
        decks[user_id] = deck

    if numero < 1:
        await interaction.response.send_message("Inserisci un numero maggiore di 0!")
        return

    drawn = []
    for _ in range(numero):
        if not deck:
            deck = create_deck()
            decks[user_id] = deck
        card = deck.pop(0)
        if card == f"A{suits['picche']}":
            shuffle_deck(deck)
        if card.startswith("Jolly"):
            discards[user_id].insert(0, card)
        else:
            discards[user_id].append(card)
        drawn.append(card)
    await interaction.response.send_message(f"Hai pescato: {', '.join(drawn)}")

# /mischia
@bot.tree.command(name="mischia", description="Rimischia il mazzo (esclusi i jolly)")
async def mischia(interaction: discord.Interaction):
    user_id = interaction.user.id
    deck = get_user_deck(user_id)
    non_jolly = [c for c in deck if not c.startswith("Jolly")]
    shuffle_deck(non_jolly)
    jolly_cards = [c for c in deck if c.startswith("Jolly")]
    decks[user_id] = non_jolly + jolly_cards
    await interaction.response.send_message("Il tuo mazzo è stato rimischiato!")

# /jolly
@bot.tree.command(name="jolly", description="Rimetti i jolly nel mazzo e rimischia")
async def jolly(interaction: discord.Interaction):
    user_id = interaction.user.id
    deck = get_user_deck(user_id)
    jolly_cards = [c for c in ["Jolly🟥", "Jolly⬛"] if c not in deck]
    deck.extend(jolly_cards)
    shuffle_deck(deck)
    decks[user_id] = deck
    await interaction.response.send_message("I jolly sono stati reinseriti e il mazzo è stato rimischiato!")

# /scarti
@bot.tree.command(name="scarti", description="Mostra le carte scartate")
async def scarti(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_discards = discards.get(user_id, [])
    if not user_discards:
        await interaction.response.send_message("Non ci sono carte scartate.")
        return
    # ordina per seme e jolly all'inizio
    jolly_cards = [c for c in user_discards if c.startswith("Jolly")]
    non_jolly = [c for c in user_discards if not c.startswith("Jolly")]
    sorted_discards = []
    for suit, emoji in suits.items():
        sorted_discards.extend(sorted([c for c in non_jolly if emoji in c]))
    final_list = jolly_cards + sorted_discards
    await interaction.response.send_message(f"Carte scartate: {', '.join(final_list)}")

bot.run(TOKEN)
