import discord
from discord.ext import commands
from decks import create_deck, draw_card
from state import state
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def setgm(ctx, member: discord.Member):
    state["gm"] = member.id
    await ctx.send(f"{member.display_name} è ora il GM!")

@bot.command()
async def pesca(ctx, member: discord.Member):
    if ctx.author.id != state.get("gm"):
        await ctx.send("Solo il GM può far pescare!")
        return

    # crea mazzo se non esiste
    if member.id not in state["players"]:
        state["players"][member.id] = {"deck": create_deck(), "pile": []}

    card = draw_card(state["players"][member.id])
    await ctx.send(f"{member.display_name} ha pescato: {card}")

@bot.command()
async def pila(ctx, member: discord.Member):
    if member.id not in state["players"]:
        await ctx.send("Questo giocatore non ha ancora un mazzo.")
        return
    pile = state["players"][member.id]["pile"]
    await ctx.send(f"Pila di {member.display_name}: {pile}")

bot.run(TOKEN)
