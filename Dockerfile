# Immagine base NVIDIA con Python e CUDA 12.1
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crea la cartella dell'app
WORKDIR /app

# Copia i requirements
COPY requirements.txt .

# Installa le librerie Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice sorgente
COPY . .

# Avvia l'app
CMD ["python", "test.py"]
