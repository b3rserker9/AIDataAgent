from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Carica il modello e il tokenizer
model_id = "defog/sqlcoder-7b-2"
logger.info(f"Caricamento del modello: {model_id}")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda")
logger.info(f"Modello {model_id} caricato correttamente.")


@app.route('/generate', methods=['POST'])
def generate_sql():
    data = request.get_json()
    prompt = data.get('prompt', '')

    logger.info(
        f"Ricevuta richiesta con il prompt: {prompt[:100]}...")  # Logga solo una parte del prompt per motivi di sicurezza

    if not prompt:
        logger.warning("Prompt mancante nella richiesta.")
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # Tokenizza l'input
        logger.info("Tokenizzazione del prompt...")
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

        # Genera la query SQL
        logger.info("Generazione della query SQL...")
        outputs = model.generate(**inputs, max_new_tokens=150)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)

        logger.info("Generazione della query SQL completata.")
        return jsonify({'response': result})

    except Exception as e:
        logger.error(f"Errore durante la generazione della query SQL: {str(e)}")
        return jsonify({'error': 'Errore durante la generazione della query SQL'}), 500


if __name__ == '__main__':
    logger.info("Avvio del server Flask...")
    app.run(host='0.0.0.0', port=5000)
