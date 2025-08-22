# Usa immagine Python 3.11
FROM python:3.11-slim

# Imposta la cartella di lavoro
WORKDIR /app

# Copia file di requirements
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . .

# Comando per avviare il bot
CMD ["python", "bot.py"]
