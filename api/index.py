from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import datetime

app = Flask(__name__)
CORS(app)

# === KONEKSI KE SUPABASE (Pakai REST API) ===
SUPABASE_URL = "https://yosjwtcxdycqnicrexdf.supabase.co/rest/v1/"  # GANTI INI
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlvc2p3dGN4ZHljcW5pY3JleGRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYzMzQyNDYsImV4cCI6MjEwMTkxMDI0Nn0.9DVQYCIbNo7jxYUtcEEN2A76-yCTz7CfeuiSbrcgv44"   # GANTI INI (anon public key)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# === API AMBIL PRODUK ===
@app.route('/api/products', methods=['GET'])
def get_products():
    url = f"{SUPABASE_URL}/rest/v1/products?select=*"
    res = requests.get(url, headers=HEADERS)
    return jsonify(res.json())

# === API TAMBAH PRODUK ===
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    url = f"{SUPABASE_URL}/rest/v1/products"
    payload = {
        "name": data['name'],
        "price": data['price'],
        "stock": data['stock'],
        "image": data['image']
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    return jsonify({"message": "Produk berhasil ditambahkan!"}), 201

# === API EDIT PRODUK ===
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{id}"
    payload = {
        "name": data['name'],
        "price": data['price'],
        "stock": data['stock'],
        "image": data['image']
    }
    # Supabase pakai method PATCH buat update, jadi kita patch lewat requests
    requests.patch(url, headers=HEADERS, json=payload)
    return jsonify({"message": "Produk berhasil diperbarui!"}), 200

# === API HAPUS PRODUK ===
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{id}"
    requests.delete(url, headers=HEADERS)
    return jsonify({"message": "Produk berhasil dihapus!"}), 200

# === API CHECKOUT ===
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Simpan Header Transaksi (Pakai header khusus biar dapet ID balikannya)
    headers_rep = HEADERS.copy()
    headers_rep["Prefer"] = "return=representation"
    
    url_trans = f"{SUPABASE_URL}/rest/v1/transactions"
    payload_trans = {
        "date": date_now,
        "total_price": data['total_price'],
        "paid_amount": data['paid_amount'],
        "change_amount": data['change_amount']
    }
    res_trans = requests.post(url_trans, headers=headers_rep, json=payload_trans)
    transaction_id = res_trans.json()[0]['id']
    
    # 2. Simpan Detail Item & Kurangi Stok
    for item in data['items']:
        url_detail = f"{SUPABASE_URL}/rest/v1/transaction_details"
        payload_detail = {
            "transaction_id": transaction_id,
            "product_id": item['id'],
            "quantity": item['qty'],
            "subtotal": item['subtotal']
        }
        requests.post(url_detail, headers=HEADERS, json=payload_detail)
        
        # Ambil stok sekarang
        url_prod = f"{SUPABASE_URL}/rest/v1/products?id=eq.{item['id']}&select=stock"
        res_prod = requests.get(url_prod, headers=HEADERS)
        current_stock = res_prod.json()[0]['stock']
        new_stock = current_stock - item['qty']
        
        # Update stok baru
        url_update = f"{SUPABASE_URL}/rest/v1/products?id=eq.{item['id']}"
        requests.patch(url_update, headers=HEADERS, json={"stock": new_stock})
        
    return jsonify({"message": "Transaksi berhasil disimpan!", "transaction_id": transaction_id}), 201

# === API STRUK ===
@app.route('/api/receipt/<int:transaction_id>', methods=['GET'])
def get_receipt(transaction_id):
    # Ambil Header
    url_trans = f"{SUPABASE_URL}/rest/v1/transactions?id=eq.{transaction_id}&select=*"
    res_trans = requests.get(url_trans, headers=HEADERS)
    if not res_trans.json():
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404
    header = res_trans.json()[0]

    # Ambil Detail
    url_details = f"{SUPABASE_URL}/rest/v1/transaction_details?transaction_id=eq.{transaction_id}&select=quantity,subtotal,product_id"
    res_details = requests.get(url_details, headers=HEADERS)
    
    details = []
    for d in res_details.json():
        url_prod = f"{SUPABASE_URL}/rest/v1/products?id=eq.{d['product_id']}&select=name,price"
        res_prod = requests.get(url_prod, headers=HEADERS)
        prod_data = res_prod.json()[0]
        details.append({
            "quantity": d['quantity'],
            "subtotal": d['subtotal'],
            "name": prod_data['name'],
            "price": prod_data['price']
        })
    
    return jsonify({"header": header, "details": details})

if __name__ == '__main__':
    app.run(debug=True, port=5000)