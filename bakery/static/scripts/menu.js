var cart = [];

// ── Grab the CSRF token ───────────────────────────────────────────────────────
// Primary: window.CSRF_TOKEN injected by the Django template
// Fallback: read Django's csrftoken cookie (Django docs recommended approach)
function getCsrfToken() {
    if (window.CSRF_TOKEN) return window.CSRF_TOKEN;
    var name = 'csrftoken';
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var c = cookies[i].trim();
        if (c.indexOf(name + '=') === 0) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return '';
}

<<<<<<< HEAD
// ── Show a brief toast notification ───────────────────────────────────────────
function showToast(message, success) {
    var existing = document.getElementById('cart-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.id = 'cart-toast';
    toast.textContent = message;
    toast.style.cssText = [
        'position:fixed', 'bottom:24px', 'right:24px',
        'background:' + (success ? '#2e7d32' : '#c62828'),
        'color:#fff', 'padding:12px 20px', 'border-radius:8px',
        'font-size:14px', 'z-index:9999', 'box-shadow:0 4px 12px rgba(0,0,0,.25)',
        'transition:opacity .4s ease', 'opacity:1'
    ].join(';');
    document.body.appendChild(toast);

    setTimeout(function () { toast.style.opacity = '0'; }, 2500);
    setTimeout(function () { toast.remove(); }, 3000);
}

// ── Add item to cart ──────────────────────────────────────────────────────────
function addToCart(name, price, quantity, event) {
    if (event) event.stopPropagation();   // prevent card onclick from firing

    if (!window.USER_AUTHENTICATED) {
        window.location.href = '/login.php?next=/menu.php';
        return;
    }

    var qty = parseInt(quantity) || 1;
    var item = { name: name, price: price, quantity: qty };

    fetch('add-to-cart.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(item)
    })
    .then(function (response) {
        if (!response.ok) {
            return response.json().then(function (d) {
                throw new Error(d.message || 'Server error ' + response.status);
            });
        }
        return response.json();
    })
    .then(function (data) {
        showToast('✓ ' + name + ' added to cart!', true);
        loadCart();
    })
    .catch(function (error) {
        console.error('Error adding item to cart:', error);
        showToast('Failed to add item: ' + error.message, false);
    });
=======
// Function to show notification popup
function showNotification(message, type = 'success') {
    // Remove existing notification if any
    const existingNotification = document.querySelector('.notification-popup');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification-popup';
    notification.textContent = message;

    // Set color based on type
    if (type === 'success') {
        notification.style.backgroundColor = '#28a745';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#dc3545';
    } else {
        notification.style.backgroundColor = '#17a2b8';
    }

    // Add to body
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Function to add item to cart
function addToCart(name, price, quantity) {
    // Check if user is logged in
    if (!window.isUserLoggedIn) {
        window.location.href = '/login.php';
        return;
    }
    
    const item = { name: name, price: price, quantity: quantity };

    fetch('add-to-cart.php', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(item)
    })
    .then(response => {
        if (!response.ok) {
            // Check if redirected to login (HTML response instead of JSON)
            if (response.headers.get('content-type') && response.headers.get('content-type').includes('text/html')) {
                window.location.href = '/login.php';
                return;
            }
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data) {
            showNotification(data.message, 'success');
            loadCart();
        }
    })
    .catch(error => {
        console.error('Error adding item to cart:', error);
        showNotification('Error adding item to cart', 'error');
    });
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
>>>>>>> origin/chelle_django_ver
}

// ── Remove / decrement item from cart ─────────────────────────────────────────
function removeFromCart(index) {
    fetch('remove-from-cart.php', {
        method: 'POST',
<<<<<<< HEAD
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ index: index })
    })
    .then(function (response) { return response.json(); })
    .then(function (data) {
        loadCart();
    })
    .catch(function (error) {
        console.error('Error removing item from cart:', error);
        showToast('Failed to remove item.', false);
=======
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ index: index, action: 'remove' })
    })
    .then(response => response.json())
    .then(data => {
        showNotification(data.message, 'success');
        loadCart();
    })
    .catch(error => {
        console.error('Error removing item from cart:', error);
        showNotification('Error removing item from cart', 'error');
    });
}

// Function to increment cart item quantity
function incrementCartItem(index) {
    fetch('update-cart-quantity.php', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ index: index, action: 'increment' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCart();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error incrementing item quantity:', error);
        showNotification('Error incrementing item quantity', 'error');
    });
}

// Function to decrement cart item quantity
function decrementCartItem(index) {
    fetch('update-cart-quantity.php', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ index: index, action: 'decrement' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCart();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error decrementing item quantity:', error);
        showNotification('Error decrementing item quantity', 'error');
>>>>>>> origin/chelle_django_ver
    });
}

// ── Load cart from server ─────────────────────────────────────────────────────
function loadCart() {
    fetch('get-cart.php')
<<<<<<< HEAD
        .then(function (response) { return response.json(); })
        .then(function (data) {
            cart = data.items || [];
            updateCart();
=======
        .then(response => {
            if (!response.ok) {
                // Check if redirected to login (HTML response instead of JSON)
                if (response.headers.get('content-type') && response.headers.get('content-type').includes('text/html')) {
                    window.location.href = '/login.php';
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                cart = data.items;
                updateCart();
            }
>>>>>>> origin/chelle_django_ver
        })
        .catch(function (error) {
            console.error('Error loading cart:', error);
        });
}

// ── Render cart table ─────────────────────────────────────────────────────────
function updateCart() {
<<<<<<< HEAD
    var cartItemsElement = document.getElementById('cartItems');
    var cartTotalElement = document.getElementById('cartTotal');
    if (!cartItemsElement || !cartTotalElement) return;
=======
    const cartItemsElement = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');
    
    if (!cartItemsElement || !cartTotalElement) {
        return; // Elements don't exist (user not logged in)
    }
    
    let total = 0;
>>>>>>> origin/chelle_django_ver

    var total = 0;
    cartItemsElement.innerHTML = '';

<<<<<<< HEAD
    cart.forEach(function (item, index) {
        var subtotal = (item.subtotal != null) ? item.subtotal : (item.item_price * item.quantity);
        var row = document.createElement('tr');
        row.innerHTML =
            '<td>' + item.item_name + '</td>' +
            '<td>₱ ' + parseFloat(item.item_price).toFixed(2) + '</td>' +
            '<td>' + item.quantity + '</td>' +
            '<td><button onclick="removeFromCart(' + index + ')" class="btn btn-sm btn-danger" style="padding:1px 6px;">X</button></td>';
        cartItemsElement.appendChild(row);
        total += subtotal;
=======
    cart.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.item_name}</td>
            <td>₱ ${item.item_price.toFixed(2)}</td>
            <td>
                <button onclick="decrementCartItem(${index})" style="padding: 2px 8px;">-</button>
                <span>${item.quantity}</span>
                <button onclick="incrementCartItem(${index})" style="padding: 2px 8px;">+</button>
            </td>
            <td><button onclick="removeFromCart(${index})" style="background-color: #dc3545; color: white; border: none; padding: 2px 8px;">X</button></td>
        `;
        cartItemsElement.appendChild(row);
        total += item.item_price * item.quantity;
>>>>>>> origin/chelle_django_ver
    });

    cartTotalElement.textContent = '₱ ' + total.toFixed(2);
}

<<<<<<< HEAD
// ── Wire up UI once DOM is ready ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Only initialise cart for logged-in users
    if (!window.USER_AUTHENTICATED) return;

    // Load cart items on page load
    loadCart();

    // Open cart sidebar
    var openCartBtn = document.getElementById('openCart');
    var cartEl = document.querySelector('.cart');
    if (openCartBtn && cartEl) {
        openCartBtn.addEventListener('click', function (e) {
            e.preventDefault();
            cartEl.classList.add('open');
        });
    }

    // Close cart sidebar
    var closeCartBtn = document.getElementById('closeCart');
    if (closeCartBtn && cartEl) {
        closeCartBtn.addEventListener('click', function () {
            cartEl.classList.remove('open');
        });
    }

    // Checkout button — server decides if cart has items
    var checkoutBtn = document.getElementById('checkOut');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function () {
            var btn = this;
            btn.disabled = true;
            btn.textContent = 'Processing...';

            fetch('checkout.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Server error ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    window.location.href = 'delivery.php';
                } else {
                    alert(data.message || 'Checkout failed. Please try again.');
                    btn.disabled = false;
                    btn.textContent = 'Checkout';
                }
            })
            .catch(function (err) {
                console.error('Checkout error:', err);
                alert('Checkout failed: ' + err.message + '. Please try again.');
                btn.disabled = false;
                btn.textContent = 'Checkout';
            });
        });
    }
});
=======
// Event listeners for opening and closing cart
if (openCartBtn) {
    openCartBtn.addEventListener('click', () => {
        cartElement.classList.add('open');
    });
}

if (closeCartBtn) {
    closeCartBtn.addEventListener('click', () => {
        cartElement.classList.remove('open');
    });
}

// Checkout function
if (checkOut) {
    checkOut.addEventListener('click', () => {
        if (cart.length === 0) {
            showNotification('You need to add an item first!', 'error');
        } else {
            fetch('checkout.php', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ cart: cart, totalPrice: totalPrice })
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
                
            })
            .then(data => {
                if (data.success) window.location.href = 'pickup.php';
                else showNotification('Checkout failed: ' + data.message, 'error');
            })
            .catch(error => {
                console.error('Error during checkout:', error);
                showNotification('Error during checkout', 'error');
            });
        }
    });
}
>>>>>>> origin/chelle_django_ver
