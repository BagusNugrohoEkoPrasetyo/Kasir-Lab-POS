from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import datetime
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# === KONEKSI KE SUPABASE ===
# Masukkan URL dan Key yang kamu simpan tadi
SUPABASE_URL = "https://yosjwtcxdycqnicrexdf.supabase.co/rest/v1/"  # GANTI INI
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlvc2p3dGN4ZHljcW5pY3JleGRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYzMzQyNDYsImV4cCI6MjEwMTkxMDI0Nn0.9DVQYCIbNo7jxYUtcEEN2A76-yCTz7CfeuiSbrcgv44"   # GANTI INI
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# === API AMBIL PRODUK ===
@app.route('/api/products', methods=['GET'])
def get_products():
    response = supabase.table('products').select("*").execute()
    return jsonify(response.data)

# === API TAMBAH PRODUK ===
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    response = supabase.table('products').insert({
        "name": data['name'],
        "price": data['price'],
        "stock": data['stock'],
        "image": data['image']
    }).execute()
    return jsonify({"message": "Produk berhasil ditambahkan!"}), 201

# === API EDIT PRODUK ===
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    supabase.table('products').update({
        "name": data['name'],
        "price": data['price'],
        "stock": data['stock'],
        "image": data['image']
    }).eq("id", id).execute()
    return jsonify({"message": "Produk berhasil diperbarui!"}), 200

# === API HAPUS PRODUK ===
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    supabase.table('products').delete().eq("id", id).execute()
    return jsonify({"message": "Produk berhasil dihapus!"}), 200

# === API CHECKOUT ===
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Simpan Header Transaksi
    trans_response = supabase.table('transactions').insert({
        "date": date_now,
        "total_price": data['total_price'],
        "paid_amount": data['paid_amount'],
        "change_amount": data['change_amount']
    }).execute()
    
    transaction_id = trans_response.data[0]['id']
    
    # 2. Simpan Detail Item & Kurangi Stok
    for item in data['items']:
        # Masukin detail
        supabase.table('transaction_details').insert({
            "transaction_id": transaction_id,
            "product_id": item['id'],
            "quantity": item['qty'],
            "subtotal": item['subtotal']
        }).execute()
        
        # Kurangi stok
        # Catatan: Ini query sederhana, di dunia nyata butuh atomic transaction biar nggak race condition
        current_stock = supabase.table('products').select("stock").eq("id", item['id']).execute()
        new_stock = current_stock.data[0]['stock'] - item['qty']
        supabase.table('products').update({"stock": new_stock}).eq("id", item['id']).execute()
        
    return jsonify({"message": "Transaksi berhasil disimpan!", "transaction_id": transaction_id}), 201

# === API STRUK ===
@app.route('/api/receipt/<int:transaction_id>', methods=['GET'])
def get_receipt(transaction_id):
    # Ambil Header
    header_res = supabase.table('transactions').select("*").eq("id", transaction_id).execute()
    if not header_res.data:
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404
    header = header_res.data[0]

    # Ambil Detail + Join Manual (Karena Supabase butuh relasi foreign key diset dulu)
    details_res = supabase.table('transaction_details').select("quantity, subtotal, product_id").eq("transaction_id", transaction_id).execute()
    
    details = []
    for d in details_res.data:
        # Ambil nama produk berdasarkan product_id
        prod_res = supabase.table('products').select("name, price").eq("id", d['product_id']).execute()
        prod_data = prod_res.data[0]
        details.append({
            "quantity": d['quantity'],
            "subtotal": d['subtotal'],
            "name": prod_data['name'],
            "price": prod_data['price']
        })
    
    return jsonify({"header": header, "details": details})

# === ROUTING VERCEL ===
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Untuk Vercel, ini nggak dipakai karena udah diatur vercel.json
    return jsonify({"status": "API Kasir Online!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)