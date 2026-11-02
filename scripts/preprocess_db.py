import os
import json
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "emporio.db")


CSV_FILES = {
    "categories": "desafio_tecnico_ai_eng - categories.csv",
    "customers": "desafio_tecnico_ai_eng - customers.csv",
    "order_items": "desafio_tecnico_ai_eng - order_items.csv",
    "orders": "desafio_tecnico_ai_eng - orders.csv",
    "products": "desafio_tecnico_ai_eng - products.csv",
    "promotions": "desafio_tecnico_ai_eng - promotions.csv"
}

def preprocess_and_load_db():

    print("🔄 Iniciando pré-processamento e carga no SQLite...")
    os.makedirs(DATA_DIR, exist_ok=True)

    # build the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # create tables and load data from CSV files
    for table_name, csv_filename in CSV_FILES.items():
        file_path = os.path.join(DATA_DIR, csv_filename)
    
        if not os.path.exists(file_path):
            file_path = os.path.join(BASE_DIR, csv_filename)

        if not os.path.exists(file_path):
            print(f"⚠️ Arquivo {csv_filename} não encontrado. Ignorando...")
            continue

        df = pd.read_csv(file_path)

        # jsonify the 'specs' column in products table if it exists
        if table_name == "products" and "specs" in df.columns:
            df["specs"] = df["specs"].apply(lambda x: json.dumps(json.loads(x)) if isinstance(x, str) else "{}")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"✅ Tabela '{table_name}' criada com sucesso ({len(df)} registros).")

    print("⚡ Criando índices de alta performance...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_price ON products(price_brl);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_tracking ON orders(tracking_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);")

    conn.commit()
    conn.close()
    print(f"🎉 Banco de dados relacional gerado com sucesso em: {DB_PATH}")

if __name__ == "__main__":
    preprocess_and_load_db()