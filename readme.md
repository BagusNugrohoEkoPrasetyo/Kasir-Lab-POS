Kasir Lab POS (Point of Sale)
Aplikasi Kasir (Point of Sale) berbasis web yang dibangun dengan arsitektur Full-Stack. Aplikasi ini dirancang untuk mengelola transaksi penjualan, manajemen produk, dan pencetakan struk secara real-time.

Projek ini menggunakan Python (Flask) sebagai backend API, SQLite sebagai database, serta HTML, Vanilla JS, dan Bootstrap 5 untuk antarmuka pengguna (frontend).

Fitur Utama
Halaman Kasir (POS): Menampilkan grid produk yang diambil langsung dari database.
Keranjang Belanja Interaktif: Tambah dan kurang jumlah barang (qty) langsung di keranjang.
Kalkulasi Otomatis: Perhitungan total harga dan kembalian secara real-time.
Manajemen Produk (CRUD): Halaman admin untuk menambah, mengubah, dan menghapus data menu. Dilengkapi dengan live preview URL gambar.
Pencetakan Struk (Receipt): Generate struk transaksi yang rapi dan bisa langsung di-save sebagai PDF menggunakan CSS @media print.
Manajemen Stok Otomatis: Stok produk di database akan berkurang otomatis setiap kali transaksi berhasil di-checkout.
    Tech Stack
        Backend:
            Python (Flask)
            Flask-CORS
            SQLite3
        Frontend:
            HTML5 & CSS3
            JavaScript (Vanilla JS, Fetch API)
            Bootstrap 5 & Bootstrap Icons
            Google Fonts (Poppins)

📁 Struktur Folder
Projek-kasir-Python/├── backend/│   └── app.py          # Server API dan logika backend (Flask)├── database/│   ├── database.py     # Script inisialisasi & dummy data database│   └── kasir.db        # File database SQLite (auto-generated)├── frontend/│   ├── index.html      # Halaman utama kasir│   ├── script.js       # Logika halaman kasir (Cart, Checkout)│   ├── manage.html     # Halaman admin kelola menu (CRUD)│   ├── manage.js       # Logika halaman admin│   └── receipt.html    # Halaman struk transaksi└── README.md

Cara Menjalankan Projek
Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal:

1. Persiapan
Pastikan Python dan pip sudah terinstall di komputer. Install library yang dibutuhkan:
pip install flask flask-cors

2. Setup Database
Buka terminal, masuk ke folder database/, dan jalankan script Python untuk membuat database dan mengisi data awal:
cd database
python database.py
(Jika muncul tulisan "Database berhasil dibuat...", berarti sukses).

3. Jalankan Backend Server
Buka terminal baru, masuk ke folder backend/, dan jalankan server Flask:
cd backend
python app.py
(Server akan berjalan di http://127.0.0.1:5000. Biarkan terminal ini tetap terbuka).

4. Jalankan Frontend
Buka folder frontend/, lalu buka file index.html menggunakan browser (Google Chrome/Edge) atau gunakan ekstensi Live Server di VS Code.

📡 Daftar API Endpoint
Method
Endpoint
Deskripsi
GET	/api/products	Mengambil daftar semua produk
POST	/api/products	Menambahkan produk baru
PUT	/api/products/<id>	Mengubah data produk berdasarkan ID
DELETE	/api/products/<id>	Menghapus produk berdasarkan ID
POST	/api/checkout	Memproses transaksi dan mengurangi stok
GET	/api/receipt/<id>	Mengambil detail struk berdasarkan ID transaksi

💡 Catatan Teknis (Poin Pengembangan)
Keamanan Data (ACID): Proses checkout menggunakan try-except dan rollback() di Python untuk mencegah data tersimpan tidak sengaja jika terjadi error di tengah transaksi.
Normalisasi Database: Transaksi dipisah menjadi 2 tabel (transactions untuk header, transaction_details untuk item) agar data tidak redundan.