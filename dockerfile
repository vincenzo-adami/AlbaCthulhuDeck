# Usa Python 3.12 slim
FROM python:3.12-slim

# Imposta la working directory
WORKDIR /app

# Copia tutti i file del progetto nella cartella di lavoro
COPY . /app

# Installa le dipendenze
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir discord.py

# Imposta la variabile d'ambiente del token se non la passi da Railway
# ENV TOKEN=your_token_here

# Comando per lanciare il bot
CMD ["python", "bot.py"]
