# Base image
FROM python:3.11-slim

# Imposta la working directory
WORKDIR /app

# Copia solo requirements per caching
COPY requirements.txt .

# Installa dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia TUTTO il resto (inclusa la cartella utils)
COPY . .

# Comando per avviare il bot
CMD ["python", "bot.py"]
