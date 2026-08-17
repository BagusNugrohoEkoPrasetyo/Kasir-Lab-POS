const API_URL = 'http://127.0.0.1:5000/api/products';
let productModal;

document.addEventListener('DOMContentLoaded', () => {
    productModal = new bootstrap.Modal(document.getElementById('productModal'));
    fetchProducts();
});

function formatRupiah(angka) {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka);
}

async function fetchProducts() {
    const response = await fetch(API_URL);
    const products = await response.json();
    const table = document.getElementById('product-table');
    table.innerHTML = '';
    
    products.forEach(product => {
        table.innerHTML += `
            <tr>
                <td><img src="${product.image}" width="50" height="50" style="object-fit: cover; border-radius: 8px;"></td>
                <td class="fw-bold">${product.name}</td>
                <td>${formatRupiah(product.price)}</td>
                <td>${product.stock}</td>
                <td class="text-end">
                    <button class="btn btn-warning btn-sm" onclick="openEditModal(${product.id}, '${product.name.replace(/'/g, "\\'")}', ${product.price}, ${product.stock}, '${product.image}')"><i class="bi bi-pencil"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteProduct(${product.id})"><i class="bi bi-trash"></i></button>
                </td>
            </tr>
        `;
    });
}

function previewImage() {
    const url = document.getElementById('product-image').value;
    const preview = document.getElementById('image-preview');
    if (url) { preview.src = url; } else { preview.src = "https://via.placeholder.com/100"; }
}

function openAddModal() {
    document.getElementById('modalTitle').innerText = "Tambah Produk Baru";
    document.getElementById('product-id').value = "";
    document.getElementById('product-name').value = "";
    document.getElementById('product-price').value = "";
    document.getElementById('product-stock').value = "";
    document.getElementById('product-image').value = "";
    document.getElementById('image-preview').src = "https://via.placeholder.com/100";
    productModal.show();
}

function openEditModal(id, name, price, stock, image) {
    document.getElementById('modalTitle').innerText = "Edit Produk";
    document.getElementById('product-id').value = id;
    document.getElementById('product-name').value = name;
    document.getElementById('product-price').value = price;
    document.getElementById('product-stock').value = stock;
    document.getElementById('product-image').value = image;
    document.getElementById('image-preview').src = image;
    productModal.show();
}

async function saveProduct() {
    const id = document.getElementById('product-id').value;
    const data = {
        name: document.getElementById('product-name').value,
        price: parseInt(document.getElementById('product-price').value),
        stock: parseInt(document.getElementById('product-stock').value),
        image: document.getElementById('product-image').value
    };

    let url, method;
    if (id) { url = `${API_URL}/${id}`; method = 'PUT'; } 
    else { url = API_URL; method = 'POST'; }

    const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        productModal.hide();
        fetchProducts(); 
        alert("Produk berhasil disimpan.");
    } else {
        alert("Gagal menyimpan produk.");
    }
}

async function deleteProduct(id) {
    if (confirm("Yakin mau menghapus produk ini?")) {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (response.ok) {
            fetchProducts();
            alert("Produk berhasil dihapus!");
        } else {
            alert("Gagal menghapus produk.");
        }
    }
}