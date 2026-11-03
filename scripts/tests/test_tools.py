import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.db_tools import search_products, get_order_status, get_customer_purchases
from src.rag_tools import consult_store_policies

def run_tests():

    print("==================================================")
    print("🧪 1. TESTE DA TOOL: search_products")
    print("==================================================")
    res_prod = search_products.invoke({"query": "violão", "max_price": 1000.0})
    print(res_prod)

    print("\n==================================================")
    print("🧪 2. TESTE DA TOOL: get_order_status")
    print("==================================================")
    res_order = get_order_status.invoke({"order_identifier": "1"})
    print(res_order)

    print("\n==================================================")
    print("🧪 3. TESTE DA TOOL: get_customer_purchases")
    print("==================================================")
    res_cust = get_customer_purchases.invoke({"contact_info": "lucas.mendes@jmail.com"})
    print(res_cust)

    print("\n==================================================")
    print("🧪 4. TESTE DA TOOL: consult_store_policies")
    print("==================================================")
    res_policy = consult_store_policies.invoke({"query": "Qual a política de devolução por arrependimento?"})
    print(res_policy[:400] + "...\n")

if __name__ == "__main__":
    run_tests()