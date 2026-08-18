let cart = [];//array untuk menyimpan data produk yang ditambahkan ke keranjang belanja
let allProducts = [];// array untuk menyimpan semua data produk yang diambil dari server
const API_URL = 'http://127.0.0.1:5000/api/products';

function formatRupiah(angka) {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka);
}

async function fetchProducts() {
    try {
        const response = await fetch(API_URL);
        const products = await response.json();
        allProducts = products;
        displayProducts(allProducts);
    } catch (error) {
        console.error("Error:", error);
    }
}

function displayProducts(productsToShow) {//fungsi untuk menampilkan produk yang diambil dari server ke dalam elemen HTML
    const productList = document.getElementById('product-list');
    productList.innerHTML = '';

    if (productsToShow.length === 0) {
        productList.innerHTML = '<p class="text-center text-muted mt-4">Produk tidak ditemukan...</p>';
        return;
    }

    productsToShow.forEach(product => {
        productList.innerHTML += `
            <div class="col-3">
                <div class="card product-card p-2" onclick="addToCart(${product.id}, '${product.name.replace(/'/g, "\\'")}', ${product.price})">
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

document.getElementById('search-product').addEventListener('input', function(e) {//fungsi untuk mencari produk berdasarkan nama saat pengguna mengetik di input pencarian
    const searchText = e.target.value.toLowerCase();
    const filteredProducts = allProducts.filter(product => product.name.toLowerCase().includes(searchText));
    displayProducts(filteredProducts);
});

function addToCart(id, name, price) {//fungsi untuk menambahkan produk ke keranjang belanja
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.qty += 1;
    } else {
        cart.push({ id, name, price, qty: 1 });
    }
    renderCart();
}

function increaseQty(id) {//fungsi untuk menambah jumlah produk di keranjang belanja
    const item = cart.find(item => item.id === id);
    if (item) { item.qty += 1; renderCart(); }
}

function decreaseQty(id) {//fungsi untuk mengurangi jumlah produk di keranjang belanja
    const item = cart.find(item => item.id === id);
    if (item) {
        item.qty -= 1;
        if (item.qty <= 0) {
            cart = cart.filter(i => i.id !== id);
        }
        renderCart();
    }
}

function renderCart() {//fungsi untuk menampilkan isi keranjang belanja di modal
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
                    <button class="btn btn-sm btn-outline-danger qty-btn" onclick="decreaseQty(${item.id})"><i class="bi bi-dash"></i></button>
                    <span class="qty-text">${item.qty}</span>
                    <button class="btn btn-sm btn-outline-primary qty-btn" onclick="increaseQty(${item.id})"><i class="bi bi-plus"></i></button>
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

function calculateChange() {//fungsi untuk menghitung kembalian saat pengguna memasukkan jumlah uang yang dibayarkan
    let total = 0;
    cart.forEach(item => total += (item.price * item.qty));
    let paid = parseInt(document.getElementById('paid-amount').value) || 0;
    let change = paid - total;
    document.getElementById('change-amount').innerText = change >= 0 ? formatRupiah(change) : "Rp 0";
}

async function checkout() {//fungsi untuk melakukan checkout dan mengirim data transaksi ke server
    let total = 0;
    let checkoutItems = cart.map(item => {
        let subtotal = item.price * item.qty;
        total += subtotal;
        return { id: item.id, qty: item.qty, subtotal: subtotal };
    });

    let paid = parseInt(document.getElementById('paid-amount').value) || 0;
    let change = paid - total;

    if (cart.length === 0) { alert("Keranjang masih kosong!"); return; }
    if (paid < total) { alert("Uang yang dibayar kurang!"); return; }

    const payload = { total_price: total, paid_amount: paid, change_amount: change, items: checkoutItems };

    try {//mengirim data transaksi ke server menggunakan fetch API
        const response = await fetch('http://127.0.0.1:5000/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.status === 201) {
            alert("Transaksi Berhasil!\nTotal: " + formatRupiah(total) + "\nKembalian: " + formatRupiah(change));
            cart = [];
            document.getElementById('paid-amount').value = '';
            renderCart();
            fetchProducts();
            window.location.href = `receipt.html?id=${result.transaction_id}`;
        } else {
            alert("Transaksi Gagal: " + result.error);
        }
    } catch (error) {
        console.error("Error saat checkout:", error);
        alert("Terjadi kesalahan koneksi ke server.");
    }
}

fetchProducts();
renderCart();