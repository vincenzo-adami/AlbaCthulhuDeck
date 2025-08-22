import discord
from discord.ext import commands
from decks import create_deck, shuffle_deck

# --- Legge il token ---
# Railway → lo prende dalle "Environment Variables"
# Locale → se hai un .env puoi usare python-dotenv, altrimenti puoi esportarlo a mano con:
#    export DISCORD_TOKEN=il_tuo_token   (Linux/Mac)
#    setx DISCORD_TOKEN "il_tuo_token"   (Windows)

TOKEN = "IL_TUO_TOKEN"  # oppure Railway lo passerà come env
if not TOKEN:
    raise ValueError("❌ Errore: variabile DISCORD_TOKEN non trovata! "
                     "Configura l'env su Railway oppure in locale.")

# --- Setup bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Stato del mazzo e scarti ---
deck = []
scarti = []

# --- Eventi ---
@bot.event
async def on_ready():
    print(f"✅ Bot connesso come {bot.user}")

# --- Comandi slash ---
@bot.tree.command(name="mischia", description="Mischia il mazzo (senza jolly)")
async def mischia(interaction: discord.Interaction):
    global deck, scarti
    deck = create_deck(include_jokers=False)
    shuffle_deck(deck)
    scarti = []
    await interaction.response.send_message("🔄 Mazzo rimescolato senza jolly!")

@bot.tree.command(name="jolly", description="Aggiunge i jolly e rimescola tutto")
async def jolly(interaction: discord.Interaction):
    global deck, scarti
    deck = create_deck(include_jokers=True)
    shuffle_deck(deck)
    scarti = []
    await interaction.response.send_message("🃏 Mazzo rimescolato con jolly!")

@bot.tree.command(name="pesca", description="Pesca una o più carte dal mazzo")
async def pesca(interaction: discord.Interaction, numero: int = 1):
    global deck, scarti
    if numero > len(deck):
        await interaction.response.send_message("❌ Non ci sono abbastanza carte nel mazzo!")
        return

    carte_pescate = [deck.pop(0) for _ in range(numero)]
    scarti.extend(carte_pescate)

    # Se esce l'asso di picche, rimischia in automatico
    if "A♠️" in carte_pescate:
        deck = create_deck(include_jokers=("🃏" in scarti))
        shuffle_deck(deck)
        scarti = []
        await interaction.response.send_message("🂡 È uscito l'asso di ♠️! Il mazzo è stato rimescolato.")
    else:
        await interaction.response.send_message(f"🎴 Carte pescate: {', '.join(carte_pescate)}")

@bot.tree.command(name="scarti", description="Mostra tutte le carte scartate")
async def mostra_scarti(interaction: discord.Interaction):
    global scarti
    if not scarti:
        await interaction.response.send_message("⚪ Nessuna carta scartata.")
        return

    # Metti i jolly in cima
    jolly = [c for c in scarti if c == "🃏"]
    altri = [c for c in scarti if c != "🃏"]

    semi = {"♠️": [], "♥️": [], "♦️": [], "♣️": []}
    for c in altri:
        for s in semi.keys():
            if s in c:
                semi[s].append(c)

    # Ordina le carte
    valori = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    for s in semi:
        semi[s].sort(key=lambda c: valori.index(c[:-2]))

    # Costruisci messaggio
    messaggio = []
    if jolly:
        messaggio.append("🃏 Jolly: " + ", ".join(jolly))
    for s, carte in semi.items():
        if carte:
            messaggio.append(f"{s}: " + ", ".join(carte))

    await interaction.response.send_message("\n".join(messaggio))

# --- Avvio ---
bot.run(TOKEN)
