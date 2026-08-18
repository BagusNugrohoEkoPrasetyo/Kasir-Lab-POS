from flask import Flask, jsonify, request #import Flask buat app web, jsonify buat ngubah data ke JSON, request buat nerima data dari frontend
from flask_cors import CORS #import CORS biar API backend bisa diakses dari frontend
import sqlite3 #import sqlite3 bwat database 
import os #import os buat ngelola path
import datetime

app = Flask(__name__) #membuat instance Flask
CORS(app) #mngaktifkan CORS biar API backend bisa diakses dari frontend

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #mengambil path direktori saat ini
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'kasir.db') #menyusun path ke database kasir.db

def get_db(): #fungsi buat koneksi ke database
    conn = sqlite3.connect(DB_PATH) #koneksi ke database kasir.db
    conn.row_factory = sqlite3.Row #mengatur row_factory biar hasil query bisa diakses kayak dictionary
    return conn #mengembalikan objek koneksi database

@app.route('/api/products', methods=['GET']) #buat ngambil data produk
def get_products(): 
    conn = get_db() 
    products = conn.execute('SELECT * FROM products').fetchall() #menjalankan query buat ngambil semua data produk dari tabel products
    conn.close() 
    return jsonify([dict(row) for row in products]) #mengonversi setiap row hasil query ke dictionary dan mengembalikannya sebagai JSON

@app.route('/api/products', methods=['POST']) #buat nambah data produk
def add_product():
    data = request.get_json() #membaca data JSON dari request body
    conn = get_db() 
    cursor = conn.cursor() #membuat cursor buat eksekusi query
    cursor.execute( 
        "INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)", #menggunakan parameterized query ('?') buat mencegah SQL injection
        (data['name'], data['price'], data['stock'], data['image']) #mengambil data buat dimasukin ke query INSERT
    )
    conn.commit() #menyimpan perubahan ke database
    conn.close() 
    return jsonify({"message": "Produk berhasil ditambahkan!"}), 201 #201 (Created)

@app.route('/api/products/<int:id>', methods=['PUT']) #buat update data produk berdasarkan id
def update_product(id): 
    data = request.get_json() 
    conn = get_db() 
    cursor = conn.cursor() 
    cursor.execute( 
        "UPDATE products SET name = ?, price = ?, stock = ?, image = ? WHERE id = ?", 
        (data['name'], data['price'], data['stock'], data['image'], id) #mengambil data buat dimasukin ke query UPDATE
    )
    conn.commit() 
    conn.close() 
    return jsonify({"message": "Produk berhasil diperbarui!"}), 200 #200 (OK)

@app.route('/api/products/<int:id>', methods=['DELETE']) #buat hapus data produk berdasarkan id
def delete_product(id):
    conn = get_db() 
    cursor = conn.cursor() 
    cursor.execute("DELETE FROM products WHERE id = ?", (id,)) # query buat hapus data produk di tabel products berdasarkan id
    conn.commit() 
    conn.close() 
    return jsonify({"message": "Produk berhasil dihapus!"}), 200 #200 (OK)

@app.route('/api/checkout', methods=['POST']) #buat proses checkout
def checkout(): 
    data = request.get_json() 
    conn = get_db() 
    cursor = conn.cursor() 
    
    try: #membuka blok try buat menangani error
        total_price = data['total_price'] #mengambil total harga dari data JSON
        paid_amount = data['paid_amount'] #mengambil jumlah uang yang dibayarkan dari data JSON
        change_amount = data['change_amount'] #mengambil jumlah kembalian dari data JSON
        items = data['items'] #mengambil array item yang dibeli dari data JSON
        
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #mengambil tanggal dan waktu saat ini dan memformatnya dalam format "YYYY-MM-DD HH:MM:SS"
        cursor.execute( 
            "INSERT INTO transactions (date, total_price, paid_amount, change_amount) VALUES (?, ?, ?, ?)", 
            (date_now, total_price, paid_amount, change_amount) #mengambil data dari request body dan tanggal saat ini buat dimasukin ke query INSERT
        )
        transaction_id = cursor.lastrowid #mengambil id transaksi yang baru saja ditambahkan
        
        for item in items: #looping buat setiap item yang dibeli
            cursor.execute( 
                "INSERT INTO transaction_details (transaction_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)", 
                (transaction_id, item['id'], item['qty'], item['subtotal']) #mengambil data dari item yang dibeli dan id transaksi buat dimasukin ke query INSERT
            )
            cursor.execute( 
                "UPDATE products SET stock = stock - ? WHERE id = ?", 
                (item['qty'], item['id']) #mengambil data dari item yang dibeli buat dimasukin ke query UPDATE
            )
            
        conn.commit() 
        conn.close() 
        return jsonify({"message": "Transaksi berhasil disimpan!", "transaction_id": transaction_id}), 201 #code 201 (Created) dan id transaksi yang baru saja ditambahkan

    except Exception as e: #menangkap error yang terjadi selama proses checkout
        conn.rollback() #membatalkan perubahan yang belum disimpan ke database
        conn.close() 
        return jsonify({"error": str(e)}), 500 #code 500 (Internal Server Error) dan pesan error yang terjadi

@app.route('/api/receipt/<int:transaction_id>', methods=['GET']) #buat ngambil data struk transaksi berdasarkan id transaksi
def get_receipt(transaction_id): 
    conn = get_db() 
    header = conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone() #query buat ngambil data header transaksi dari tabel transactions berdasarkan id transaksi
    
    if not header: #ngecek kalo data transaksi ga ada, kalo ga ada, ngembaliin error 404
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404

    details = conn.execute(''' 
        SELECT td.quantity, td.subtotal, p.name, p.price 
        FROM transaction_details td 
        JOIN products p ON td.product_id = p.id 
        WHERE td.transaction_id = ?
    ''', (transaction_id,)).fetchall() # query buat ngambil data detail transaksi dari tabel transaction_details dan tabel products berdasarkan id transaksi
    
    conn.close() 
    
    return jsonify({ #mengirim respon data struk transaksi dalam format JSON
        "header": dict(header), #mengonversi hasil query header ke dictionary
        "details": [dict(row) for row in details] #mengonversi setiap row hasil query details ke dictionary dan mengembalikannya sebagai list
    })

if __name__ == '__main__': #ngecek kalo file ini dijalankan langsung, bukan diimport dari file lain
    app.run(debug=True, port=5000) #menjalankan server Flask di localhost dengan port 5000 dan mode debug aktif