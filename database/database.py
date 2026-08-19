import sqlite3 #mengimpor modul sqlite3 buat koneksi ke database SQLite

conn = sqlite3.connect('kasir.db') #membuka koneksi ke database kasir.db (jika belum ada, maka akan dibuat baru)
cursor = conn.cursor() #membuat cursor buat eksekusi query SQL

cursor.execute("DROP TABLE IF EXISTS products") #menghapus tabel products jika sudah ada (buat mencegah error saat bikin tabel baru)
cursor.execute("DROP TABLE IF EXISTS transactions") #menghapus tabel transactions jika sudah ada (buat mencegah error saat bikin tabel baru)
cursor.execute("DROP TABLE IF EXISTS transaction_details") #menghapus tabel transaction_details jika sudah ada (buat mencegah error saat bikin tabel baru)

cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    image TEXT NOT NULL
)
""") #membuat tabel products

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_price INTEGER NOT NULL,
    paid_amount INTEGER NOT NULL,
    change_amount INTEGER NOT NULL
)
""") #membuat tabel transactions 

cursor.execute("""
CREATE TABLE IF NOT EXISTS transaction_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    subtotal INTEGER NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
""") #membuat tabel transaction_details 

cursor.executemany("""
INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)
""", [
    ('Kopi Hitam', 15000, 50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQaGQ_RtMA6LF5xsIb3-J_n7r_0sJO8fna2SoPSpwhMAQ&s=10'),
    ('Teh Manis', 10000, 40, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRy3_BhYOdvREE8IHdr9ZtRJFOZzrKnKP4jh1Tit8-Vbw&s=10'),
    ('Roti Bakar', 20000, 20, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROizODSSI5qhACtO7zMtbTsGvPAh7uH7vlsTgS7Bc0eg&s=10'),
    ('Air Mineral', 5000, 100, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStmt0hsS1mcJPLa8xMBduVqIwnUaxcH61FrffkBFUL1A&s=10'),
    ('Mie Instan', 8000, 30, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtfZ9zwq1W_bR0NdHwGwMNm9c_kgX3pw4-sCHLXfHEEg&s=10')
]) #menambahkan beberapa data produk ke tabel products dengan menggunakan parameterized query ('?') buat mencegah SQL injection. Data yang ditambahkan berupa nama produk, harga, stok, dan URL gambar produk.

conn.commit() #menyimpan perubahan ke database
conn.close() #menutup koneksi ke database 

print("Database 'kasir.db' berhasil dibuat dan data produk sudah diisi!") 