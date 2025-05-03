from flask import Flask, request, jsonify
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import logging

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
table_schema="""tables:
CREATE TABLE aisles (aisle_id INT, aisle VARCHAR);
CREATE TABLE departments (department_id INT, department VARCHAR);
CREATE TABLE order_products_prior (order_id INT, product_id INT, add_to_cart_order INT, reordered INT);
CREATE TABLE order_products_train (order_id INT, product_id INT, add_to_cart_order INT, reordered INT);
CREATE TABLE orders (order_id INT, user_id INT, eval_set VARCHAR, order_number INT, order_dow INT, order_hour_of_day INT, days_since_prior_order DOUBLE);
CREATE TABLE products (product_id INT, product_name VARCHAR, aisle_id VARCHAR, department_id VARCHAR);
query for: """
# Inizializza Flask
app = Flask(__name__)

# Seleziona il dispositivo: GPU se disponibile, altrimenti CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Usando il dispositivo: {device}")

# Carica tokenizer e modello
model_id = "cssupport/t5-small-awesome-text-to-sql"
logger.info(f"Caricamento del modello: {model_id}")
tokenizer = T5Tokenizer.from_pretrained("t5-small")  # Il tokenizer è "t5-small"
model = T5ForConditionalGeneration.from_pretrained(model_id).to(device)
model.eval()

# Funzione per generare SQL
def generate_sql(input_prompt):
    logger.info(f"Ricevuto prompt: {input_prompt}")
    inputs = tokenizer(input_prompt, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=512)
    generated_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    logger.info(f"SQL generato: {generated_sql}")
    return generated_sql

# Rotta API POST per generare SQL
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt mancante"}), 400
    try:
        full_prompt = table_schema + prompt
        sql = generate_sql(full_prompt)
        logger.info(f"SQL generato: {sql}")
        return jsonify({"sql": sql})
    except Exception as e:
        logger.exception("Errore nella generazione della query")
        return jsonify({"error": str(e)}), 500

# Avvio del server Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
