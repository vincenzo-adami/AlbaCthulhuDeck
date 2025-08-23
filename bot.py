import discord
from discord.ext import commands
import random
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True  # serve per leggere i contenuti dei messaggi

# === Creazione del bot ===
client = commands.Bot(command_prefix="/", intents=intents)

# =========================
# MAZZO DI CARTE
# =========================
semi = ["♠️", "♥️", "♦️", "♣️"]
valori = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
mazzo_base = [f"{val}{seme}" for seme in semi for val in valori]
mazzo_base.append("🃏 Rosso")
mazzo_base.append("🃏 Nero")

# =========================
# GESTIONE STATI
# =========================
mazzi_giocatori = {}
scarti_giocatori = {}

def crea_mazzo():
    mazzo = mazzo_base.copy()
    random.shuffle(mazzo)
    return mazzo

def inizializza_giocatore(user_id):
    mazzi_giocatori[user_id] = crea_mazzo()
    scarti_giocatori[user_id] = []

# =========================
# BOT READY + SYNC
# =========================
@client.event
async def on_ready():
    print(f"{client.user} connesso.")
    try:
        synced = await client.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Comandi sincronizzati: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Errore sync: {e}")

# =========================
# COMANDI
# =========================
@client.tree.command(name="pesca", description="Pesca una carta", guild=discord.Object(id=GUILD_ID))
async def pesca(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in mazzi_giocatori:
        inizializza_giocatore(user_id)

    mazzo = mazzi_giocatori[user_id]
    scarti = scarti_giocatori[user_id]

    if not mazzo:  # se vuoto, rimescola
        mazzo.extend([c for c in scarti if "🃏" not in c])
        scarti[:] = [c for c in scarti if "🃏" in c]
        random.shuffle(mazzo)

    carta = mazzo.pop()
    scarti.append(carta)

    # logica asso di picche
    if carta == "A♠️":
        mazzo.extend([c for c in scarti if "🃏" not in c])
        scarti[:] = [c for c in scarti if "🃏" in c]
        random.shuffle(mazzo)
        await interaction.response.send_message(
            f"Hai pescato {carta}! Tutti gli scarti (tranne i jolly) sono stati rimischiati nel mazzo."
        )
    else:
        await interaction.response.send_message(f"Hai pescato: {carta}")

@client.tree.command(name="pesca_n", description="Pesca N carte", guild=discord.Object(id=GUILD_ID))
async def pesca_n(interaction: discord.Interaction, numero: int):
    user_id = interaction.user.id
    if user_id not in mazzi_giocatori:
        inizializza_giocatore(user_id)

    mazzo = mazzi_giocatori[user_id]
    scarti = scarti_giocatori[user_id]

    pescate = []
    for _ in range(numero):
        if not mazzo:
            mazzo.extend([c for c in scarti if "🃏" not in c])
            scarti[:] = [c for c in scarti if "🃏" in c]
            random.shuffle(mazzo)

        if not mazzo:  # protezione extra
            break

        carta = mazzo.pop()
        scarti.append(carta)
        pescate.append(carta)

        if carta == "A♠️":
            mazzo.extend([c for c in scarti if "🃏" not in c])
            scarti[:] = [c for c in scarti if "🃏" in c]
            random.shuffle(mazzo)

    if pescate:
        await interaction.response.send_message(
            f"Hai pescato: {', '.join(pescate)}"
        )
    else:
        await interaction.response.send_message("Non ci sono abbastanza carte da pescare.")

@client.tree.command(name="scarti", description="Mostra gli scarti", guild=discord.Object(id=GUILD_ID))
async def scarti(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in scarti_giocatori:
        inizializza_giocatore(user_id)

    scarti = scarti_giocatori[user_id]
    if scarti:
        await interaction.response.send_message(f"Scarti: {', '.join(scarti)}")
    else:
        await interaction.response.send_message("Nessuno scarto.")

@client.tree.command(name="mischia", description="Rimischia gli scarti nel mazzo (tranne i jolly)", guild=discord.Object(id=GUILD_ID))
async def mischia(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in mazzi_giocatori:
        inizializza_giocatore(user_id)

    mazzo = mazzi_giocatori[user_id]
    scarti = scarti_giocatori[user_id]

    if not scarti:
        await interaction.response.send_message("Non ci sono scarti da rimischiare.")
        return

    mazzo.extend([c for c in scarti if "🃏" not in c])
    scarti[:] = [c for c in scarti if "🃏" in c]
    random.shuffle(mazzo)

    await interaction.response.send_message("Gli scarti (tranne i jolly) sono stati rimischiati nel mazzo.")

@client.tree.command(name="reset", description="Resetta il tuo mazzo e gli scarti", guild=discord.Object(id=GUILD_ID))
async def reset(interaction: discord.Interaction):
    inizializza_giocatore(interaction.user.id)
    await interaction.response.send_message("Il tuo mazzo è stato resettato.")

# =========================
# AVVIO BOT
# =========================
if __name__ == "__main__":
    client.run(TOKEN)
