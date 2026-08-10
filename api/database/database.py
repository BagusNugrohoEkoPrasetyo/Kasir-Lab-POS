import sqlite3

conn = sqlite3.connect('kasir.db')
cursor = conn.cursor()

# Hapus tabel lama kalau ada (biar bersih)
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("DROP TABLE IF EXISTS transactions")
cursor.execute("DROP TABLE IF EXISTS transaction_details")

# Buat Tabel Produk dengan kolom 'image'
cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    image TEXT NOT NULL
)
""")

# Buat ulang tabel transaksi
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_price INTEGER NOT NULL,
    paid_amount INTEGER NOT NULL,
    change_amount INTEGER NOT NULL
)
""")

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
""")

# Isi Data Produk dengan URL Gambar (Saya pakai Unsplash buat gambar gratis)
cursor.executemany("""
INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)
""", [
    ('Kopi Hitam', 15000, 50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_lTrdyaXSmhinLmhpU8LxFV3pPyqC-MpDRyOtx5MNSg&s=10'),
    ('Teh Manis', 10000, 40, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTIbEse_g6iL0Ip1WDN_fMGzmetCOdyISKqbt25q4DzoQ&s=10'),
    ('Roti Bakar', 20000, 20, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmREaSeD-uVKcP4X5KvEsbvl0UsCIMzyGBUHHU68oGeQ&s=10'),
    ('Air Mineral', 5000, 100, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQDuheBxP4Jp1ilRBoAcQ7SHEWiOtorwBfEBZWzyTH0Mg&s=10'),
    ('Mie Instan', 8000, 30, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtfZ9zwq1W_bR0NdHwGwMNm9c_kgX3pw4-sCHLXfHEEg&s=10')
])

conn.commit()
conn.close()

print("Database 'kasir.db' berhasil dibuat ")