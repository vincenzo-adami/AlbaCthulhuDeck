import os
import random
import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
client = commands.Bot(command_prefix="/", intents=intents)

# =========================
# LOGICA DEL MAZZO
# =========================

# Mazzi globali per ogni giocatore: {user_id: {"mazzo": [], "scarti": [], "jolly": []}}
players = {}

# Tutte le carte possibili
CARDS = [f"{rank}{suit}" for suit in "♠♥♦♣" for rank in list(map(str, range(2, 11))) + ["J", "Q", "K", "A"]]
JOKER = "JOKER"

def init_player(user_id):
    if user_id not in players:
        # Copia del mazzo principale per ogni giocatore
        players[user_id] = {
            "mazzo": CARDS.copy(),
            "scarti": [],
            "jolly": [JOKER],
        }

def draw_cards(user_id, n):
    init_player(user_id)
    player = players[user_id]
    deck = player["mazzo"]
    hand = []

    for _ in range(n):
        if not deck:
            # Se il mazzo è vuoto, rimescola gli scarti tranne i Jolly
            deck += [c for c in player["scarti"] if c != JOKER]
            player["scarti"] = [c for c in player["scarti"] if c == JOKER]
            random.shuffle(deck)
        if not deck:
            break
        card = deck.pop(0)
        hand.append(card)
        # Se è JOKER, va negli scarti Jolly
        if card == JOKER:
            player["scarti"].append(card)
        else:
            player["scarti"].append(card)
    return hand

def shuffle_discards(user_id):
    init_player(user_id)
    player = players[user_id]
    # Rimescola gli scarti nel mazzo tranne i Jolly
    to_shuffle = [c for c in player["scarti"] if c != JOKER]
    player["mazzo"] += to_shuffle
    player["scarti"] = [c for c in player["scarti"] if c == JOKER]
    random.shuffle(player["mazzo"])

# =========================
# SINCRONIZZAZIONE COMANDI
# =========================

@client.event
async def setup_hook():
    guild = discord.Object(id=GUILD_ID)

    # Sincronizza i comandi sul server
    client.tree.copy_global_to(guild=guild)
    synced = await client.tree.sync(guild=guild)
    print("=== Comandi sincronizzati sul server ===")
    for cmd in synced:
        print(f"- {cmd.name}")
    print("=======================================")

# =========================
# COMANDI
# =========================

@client.tree.command(name="pesca_n", description="Pesca N carte dal tuo mazzo")
async def pesca_n(interaction: discord.Interaction, n: int):
    hand = draw_cards(interaction.user.id, n)
    await interaction.response.send_message(f"Hai pescato: {', '.join(hand) if hand else 'Nessuna carta rimasta nel mazzo.'}")

@client.tree.command(name="scarti", description="Mostra i tuoi scarti")
async def scarti(interaction: discord.Interaction):
    init_player(interaction.user.id)
    player = players[interaction.user.id]
    await interaction.response.send_message(f"Scarti: {', '.join(player['scarti']) if player['scarti'] else 'Nessuno scarto'}")

@client.tree.command(name="mischia", description="Rimescola gli scarti nel mazzo")
async def mischia(interaction: discord.Interaction):
    shuffle_discards(interaction.user.id)
    await interaction.response.send_message("Il mazzo è stato rimescolato con gli scarti (Jolly esclusi).")

# =========================
# AVVIO BOT
# =========================

client.run(TOKEN)
