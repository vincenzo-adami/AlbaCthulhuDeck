# base image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# copia file principali
COPY . .

# installa dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# comando di avvio
CMD ["python", "bot.py"]
