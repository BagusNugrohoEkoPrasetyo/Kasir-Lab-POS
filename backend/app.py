from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'kasir.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(row) for row in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)",
        (data['name'], data['price'], data['stock'], data['image'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Produk berhasil ditambahkan!"}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name = ?, price = ?, stock = ?, image = ? WHERE id = ?",
        (data['name'], data['price'], data['stock'], data['image'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Produk berhasil diperbarui!"}), 200

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Produk berhasil dihapus!"}), 200

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        total_price = data['total_price']
        paid_amount = data['paid_amount']
        change_amount = data['change_amount']
        items = data['items']
        
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO transactions (date, total_price, paid_amount, change_amount) VALUES (?, ?, ?, ?)",
            (date_now, total_price, paid_amount, change_amount)
        )
        transaction_id = cursor.lastrowid
        
        for item in items:
            cursor.execute(
                "INSERT INTO transaction_details (transaction_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                (transaction_id, item['id'], item['qty'], item['subtotal'])
            )
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item['qty'], item['id'])
            )
            
        conn.commit()
        conn.close()
        return jsonify({"message": "Transaksi berhasil disimpan!", "transaction_id": transaction_id}), 201

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/receipt/<int:transaction_id>', methods=['GET'])
def get_receipt(transaction_id):
    conn = get_db()
    header = conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
    
    if not header:
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404

    details = conn.execute('''
        SELECT td.quantity, td.subtotal, p.name, p.price 
        FROM transaction_details td 
        JOIN products p ON td.product_id = p.id 
        WHERE td.transaction_id = ?
    ''', (transaction_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        "header": dict(header),
        "details": [dict(row) for row in details]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)