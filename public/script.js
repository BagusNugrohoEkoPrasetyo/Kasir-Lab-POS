let cart = [];
let allProducts = [];
const API_URL = '/api/products';

// Format angka jadi Rupiah (Contoh: 15000 -> Rp 15.000)
function formatRupiah(angka) {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka);
}

// 1. Ambil data produk dari Backend
async function fetchProducts() {
    try {
        const response = await fetch(API_URL);
        const products = await response.json();
        allProducts = products; // Simpan data asli ke allProducts
        displayProducts(allProducts); // Tampilkan ke layar
    } catch (error) {
        console.error("Error:", error);
    }
}

// Fungsi buat nampilin produk ke HTML
function displayProducts(productsToShow) {
    const productList = document.getElementById('product-list');
    productList.innerHTML = '';

    // Kalau produk kosong (hasil search nggak ketemu)
    if (productsToShow.length === 0) {
        productList.innerHTML = '<p class="text-center text-muted mt-4">Produk tidak ditemukan...</p>';
        return;
    }

    productsToShow.forEach(product => {
        productList.innerHTML += `
            <div class="col-3">
                <div class="card product-card p-2" onclick="addToCart(${product.id}, '${product.name}', ${product.price})">
                    <!-- Ganti icon jadi img -->
                    <img src="${product.image}" class="product-img" alt="${product.name}">
                    <div class="card-body text-center p-1">
                        <h6 class="fw-bold mb-1">${product.name}</h6>
                        <small class="text-muted d-block mb-2">Stok: ${product.stock}</small>
                        <span class="badge bg-light text-dark fs-6 p-2">${formatRupiah(product.price)}</span>
                    </div>
                </div>
            </div>
        `;
    });
}

// Event Listener buat Search Bar
document.getElementById('search-product').addEventListener('input', function(e) {
    const searchText = e.target.value.toLowerCase();
    
    // Filter produk yang namanya ada di search bar
    const filteredProducts = allProducts.filter(product => 
        product.name.toLowerCase().includes(searchText)
    );
    
    // Tampilkan produk yang udah difilter
    displayProducts(filteredProducts);
});

// 2. Tambah ke Keranjang
function addToCart(id, name, price) {
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.qty += 1;
    } else {
        cart.push({ id, name, price, qty: 1 });
    }
    renderCart();
}
// Fungsi Tambah Qty
function increaseQty(id) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.qty += 1;
        renderCart(); // Update tampilan
    }
}

// Fungsi Kurang Qty
function decreaseQty(id) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.qty -= 1;
        
        // Kalau Qty sampai 0, hapus item dari keranjang
        if (item.qty <= 0) {
            cart = cart.filter(i => i.id !== id);
        }
        
        renderCart(); // Update tampilan
    }
}
// 3. Tampilan Keranjang
function renderCart() {
    const cartList = document.getElementById('cart-list');
    const cartCount = document.getElementById('cart-count');
    cartList.innerHTML = '';
    
    let total = 0;
    let totalItem = 0;

    if (cart.length === 0) {
        cartList.innerHTML = `<div class="text-center text-muted mt-5"><i class="bi bi-basket2" style="font-size: 3rem;"></i><p class="mt-3">Keranjang masih kosong</p></div>`;
    }

    cart.forEach(item => {
        let subtotal = item.price * item.qty;
        total += subtotal;
        totalItem += item.qty;

        cartList.innerHTML += `
            <div class="cart-item">
                <div class="flex-grow-1">
                    <h6 class="mb-0">${item.name}</h6>
                    <small class="text-muted">${formatRupiah(item.price)}</small>
                </div>
                
                <div class="d-flex align-items-center me-3">
                    <!-- Tombol Minus -->
                    <button class="btn btn-sm btn-outline-danger qty-btn" onclick="decreaseQty(${item.id})">
                        <i class="bi bi-dash"></i>
                    </button>
                    <span class="qty-text">${item.qty}</span>
                    <!-- Tombol Plus -->
                    <button class="btn btn-sm btn-outline-primary qty-btn" onclick="increaseQty(${item.id})">
                        <i class="bi bi-plus"></i>
                    </button>
                </div>

                <div class="text-end" style="width: 90px;">
                    <h6 class="mb-0 fw-bold">${formatRupiah(subtotal)}</h6>
                </div>
            </div>
        `;
    });

    document.getElementById('total-price').innerText = formatRupiah(total);
    cartCount.innerText = `${totalItem} Item`;
    calculateChange();
}

// 4. Hitung Kembalian
function calculateChange() {
    let total = 0;
    cart.forEach(item => total += (item.price * item.qty));
    
    let paid = parseInt(document.getElementById('paid-amount').value) || 0;
    let change = paid - total;
    
    document.getElementById('change-amount').innerText = change >= 0 ? formatRupiah(change) : "Rp 0";
}

// 5. Checkout (Sementara)
async function checkout() {
    let total = 0;
    let totalItem = 0;
    
    // Susun ulang data keranjang agar mudah dibaca Python
    let checkoutItems = cart.map(item => {
        let subtotal = item.price * item.qty;
        total += subtotal;
        totalItem += item.qty;
        return {
            id: item.id,
            qty: item.qty,
            subtotal: subtotal
        };
    });

    let paid = parseInt(document.getElementById('paid-amount').value) || 0;
    let change = paid - total;

    // Validasi Pop-up
    if (cart.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Oops...',
            text: 'Keranjang masih kosong!'
        });
        return;
    }
    if (paid < total) {
        Swal.fire({
            icon: 'error',
            title: 'Uang Kurang',
            text: 'Nominal uang yang dibayar masih kurang!'
        });
        return;
    }

    // Siapkan data yang akan dikirim ke Backend Python
    const payload = {
        total_price: total,
        paid_amount: paid,
        change_amount: change,
        items: checkoutItems
    };

    try {
        // Kirim data ke API Python (POST Request)
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.status === 201) {
            // Pop-up Sukses Checkout
            Swal.fire({
                icon: 'success',
                title: 'Transaksi Berhasil!',
                html: `Total: <b>${formatRupiah(total)}</b><br>Kembalian: <b>${formatRupiah(change)}</b>`,
                confirmButtonText: 'Lihat Struk',
                confirmButtonColor: '#10b981'
            }).then(() => {
                // Kosongkan keranjang setelah berhasil
                cart = [];
                document.getElementById('paid-amount').value = '';
                renderCart();
                
                // Ambil ulang data produk agar stok di layar ikut berkurang!
                fetchProducts();

                // Pindah ke halaman struk bawa ID transaksi
                window.location.href = `receipt.html?id=${result.transaction_id}`;
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Transaksi Gagal',
                text: result.error
            });
        }

    } catch (error) {
        console.error("Error saat checkout:", error);
        Swal.fire({
            icon: 'error',
            title: 'Error Koneksi',
            text: 'Terjadi kesalahan koneksi ke server.'
        });
    }
}

// Jalankan saat halaman dibuka
fetchProducts();
renderCart();