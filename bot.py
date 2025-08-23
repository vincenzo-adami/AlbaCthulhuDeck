import discord
from discord.ext import commands
import random
import os

TOKEN = os.environ.get("TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True  # serve per leggere i contenuti dei messaggi
bot = commands.Bot(command_prefix="/", intents=intents)

# Emoji dei semi
SUITS = {
    "cuori": "♥️",
    "quadri": "♦️",
    "fiori": "♣️",
    "picche": "♠️"
}

# Valori carte
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Due jolly
JOKERS = ["🃏🔴", "🃏⚫"]

# Dizionario giocatori
players = {}

def initialize_deck():
    deck = []
    for suit in SUITS.values():
        for value in VALUES:
            deck.append(f"{value}{suit}")
    deck.extend(JOKERS)
    random.shuffle(deck)
    return deck

def draw_cards(player_id, n):
    if player_id not in players:
        players[player_id] = {"deck": initialize_deck(), "hand": [], "discards": []}

    player = players[player_id]
    drawn = []
    for _ in range(n):
        if not player["deck"]:
            reshuffle_discard(player_id)
        if not player["deck"]:
            break
        card = player["deck"].pop(0)
        player["hand"].append(card)
        drawn.append(card)
        if card in JOKERS:
            player["discards"].insert(0, card)
        else:
            player["discards"].append(card)
    return drawn

def reshuffle_discard(player_id):
    player = players[player_id]
    # Tutti tranne jolly
    cards_to_reshuffle = [c for c in player["discards"] if c not in JOKERS]
    player["deck"].extend(cards_to_reshuffle)
    # Rimuovo dal discard
    player["discards"] = [c for c in player["discards"] if c in JOKERS]
    random.shuffle(player["deck"])

@bot.tree.command(name="pesca_n", description="Pesca N carte")
async def pesca_n(interaction: discord.Interaction, n: int):
    cards = draw_cards(interaction.user.id, n)
    await interaction.response.send_message(f"Hai pescato: {' '.join(cards)}")

@bot.tree.command(name="scarti", description="Mostra gli scarti")
async def scarti(interaction: discord.Interaction):
    if interaction.user.id not in players:
        await interaction.response.send_message("Non hai ancora giocato.")
        return
    discards = players[interaction.user.id]["discards"]
    # Ordinamento jolly in testa e per semi
    jokers = [c for c in discards if c in JOKERS]
    non_jokers = sorted([c for c in discards if c not in JOKERS],
                         key=lambda x: (x[-1], VALUES.index(x[:-1])))
    ordered_discards = jokers + non_jokers
    await interaction.response.send_message(f"I tuoi scarti: {' '.join(ordered_discards)}")

@bot.tree.command(name="mischia", description="Rimescola gli scarti nel mazzo")
async def mischia(interaction: discord.Interaction):
    reshuffle_discard(interaction.user.id)
    await interaction.response.send_message("Scarti rimescolati nel mazzo (jolly esclusi).")

@bot.tree.command(name="jolly", description="Rimescola un jolly nel mazzo")
async def jolly(interaction: discord.Interaction):
    if interaction.user.id not in players:
        players[interaction.user.id] = {"deck": initialize_deck(), "hand": [], "discards": []}
    player = players[interaction.user.id]
    for joker in JOKERS:
        if joker in player["discards"]:
            player["discards"].remove(joker)
            player["deck"].append(joker)
            random.shuffle(player["deck"])
            await interaction.response.send_message(f"{joker} rimesso nel mazzo.")
            return
    await interaction.response.send_message("Non ci sono jolly da rimescolare.")

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("Bot pronto e comandi sincronizzati sul server.")

bot.run(TOKEN)
