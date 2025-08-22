import discord
from discord import app_commands
import random
import os

# ===============================
# TOKEN
# ===============================
TOKEN = os.getenv("TOKEN")  # passato come variabile d'ambiente su Railway

# ===============================
# Dati mazzo
# ===============================
semi = ["♠️", "♥️", "♦️", "♣️"]
valori = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
jolly = ["🃏Nero", "🃏Rosso"]

# stato dei mazzi degli utenti
mazzi = {}
scarti = {}
jolly_in_mano = {}

# ===============================
# Funzioni mazzo
# ===============================
def crea_mazzo():
    return [f"{v}{s}" for s in semi for v in valori]

def mescola_mazzo(mazzo):
    random.shuffle(mazzo)
    return mazzo

def pesca_carte(user_id, n=1):
    if user_id not in mazzi:
        mazzi[user_id] = mescola_mazzo(crea_mazzo())
        scarti[user_id] = []
        jolly_in_mano[user_id] = []

    pescate = []
    for _ in range(n):
        if not mazzi[user_id]:
            mazzi[user_id] = mescola_mazzo(crea_mazzo())
        carta = mazzi[user_id].pop(0)
        # Asso di picche si rimischia automaticamente
        if carta == "A♠️":
            mazzi[user_id].append(carta)
            mescola_mazzo(mazzi[user_id])
        # Jolly non tornano nel mazzo finché non usi /jolly
        elif carta in jolly:
            jolly_in_mano[user_id].append(carta)
        else:
            scarti[user_id].append(carta)
        pescate.append(carta)
    return pescate

def rimischia(user_id):
    if user_id in mazzi:
        mazzi[user_id] = mescola_mazzo([c for c in mazzi[user_id] if c not in jolly])
        return True
    return False

def rimetti_jolly(user_id):
    if user_id in mazzi:
        mazzi[user_id] += jolly_in_mano[user_id]
        mescola_mazzo(mazzi[user_id])
        jolly_in_mano[user_id] = []

def get_scarti(user_id):
    if user_id not in scarti or not scarti[user_id]:
        return None
    carte = scarti[user_id][:]
    j = [c for c in jolly if c in carte]
    resto = [c for c in carte if c not in j]
    # ordinamento per seme
    seme_dict = {s: [] for s in semi}
    for c in resto:
        for s in semi:
            if s in c:
                seme_dict[s].append(c)
                break
    risultato = []
    if j:
        risultato += j
    for s in semi:
        if seme_dict[s]:
            risultato.append(f"**{s}**: " + ", ".join(seme_dict[s]))
    return "\n".join(risultato)

# ===============================
# Client Discord
# ===============================
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # sincronizzazione comandi solo sul server di test per apparire subito
        GUILD_ID = 301079091640139778  # metti ID server
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

client = MyClient()

# ===============================
# Comandi slash
# ===============================
@client.tree.command(name="pesca", description="Pesca una carta")
async def pesca(interaction: discord.Interaction):
    carte = pesca_carte(interaction.user.id, 1)
    await interaction.response.send_message(f"Hai pescato: {', '.join(carte)}")

# pesca con numero
@client.tree.command(name="pesca2", description="Pesca due carte")
async def pesca2(interaction: discord.Interaction):
    carte = pesca_carte(interaction.user.id, 2)
    await interaction.response.send_message(f"Hai pescato: {', '.join(carte)}")

@client.tree.command(name="pesca5", description="Pesca cinque carte")
async def pesca5(interaction: discord.Interaction):
    carte = pesca_carte(interaction.user.id, 5)
    await interaction.response.send_message(f"Hai pescato: {', '.join(carte)}")

@client.tree.command(name="mischia", description="Rimischia il tuo mazzo senza i jolly")
async def mischia(interaction: discord.Interaction):
    rimischia(interaction.user.id)
    await interaction.response.send_message("Il tuo mazzo è stato rimischiato (i jolly non sono stati rimessi).")

@client.tree.command(name="jolly", description="Rimetti i jolly nel mazzo e mescola")
async def jolly_cmd(interaction: discord.Interaction):
    rimetti_jolly(interaction.user.id)
    await interaction.response.send_message("I jolly sono stati rimessi nel mazzo e il mazzo è stato rimischiato.")

@client.tree.command(name="scarti", description="Mostra le carte già pescate")
async def scarti_cmd(interaction: discord.Interaction):
    risultato = get_scarti(interaction.user.id)
    if not risultato:
        await interaction.response.send_message("Non hai ancora scarti.")
    else:
        await interaction.response.send_message(f"Le tue carte scartate:\n{risultato}")

# ===============================
# Avvio bot
# ===============================
client.run(TOKEN)
