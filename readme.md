Kasirku (Frontend)

Aplikasi Kasir dan Manajemen Produk berbasis web (*Point of Sales*) yang responsif, cepat, dan intuitif. Aplikasi ini memfasilitasi transaksi penjualan, manajemen inventoris (CRUD Produk), kalkulasi kembalian otomatis, serta pencetakan struk belanja fisik maupun digital.

Fitur Utama

Antarmuka Kasir (POS):
  - Pemilihan produk langsung via kartu (card view).
  - Pencarian produk secara real-time berdasarkan nama.
  - Manajemen keranjang (tambah, kurangi qty, hapus otomatis jika qty 0).
  - Kalkulasi total belanja dan kembalian secara presisi.
  - Format harga otomatis sesuai mata uang Indonesia (Rupiah).
Manajemen Produk (CRUD):
  - Menampilkan daftar produk lengkap dengan gambar thumbnail dan stok.
  - Fitur Tambah dan Edit produk melalui Modal Pop-up Bootstrap.
  - Real-time preview gambar produk via URL.
  - Penghapusan produk dengan konfirmasi keamanan.
Struk Transaksi (Receipt):
  - Tampilan struk bergaya thermal print menggunakan font monospace.
  - Integrasi pencetakan langsung via browser (`window.print()`) / cetak ke PDF.
  - Tata letak khusus (Print CSS) yang otomatis menyembunyikan elemen navigasi saat dicetak.


Teknologi yang Digunakan

Frontend:
  - HTML5 & CSS3
  - JavaScript (ES6+ Async/Await, Fetch API)
  - Bootstrap 5 (Framework Layout & Component)
  - Bootstrap Icons
  - Google Fonts (Roboto Mono)
Backend (API External):
  - Flask REST API (`http://127.0.0.1:5000`)
