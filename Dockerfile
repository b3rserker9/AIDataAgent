FROM openjdk:17-jdk-slim

# Installazione Python3 e pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Installazione dipendenze Python
RUN pip3 install --no-cache-dir pyspark==4.0.0 flask

COPY sparkInit.py /app/sparkInit.py
WORKDIR /app

EXPOSE 6000

# Comando di avvio: puoi cambiare con il nome del tuo script
CMD ["python3", "sparkInit.py"]
