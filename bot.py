import os
import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True

class BriscolaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.players = {}  # player_id -> {"mazzo": [], "mano": [], "scarti": []}

    async def setup_hook(self):
        # sincronizzazione comandi bulletproof
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        try:
            synced = await self.tree.sync(guild=guild)
            print(f"=== Comandi sincronizzati sul server ({len(synced)}) ===")
            for cmd in synced:
                print(f"- {cmd.name}")
            print("=======================================")
        except Exception as e:
            print(f"Errore sync comandi: {e}")

client = BriscolaBot()

# === COSTANTI MAZZO ===
SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
JOKERS = ["JOKER ROSSO", "JOKER NERO"]

def crea_mazzo():
    mazzo = [rank + suit for suit in SUITS for rank in RANKS]
    mazzo.extend(JOKERS)
    random.shuffle(mazzo)
    return mazzo

def get_player_data(user_id):
    if user_id not in client.players:
        client.players[user_id] = {
            "mazzo": crea_mazzo(),
            "mano": [],
            "scarti": []
        }
    return client.players[user_id]

# === COMANDI ===

@client.tree.command(name="pesca", description="Pesca una carta dal mazzo")
async def pesca(interaction: discord.Interaction):
    player = get_player_data(interaction.user.id)

    if not player["mazzo"]:
        await interaction.response.send_message("Il mazzo è vuoto!", ephemeral=True)
        return

    carta = player["mazzo"].pop(0)

    # gestione jolly
    if carta in JOKERS:
        player["scarti"].append(carta)
        await interaction.response.send_message(f"Hai pescato un **{carta}** (finisce subito negli scarti)")
        return

    # gestione normale
    player["mano"].append(carta)
    await interaction.response.send_message(f"Hai pescato: **{carta}**")

    # controllo Asso di Picche
    if carta == "A♠️":
        # rimescola scarti (esclusi i jolly) nel mazzo
        da_rimescolare = [c for c in player["scarti"] if c not in JOKERS]
        player["mazzo"].extend(da_rimescolare)
        random.shuffle(player["mazzo"])
        player["scarti"] = [c for c in player["scarti"] if c in JOKERS]
        await interaction.followup.send("Hai pescato l'**Asso di Picche**! Gli scarti (senza Jolly) tornano nel mazzo.")

@client.tree.command(name="scarti", description="Mostra le carte negli scarti")
async def scarti(interaction: discord.Interaction):
    player = get_player_data(interaction.user.id)
    if not player["scarti"]:
        await interaction.response.send_message("Non ci sono scarti.")
        return
    scarti_txt = ", ".join(player["scarti"])
    await interaction.response.send_message(f"Scarti attuali: {scarti_txt}")

@client.tree.command(name="mischia", description="Rimescola gli scarti nel mazzo")
async def mischia(interaction: discord.Interaction):
    player = get_player_data(interaction.user.id)
    if not player["scarti"]:
        await interaction.response.send_message("Non ci sono scarti da rimescolare.")
        return

    da_rimescolare = [c for c in player["scarti"] if c not in JOKERS]
    if not da_rimescolare:
        await interaction.response.send_message("Negli scarti ci sono solo Jolly, non rimescolati.")
        return

    player["mazzo"].extend(da_rimescolare)
    random.shuffle(player["mazzo"])
    player["scarti"] = [c for c in player["scarti"] if c in JOKERS]

    await interaction.response.send_message("Gli scarti (senza Jolly) sono stati rimescolati nel mazzo!")

@client.tree.command(name="mano", description="Mostra le tue carte in mano")
async def mano(interaction: discord.Interaction):
    player = get_player_data(interaction.user.id)
    if not player["mano"]:
        await interaction.response.send_message("Non hai carte in mano.")
        return
    mano_txt = ", ".join(player["mano"])
    await interaction.response.send_message(f"Carte in mano: {mano_txt}")

@client.tree.command(name="reset", description="Resetta il tuo mazzo")
async def reset(interaction: discord.Interaction):
    client.players[interaction.user.id] = {
        "mazzo": crea_mazzo(),
        "mano": [],
        "scarti": []
    }
    await interaction.response.send_message("Il tuo mazzo è stato resettato!")

if __name__ == "__main__":
    client.run(TOKEN)
