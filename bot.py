import discord
from discord import app_commands
import random
import os

# ===============================
# TOKEN e SERVER
# ===============================
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

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
    return [f"{v}{s}" for s in semi for v in valori] + jolly[:]

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
        if carta == "A♠️":
            mazzi[user_id] += mescola_mazzo([c for c in scarti[user_id] if c not in jolly] + ["A♠️"])
            scarti[user_id] = [c for c in scarti[user_id] if c in jolly]
            scarti[user_id].append(carta)
        elif carta in jolly:
            jolly_in_mano[user_id].append(carta)
            scarti[user_id].append(carta)
        else:
            scarti[user_id].append(carta)
        pescate.append(carta)
    return pescate

def rimischia(user_id):
    if user_id in mazzi:
        mazzi[user_id] += [c for c in scarti[user_id] if c not in jolly]
        mescola_mazzo(mazzi[user_id])
        scarti[user_id] = [c for c in scarti[user_id] if c in jolly]

def rimetti_jolly(user_id):
    if user_id in mazzi:
        mazzi[user_id] += jolly_in_mano[user_id]
        mescola_mazzo(mazzi[user_id])
        jolly_in_mano[user_id] = []

def get_scarti(user_id):
    if user_id not in scarti or not scarti[user_id]:
        return "Nessuna carta scartata."
    carte = scarti[user_id][:] + jolly_in_mano.get(user_id, [])
    j = [c for c in jolly if c in carte]
    resto = [c for c in carte if c not in j]
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
        guild = discord.Object(id=GUILD_ID)

        # Cancella tutti i comandi vecchi
        existing_commands = await self.tree.fetch_commands(guild=guild)
        for cmd in existing_commands:
            await self.tree.remove_command(cmd.name, type=cmd.type, guild=guild)
        print(f"Rimossi {len(existing_commands)} comandi vecchi dal server.")

        # Sincronizza i comandi definiti nel codice
        synced = await self.tree.sync(guild=guild)
        print(f"Comandi sincronizzati sul server: {[c.name for c in synced]}")

client = MyClient()

# ===============================
# Comandi slash
# ===============================
@client.tree.command(name="pesca", description="Pesca una carta")
async def pesca(interaction: discord.Interaction):
    carta = pesca_carte(interaction.user.id)[0]
    await interaction.response.send_message(f"Hai pescato: {carta}")

@client.tree.command(name="pesca_n", description="Pesca un certo numero di carte")
async def pesca_n(interaction: discord.Interaction, numero: int):
    carte = pesca_carte(interaction.user.id, numero)
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
    await interaction.response.send_message(risultato)

# ===============================
# Avvio bot
# ===============================
client.run(TOKEN)
