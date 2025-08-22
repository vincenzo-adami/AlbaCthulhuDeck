import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from utils.deck import create_deck, shuffle_deck
from state import state

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Setup slash commands
@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")

# Funzione per inizializzare mazzo
def ensure_deck(user_id):
    if user_id not in state["decks"]:
        state["decks"][user_id] = {
            "mazzo": shuffle_deck(create_deck()),
            "scarti": [],
            "jolly": []
        }

# Comando /pesca
@bot.slash_command(name="pesca", description="Pesca 1 carta")
async def pesca(ctx: discord.ApplicationContext):
    ensure_deck(ctx.author.id)
    deck = state["decks"][ctx.author.id]
    if not deck["mazzo"]:
        await ctx.respond("Il mazzo è vuoto!")
        return
    card = deck["mazzo"].pop(0)
    deck["scarti"].append(card)
    # Se asso di picche rimischia
    if card == "A♠️":
        deck["mazzo"] = shuffle_deck(deck["mazzo"] + deck["scarti"][:-1])
        deck["scarti"] = [card]
        await ctx.respond(f"Hai pescato {card}. Mazzo rimischiato automaticamente!")
    else:
        await ctx.respond(f"Hai pescato {card}")

# Comando /pescax
@bot.slash_command(name="pescax", description="Pesca x carte")
async def pescax(ctx: discord.ApplicationContext, numero: int):
    ensure_deck(ctx.author.id)
    deck = state["decks"][ctx.author.id]
    if numero < 1:
        await ctx.respond("Devi pescare almeno una carta!")
        return
    pescate = []
    for _ in range(numero):
        if not deck["mazzo"]:
            break
        card = deck["mazzo"].pop(0)
        deck["scarti"].append(card)
        pescate.append(card)
        if card == "A♠️":
            deck["mazzo"] = shuffle_deck(deck["mazzo"] + deck["scarti"][:-1])
            deck["scarti"] = [card]
    await ctx.respond(f"Hai pescato: {', '.join(pescate)}")

# Comando /mischia
@bot.slash_command(name="mischia", description="Rimischia il mazzo (senza jolly)")
async def mischia(ctx: discord.ApplicationContext):
    ensure_deck(ctx.author.id)
    deck = state["decks"][ctx.author.id]
    deck["mazzo"] = shuffle_deck(deck["mazzo"])
    await ctx.respond("Il tuo mazzo è stato rimischiato!")

# Comando /jolly
@bot.slash_command(name="jolly", description="Rimette i jolly nel mazzo e lo rimischia")
async def jolly(ctx: discord.ApplicationContext):
    ensure_deck(ctx.author.id)
    deck = state["decks"][ctx.author.id]
    jolly_cards = ["JokerN", "JokerR"]
    for j in jolly_cards:
        if j not in deck["jolly"]:
            deck["mazzo"].append(j)
            deck["jolly"].append(j)
    deck["mazzo"] = shuffle_deck(deck["mazzo"])
    await ctx.respond("I Jolly sono stati aggiunti e il mazzo è stato rimischiato!")

# Comando /scarti
@bot.slash_command(name="scarti", description="Mostra le carte pescate")
async def scarti(ctx: discord.ApplicationContext):
    ensure_deck(ctx.author.id)
    deck = state["decks"][ctx.author.id]
    if not deck["scarti"]:
        await ctx.respond("Non hai ancora scarti!")
        return
    # Ordinamento seme
    semi = ["♠️","♥️","♦️","♣️"]
    ordinati = []
    # Aggiungi Jolly in cima se ci sono
    jolly_presenti = [c for c in deck["scarti"] if "Joker" in c]
    ordinati.extend(jolly_presenti)
    for s in semi:
        ordinati.extend([c for c in deck["scarti"] if s in c])
    await ctx.respond(f"Scarti: {', '.join(ordinati)}")

bot.run(TOKEN)
