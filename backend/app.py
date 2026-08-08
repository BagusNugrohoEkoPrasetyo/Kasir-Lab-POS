from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
from flask import request
import datetime

app = Flask(__name__)
CORS(app) # Aktifkan CORS agar frontend bisa akses API ini

# Buat path absolut ke file database
# Karena app.py ada di folder backend/, kita naik 1 level (..) lalu masuk folder database/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'kasir.db')

# Fungsi untuk koneksi ke database
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Agar hasil query berbentuk dictionary (key-value)
    return conn

# Bikin Endpoint (Route) untuk mengambil data produk
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    # Ambil semua data dari tabel products
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
  
    # Ubah data SQL menjadi format JSON
    result = [dict(row) for row in products]
    return jsonify(result)

# Endpoint untuk Checkout
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json() # Ambil data JSON dari JavaScript
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. Ambil data dari frontend
        total_price = data['total_price']
        paid_amount = data['paid_amount']
        change_amount = data['change_amount']
        items = data['items'] # Ini adalah array keranjang belanja
        
        # 2. Simpan ke tabel transactions (Header)
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO transactions (date, total_price, paid_amount, change_amount) VALUES (?, ?, ?, ?)",
            (date_now, total_price, paid_amount, change_amount)
        )
        transaction_id = cursor.lastrowid # Ambil ID transaksi yang baru dibuat
        
        # 3. Looping keranjang, simpan ke transaction_details dan kurangi stok
        for item in items:
            # Simpan detail item
            cursor.execute(
                "INSERT INTO transaction_details (transaction_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                (transaction_id, item['id'], item['qty'], item['subtotal'])
            )
            
            # Kurangi stok produk!
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item['qty'], item['id'])
            )
            
        # 4. Simpan permanen perubahan database
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Transaksi berhasil disimpan!", "transaction_id": transaction_id}), 201

    except Exception as e:
        # Kalau ada error, batalkan semua perubahan (Rollback)
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

# API untuk mengambil detail struk berdasarkan ID Transaksi
@app.route('/api/receipt/<int:transaction_id>', methods=['GET'])
def get_receipt(transaction_id):
    conn = get_db()
    
    # Ambil data header transaksi
    header = conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
    
    if not header:
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404

    # Ambil detail item + JOIN dengan tabel products untuk dapat nama produk
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

# 1. API untuk TAMBAH PRODUK
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

# 2. API untuk EDIT PRODUK
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

# 3. API untuk HAPUS PRODUK
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Produk berhasil dihapus!"}), 200

# Jalankan server
if __name__ == '__main__':
    # debug=True agar server otomatis restart kalau ada perubahan kode
    app.run(debug=True, port=5000)