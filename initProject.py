import kagglehub
import pandas as pd
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("✅ Log visibile")
# Dizionario file CSV (come prima)
files = {
    "categories": "categories_dataset.csv",
    "customers": "customers_dataset.csv",
    "products": "products_dataset.csv",
    "transaction_lines": "transaction_lines_dataset.csv",
    "transactions": "transactions_dataset.csv",
    "brands": "brands_dataset.csv"
}

# 🔹 2. Download del dataset
print("🚀 Avvio download del dataset da KaggleHub...")
dataset_path = kagglehub.dataset_download("nadinramadan/supermarket-transactional-data")
print(f"✅ Dataset scaricato in: {dataset_path}")
# Percorso della directory dove si trova lo script Python
base_dir = os.path.dirname(os.path.abspath(__file__))

# Percorso dove salvare i parquet
parquet_base_path = os.path.join(base_dir, "data", "parquet")
os.makedirs(parquet_base_path, exist_ok=True)
print(os.path.abspath(parquet_base_path))
for key, filename in files.items():
    csv_file = os.path.join(dataset_path, filename)
    parquet_file = os.path.join(parquet_base_path, f"{key}.parquet")

    print(f"📂 Leggo {csv_file}...")

    df = pd.read_csv(csv_file, encoding='latin1', low_memory=False)

    print(f"💾 Salvo in Parquet: {parquet_file}...")

    df.to_parquet(parquet_file, engine='pyarrow', index=False)

    print(f"✅ {key} convertito in Parquet.")