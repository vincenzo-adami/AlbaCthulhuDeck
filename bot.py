import discord
from discord import app_commands
import random
import os

# ===============================
# TOKEN
# ===============================
TOKEN = os.getenv("TOKEN")  # passato come variabile d'ambiente
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # anche l’ID del server da env

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
        # Asso di picche rimescola tutti gli scarti eccetto i jolly
        if carta == "A♠️":
            mazzi_user = [c for c in scarti[user_id] if c not in jolly]
            mazzi[user_id] += mescola_mazzo(mazzi_user)
            scarti[user_id] = [c for c in scarti[user_id] if c in jolly]
            scarti[user_id].append(carta)
        # Jolly vanno in mano e negli scarti
        elif carta in jolly:
            jolly_in_mano[user_id].append(carta)
            scarti[user_id].append(carta)
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

def get_scarti_text(user_id):
    if user_id not in scarti or not scarti[user_id]:
        return None
    carte = scarti[user_id][:]  # carte già scartate
    # aggiungi jolly pescati ma non ancora rimessi nel mazzo
    carte += jolly_in_mano.get(user_id, [])
    
    j = [c for c in jolly if c in carte]  # separa jolly
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
        guild = discord.Object(id=GUILD_ID)

        # 🔥 1. Cancello i comandi locali per quella guild
        self.tree.clear_commands(guild=guild)

        # 🔥 2. Cancello anche eventuali comandi globali (per sicurezza)
        self.tree.clear_commands(guild=None)

        # (opzionale) se vuoi ripulire anche i globali dal server:
        await self.tree.sync(guild=None)
        print("🧹 Comandi globali rimossi.")

         # 🔥 3. Sync guild: carica SOLO quelli che hai definito nel codice
        synced = await self.tree.sync(guild=guild)


        print(f"✅ Comandi sincronizzati sulla guild {GUILD_ID}: {[cmd.name for cmd in synced]}")

client = MyClient()

# ===============================
# Variabile globale deck per pesca_n
# ===============================
deck = []

# ===============================
# Comandi slash
# ===============================

@client.tree.command(name="pesca", description="Pesca una carta")
async def pesca(interaction: discord.Interaction):
    user_id = interaction.user.id
    carte = pesca_carte(user_id, 1)
    await interaction.response.send_message(f"Hai pescato: {', '.join(carte)}")

@client.tree.command(name="pesca_n", description="Pesca un certo numero di carte")
async def pesca_n(interaction: discord.Interaction, numero: int):
    global deck
    user_id = interaction.user.id

    # inizializza deck se vuoto
    if not deck:
        deck = crea_mazzo()  # contiene anche i jolly
        mescola_mazzo(deck)

    pescate = []
    remaining = numero

    while remaining > 0 and deck:
        carta = deck.pop(0)

        if carta == "A♠️":
            # rimescola tutti gli scarti tranne i jolly e l'asso stesso
            mazzi_user = [c for c in pescate + deck if c not in jolly] + [carta]
            mescola_mazzo(mazzi_user)
            deck = mazzi_user
            continue  # continua a pescare le carte rimanenti

        if user_id not in scarti:
            scarti[user_id] = []

        if carta in jolly:
            if user_id not in jolly_in_mano:
                jolly_in_mano[user_id] = []
            jolly_in_mano[user_id].append(carta)
            # aggiungi subito il jolly anche agli scarti
            scarti[user_id].append(carta)
        else:
            scarti[user_id].append(carta)

        pescate.append(carta)
        remaining -= 1

    await interaction.response.send_message(f"Hai pescato: {', '.join(pescate)}")


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
    user_id = interaction.user.id
    risultato = get_scarti_text(user_id)
    if not risultato:
        await interaction.response.send_message("Non hai ancora scarti.")
    else:
        await interaction.response.send_message(f"Le tue carte scartate:\n{risultato}")

# ===============================
# Avvio bot
# ===============================
client.run(TOKEN)
