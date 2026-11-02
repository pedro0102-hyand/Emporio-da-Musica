import os
import json
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

CSV_FILES = {
    "categories": "desafio_tecnico_ai_eng - categories.csv",
    "customers": "desafio_tecnico_ai_eng - customers.csv",
    "order_items": "desafio_tecnico_ai_eng - order_items.csv",
    "orders": "desafio_tecnico_ai_eng - orders.csv",
    "products": "desafio_tecnico_ai_eng - products.csv",
    "promotions": "desafio_tecnico_ai_eng - promotions.csv"
}

# function to load CSV files into pandas DataFrames
def load_dataframes():
    
    dfs = {} # dictionary to hold DataFrames
    for table_name, filename in CSV_FILES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            file_path = filename  

        if os.path.exists(file_path):
            dfs[table_name] = pd.read_csv(file_path)
        else:
            print(f"⚠️ Arquivo {filename} não encontrado.")
    return dfs

def analyze_data_types_and_nulls(dfs):

    print("=" * 60)
    print(" 📊 1. ANÁLISE DE TIPOS DE DADOS E VALORES NULOS")
    print("=" * 60)
    
    for name, df in dfs.items():
        print(f"\n--- TABELA: {name.upper()} ({df.shape[0]} linhas, {df.shape[1]} colunas) ---")
        info_df = pd.DataFrame({
            "Tipo": df.dtypes,
            "Nulos": df.isnull().sum(),
            "% Nulos": (df.isnull().sum() / len(df) * 100).round(1)
        })
        print(info_df)

def check_referential_integrity(dfs):
   
    print("\n" + "=" * 60)
    print(" 🔗 2. VALIDAÇÃO DE INTEGRIDADE REFERENCIAL")
    print("=" * 60)
    
    # 1. Orders -> Customers
    orphan_cust = set(dfs['orders']['customer_id']) - set(dfs['customers']['customer_id'])
    print(f"• Pedidos com customer_id inválido: {len(orphan_cust)}")

    # 2. Order_items -> Orders
    orphan_orders = set(dfs['order_items']['order_id']) - set(dfs['orders']['order_id'])
    print(f"• Itens de pedido com order_id inválido: {len(orphan_orders)}")

    # 3. Order_items -> Products
    orphan_items_prod = set(dfs['order_items']['product_id']) - set(dfs['products']['product_id'])
    print(f"• Itens de pedido com product_id inválido: {len(orphan_items_prod)}")

    # 4. Products -> Categories
    orphan_cat = set(dfs['products']['category_id']) - set(dfs['categories']['category_id'])
    print(f"• Produtos com category_id inválido: {len(orphan_cat)}")

    # 5. Promotions -> Products
    orphan_prom = set(dfs['promotions']['product_id']) - set(dfs['products']['product_id'])
    print(f"• Promoções com product_id inválido: {len(orphan_prom)}")

def inspect_json_specs(dfs):
   
    print("\n" + "=" * 60)
    print(" 🧬 3. ANÁLISE DO CAMPO JSON 'specs' (PRODUCTS)")
    print("=" * 60)

    if 'products' not in dfs or 'specs' not in dfs['products'].columns:
        print("Tabela 'products' ou coluna 'specs' não encontrada.")
        return

    products_df = dfs['products']
    specs_list = []
    all_keys = set()
    invalid_jsons = 0

    for idx, row in products_df.iterrows():
        try:
            parsed = json.loads(row['specs'])
            specs_list.append(parsed)
            all_keys.update(parsed.keys())
        except Exception as e:
            invalid_jsons += 1

    print(f"• Total de registros processados: {len(products_df)}")
    print(f"• JSONs inválidos: {invalid_jsons}")
    print(f"• Todas as chaves encontradas no JSON: {sorted(list(all_keys))}\n")

    if 'categories' in dfs:
        merged = products_df.merge(dfs['categories'], on='category_id')
        cat_specs = {}

        for _, row in merged.iterrows():
            cat_name = row['name_y']
            s = json.loads(row['specs'])
            if cat_name not in cat_specs:
                cat_specs[cat_name] = set()
            cat_specs[cat_name].update(s.keys())

        print("--- Chaves do JSON por Categoria ---")
        for cat, keys in cat_specs.items():
            print(f"• {cat}: {sorted(list(keys))}")

if __name__ == "__main__":

    dfs = load_dataframes()
    if dfs:
        analyze_data_types_and_nulls(dfs)
        check_referential_integrity(dfs)
        inspect_json_specs(dfs)