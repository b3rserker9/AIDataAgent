# Usa un'immagine base con Python 3.9
FROM python:3.9-slim

# Aggiorna e installa le dipendenze necessarie
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crea una directory per il progetto
WORKDIR /app

# Copia il file requirements.txt e installa le librerie
COPY requirements.txt .

# Installa Hugging Face Transformers e PyTorch (se non già presenti)
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'app nel contenitore
COPY . .

# Comando di default per avviare il server
CMD ["python", "test.py"]
