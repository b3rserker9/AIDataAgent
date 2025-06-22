import json
import os
import time
import logging
from flask import Flask, request, jsonify
from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

files = {
    "categories": "categories.parquet",
    "customers": "customers.parquet",
    "products": "products.parquet",
    "transaction_lines": "transaction_lines.parquet",
    "transactions": "transactions.parquet",
    "brands": "brands.parquet"
}

app = Flask(__name__)
spark = None
dfs = {}

DATASET_PATH = "/app/data/parquet"  # Modifica se vuoi


def create_spark_session(master_url: str) -> SparkSession:
    logger.info("🔧 Inizializzazione SparkSession...")
    spark_session = SparkSession.builder.master(master_url).appName("SupermarketAnalysis").getOrCreate()
    logger.info("✅ SparkSession avviata!")
    return spark_session


def load_parquet_to_view(spark: SparkSession, path: str, view_name: str):
    logger.info(f"📂 Caricamento Parquet: {view_name} da {path}")
    start = time.time()
    try:
        df = spark.read.parquet(path)
        df.createOrReplaceTempView(view_name)
        count = df.count()
        logger.info(f"✅ '{view_name}' caricato con {count} righe in {round(time.time() - start, 2)}s.")
        return df
    except Exception as e:
        logger.error(f"❌ Errore caricamento {view_name}: {e}")
        return None


def init_data():
    global dfs
    for key, filename in files.items():
        full_path = os.path.join(DATASET_PATH, filename)
        df = load_parquet_to_view(spark, full_path, key)
        if df is None:
            raise Exception(f"Non è stato possibile caricare {key}")
        dfs[key] = df.persist()


@app.route("/query", methods=["POST"])
def run_query():
    data = request.json
    if not data or "sql" not in data:
        return jsonify({"error": "Parametro 'sql' mancante"}), 400

    sql_query = data["sql"]
    page = data.get("page", 1)
    page_size = data.get("page_size", 100)

    # Validazioni base su page e page_size
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        page = 1
    try:
        page_size = int(page_size)
        if page_size < 1 or page_size > 1000:
            page_size = 100
    except:
        page_size = 100

    logger.info(f"📋 Query ricevuta: {sql_query} - pagina {page} - page_size {page_size}")

    try:
        start_time = time.time()
        result_df = spark.sql(sql_query)
        total_count = result_df.count()
        logger.info(f"✅ Query eseguita in {round(time.time() - start_time, 2)}s, righe risultato: {total_count}")

        offset = (page - 1) * page_size
        # Limitiamo i dati caricati a offset+page_size per fare paginazione semplice in memoria
        collected = result_df.limit(offset + page_size).toJSON().collect()
        page_items = collected[offset:offset + page_size]

        return jsonify({
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count
            },
            "data": [json.loads(item) for item in page_items]
        })

    except Exception as e:
        logger.error(f"Errore esecuzione query: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    spark = create_spark_session("spark://spark-master:7077")
    init_data()
    app.run(host="0.0.0.0", port=6000)
