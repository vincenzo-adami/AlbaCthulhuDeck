# --- Stage 0: Base ---
FROM python:3.11-slim AS base

# Imposta la working directory
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Installa dipendenze
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# Aggiungi venv al PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copia tutto il codice (incluso utils)
COPY . .

# --- Stage 1: Final ---
FROM python:3.11-slim

WORKDIR /app

# Copia venv e codice dallo stage precedente
COPY --from=base /opt/venv /opt/venv
COPY --from=base /app /app

ENV PATH="/opt/venv/bin:$PATH"

# Comando per avviare il bot
CMD ["python", "bot.py"]
