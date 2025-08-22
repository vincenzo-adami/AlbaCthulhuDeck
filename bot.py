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
    # inizializza mazzo se necessario
    if user_id not in mazzi:
        mazzi[user_id] = mescola_mazzo(crea_mazzo())
        scarti[user_id] = []
        jolly_in_mano[user_id] = []

    pescate = []
    remaining = n

    while remaining > 0 and mazzi[user_id]:
        carta = mazzi[user_id].pop(0)

        if carta == "A♠️":
            # rimescola tutti gli scarti eccetto i jolly + Asso di picche
            mazzi[user_id] += mescola_mazzo([c for c in scarti[user_id] if c not in jolly] + ["A♠️"])
            scarti[user_id] = [c for c in scarti[user_id] if c in jolly]
            # non decrementare remaining perché l'Asso non conta ancora come pescato
            continue

        elif carta in jolly:
            jolly_in_mano[user_id].append(carta)
            scarti[user_id].append(carta)
        else:
            scarti[user_id].append(carta)

        pescate.append(carta)
        remaining -= 1

    return pescate


def rimischia(user_id):
    if user_id in mazzi:
        # reintegra scarti tranne jolly e mischia
        mazzi[user_id] += [c for c in scarti[user_id] if c not in jolly]
        scarti[user_id] = [c for c in scarti[user_id] if c in jolly]
        mescola_mazzo(mazzi[user_id])
        return True
    return False


def rimetti_jolly(user_id):
    if user_id in mazzi:
        mazzi[user_id] += jolly_in_mano[user_id]
        mescola_mazzo(mazzi[user_id])
        jolly_in_mano[user_id] = []


def get_scarti(user_id):
    if user_id not in scarti:
        return None
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

        guild_commands = list(self.tree._guild_commands.get(GUILD_ID, {}).values())
        for cmd in guild_commands:
            self.tree.remove_command(cmd.name, guild=guild)

        # Copia solo i comandi globali sul server
        self.tree.copy_global_to(guild=guild)

        # Sincronizza il server (registra solo i comandi copiati)
        await self.tree.sync(guild=guild)

client = MyClient()

# ===============================
# Variabile globale deck per pesca_n
# ===============================
deck = []

# ===============================
# Comandi slash
# ===============================

def pesca_carte(user_id, n=1):
    # inizializza mazzo se necessario
    if user_id not in mazzi:
        mazzi[user_id] = mescola_mazzo(crea_mazzo())
        scarti[user_id] = []
        jolly_in_mano[user_id] = []

    pescate = []
    remaining = n

    while remaining > 0 and mazzi[user_id]:
        carta = mazzi[user_id].pop(0)

        if carta == "A♠️":
            # rimescola tutti gli scarti eccetto i jolly + Asso di picche
            mazzi[user_id] += mescola_mazzo([c for c in scarti[user_id] if c not in jolly] + ["A♠️"])
            scarti[user_id] = [c for c in scarti[user_id] if c in jolly]
            # non decrementare remaining perché l'Asso non conta ancora come pescato
            continue

        elif carta in jolly:
            jolly_in_mano[user_id].append(carta)
            scarti[user_id].append(carta)
        else:
            scarti[user_id].append(carta)

        pescate.append(carta)
        remaining -= 1

    return pescate


def rimischia(user_id):
    if user_id in mazzi:
        # reintegra scarti tranne jolly e mischia
        mazzi[user_id] += [c for c in scarti[user_id] if c not in jolly]
        scarti[user_id] = [c for c in scarti[user_id] if c in jolly]
        mescola_mazzo(mazzi[user_id])
        return True
    return False


def rimetti_jolly(user_id):
    if user_id in mazzi:
        mazzi[user_id] += jolly_in_mano[user_id]
        mescola_mazzo(mazzi[user_id])
        jolly_in_mano[user_id] = []


def get_scarti(user_id):
    if user_id not in scarti:
        return None
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
# Avvio bot
# ===============================
client.run(TOKEN)
