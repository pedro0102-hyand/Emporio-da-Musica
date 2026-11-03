import os
import sqlite3
import json
from langchain_core.tools import tool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "emporio.db")

# build the database path dynamically based on the current file's location
def get_db_connection():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@tool
def search_products(query: str = None, min_price: float = None, max_price: float = None, category_name: str = None) -> str:
    """Busca produtos ativos por texto, faixa de preço e categoria."""

    # connect to the database and execute the query
    conn = get_db_connection()
    cursor = conn.cursor()

    # 
    sql = """
        SELECT p.product_id, p.name, p.price_brl, p.stock_quantity, p.description, p.specs, c.name as category
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.status = 'active'
    """
    params = []
    
    if query:
        sql += " AND (p.name LIKE ? OR p.description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if min_price is not None:
        sql += " AND p.price_brl >= ?"
        params.append(min_price)
    if max_price is not None:
        sql += " AND p.price_brl <= ?"
        params.append(max_price)
    if category_name:
        sql += " AND c.name LIKE ?"
        params.append(f"%{category_name}%")
        
    sql += " ORDER BY p.price_brl ASC LIMIT 10"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "Nenhum produto encontrado com os critérios informados."
    
    results = []
    for r in rows:
        results.append({

            "id": r["product_id"],
            "nome": r["name"],
            "preco_brl": r["price_brl"],
            "estoque": r["stock_quantity"],
            "categoria": r["category"],
            "descricao": r["description"]

        })
    return json.dumps(results, ensure_ascii=False, indent=2)

@tool
def get_order_status(order_identifier: str) -> str:
    """Consulta o status de um pedido pelo ID ou código de rastreio."""

    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
        SELECT o.order_id, o.order_date, o.status, o.total_brl, o.payment_method, 
               o.tracking_code, o.estimated_delivery, o.notes, c.name as customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE CAST(o.order_id AS TEXT) = ? OR o.tracking_code = ?
    """
    cursor.execute(sql, (str(order_identifier), str(order_identifier)))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return f"Nenhum pedido encontrado para a identificação '{order_identifier}'."
    
    order_id = row["order_id"]
    cursor.execute("""
        SELECT p.name, oi.quantity, p.price_brl
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()
    conn.close()
    
    item_list = [{"produto": i["name"], "quantidade": i["quantity"], "preco_unitario": i["price_brl"]} for i in items]
    
    result = {
        "order_id": row["order_id"],
        "cliente": row["customer_name"],
        "data_pedido": row["order_date"],
        "status": row["status"],
        "total_brl": row["total_brl"],
        "forma_pagamento": row["payment_method"],
        "codigo_rastreio": row["tracking_code"] or "Ainda não gerado",
        "previsao_entrega": row["estimated_delivery"] or "A definir",
        "itens": item_list
    }
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool
def get_customer_purchases(contact_info: str) -> str:
    """Busca o histórico de compras de um cliente por email ou telefone."""

    conn = get_db_connection()
    cursor = conn.cursor()
    
    clean_contact = contact_info.strip()
    cursor.execute("""
        SELECT customer_id, name, email, phone 
        FROM customers 
        WHERE email LIKE ? OR phone LIKE ?
    """, (f"%{clean_contact}%", f"%{clean_contact}%"))
    customer = cursor.fetchone()
    
    if not customer:
        conn.close()
        return f"Nenhum cliente cadastrado com a informação '{contact_info}'."
        
    cursor.execute("""
        SELECT order_id, order_date, status, total_brl, tracking_code
        FROM orders
        WHERE customer_id = ?
        ORDER BY order_date DESC
    """, (customer["customer_id"],))
    orders = cursor.fetchall()
    conn.close()
    
    order_list = []
    for o in orders:
        order_list.append({
            "order_id": o["order_id"],
            "data": o["order_date"],
            "status": o["status"],
            "total_brl": o["total_brl"],
            "rastreio": o["tracking_code"] or "Sem rastreio"
        })
        
    result = {
        "cliente": customer["name"],
        "email": customer["email"],
        "telefone": customer["phone"],
        "pedidos": order_list
    }
    return json.dumps(result, ensure_ascii=False, indent=2)