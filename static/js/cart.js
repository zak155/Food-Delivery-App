// Cart functionality with AJAX
class CartManager {
    constructor() {
        this.csrfToken = this.getCSRFToken();
        this.updateTimeouts = {}; // For debouncing quantity updates
        this.init();
    }

    init() {
        // Initialize cart counter on page load
        this.updateCartCounter();
        // Initialize all row totals on page load
        this.updateAllRowTotals();
        // Initialize cart total on page load
        this.updateCartTotal();

        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault();
                const mealId = e.target.dataset.mealId;

                // Check if we're on product detail page and get quantity from input
                const quantityInput = document.getElementById('quantity');
                let quantity = 1;

                if (quantityInput) {
                    // Product detail page - get quantity from input field
                    quantity = parseInt(quantityInput.value) || 1;
                } else {
                    // Meal list page - get quantity from button data attribute
                    quantity = parseInt(e.target.dataset.quantity || 1);
                }

                // Extract meal information from the clicked element's context
                const mealData = this.extractMealData(e.target, mealId, quantity);
                this.addToCart(mealId, quantity, mealData);
            }
        });

        // Update quantity buttons
        document.addEventListener('click', (e) => {
            const updateBtn = e.target.closest('.update-quantity-btn');
            if (updateBtn) {
                e.preventDefault();
                const itemId = updateBtn.dataset.itemId;
                const action = updateBtn.dataset.action;
                this.updateQuantity(itemId, action);
            }
        });

        // Remove item buttons
        document.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-item-btn');
            if (removeBtn) {
                e.preventDefault();
                const itemId = removeBtn.dataset.itemId;
                this.removeItem(itemId);
            }
        });

        // Quantity input changes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                const itemId = e.target.dataset.itemId;
                const quantity = parseInt(e.target.value);
                this.debouncedUpdateQuantity(itemId, quantity);
            }
        });

        // Quantity input arrow clicks (up/down buttons)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                const itemId = e.target.dataset.itemId;
                const quantity = parseInt(e.target.value);
                this.debouncedUpdateQuantity(itemId, quantity);
            }
        });

        // Quantity input keyup events (for manual typing)
        document.addEventListener('keyup', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                const itemId = e.target.dataset.itemId;
                const quantity = parseInt(e.target.value);
                if (!isNaN(quantity) && quantity > 0 && quantity <= 25) {
                    this.debouncedUpdateQuantity(itemId, quantity);
                } else if (quantity > 25) {
                    e.target.value = 25;
                    this.debouncedUpdateQuantity(itemId, 25);
                }
            }
        });
    }

    extractMealData(buttonElement, mealId, quantity) {
        // Try to find meal data from the button's parent card/container
        const card = buttonElement.closest('.card, .meal-card, .product-card');
        let mealName = 'Product';
        let mealPrice = 0;

        if (card) {
            // Try to find meal name from various possible selectors
            const nameElement = card.querySelector('.card-title, .meal-name, .product-name, h5, h4, h3');
            if (nameElement) {
                mealName = nameElement.textContent.trim();
            }

            // Try to find meal price from various possible selectors
            const priceElement = card.querySelector('.price, .meal-price, .product-price, [class*="price"]');
            if (priceElement) {
                const priceText = priceElement.textContent.trim();
                // Extract price from text like "$5.99" or "5.99"
                const priceMatch = priceText.match(/\$?(\d+\.?\d*)/);
                if (priceMatch) {
                    mealPrice = parseFloat(priceMatch[1]);
                }
            }
        }

        // Fallback: try to get data from button's data attributes
        if (buttonElement.dataset.mealName) {
            mealName = buttonElement.dataset.mealName;
        }
        if (buttonElement.dataset.mealPrice) {
            mealPrice = parseFloat(buttonElement.dataset.mealPrice);
        }

        return {
            id: mealId,
            name: mealName,
            price: mealPrice,
            quantity: quantity
        };
    }

    addToCart(mealId, quantity = 1, mealData = null) {
        const formData = new FormData();
        formData.append('quantity', quantity);
        formData.append('csrfmiddlewaretoken', this.csrfToken);

        fetch(`/meals/add-to-cart/${mealId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
            .then(response => {
                // Check if user is not authenticated (redirect to login)
                if (response.status === 302 || response.redirected) {
                    window.location.href = '/users/login/';
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.success) {
                    // Reset quantity to 1 on product detail page
                    this.resetQuantityOnProductPage();
                    // Show popup with actual quantity added
                    this.showAddToCartPopup(`${quantity} item${quantity > 1 ? 's' : ''} added to cart!`, mealData);
                    this.updateCartCounter();
                    this.updateCartTotal();
                } else if (data && data.error) {
                    this.showError(data.error);
                } else {
                    // If no data returned, user might not be authenticated
                    this.showError('Please log in to add items to cart');
                }
            })
            .catch(error => {
                console.error('Add to cart error:', error);
                this.showError('Please log in to add items to cart');
            });
    }

    updateQuantity(itemId, action) {
        const quantityInput = document.querySelector(`input[data-item-id="${itemId}"]`);

        if (!quantityInput) {
            console.error('Quantity input not found for item:', itemId);
            return;
        }

        let currentQuantity = parseInt(quantityInput.value);

        if (action === 'increase' && currentQuantity < 25) {
            currentQuantity += 1;
        } else if (action === 'decrease' && currentQuantity > 1) {
            currentQuantity -= 1;
        }

        this.updateQuantityDirect(itemId, currentQuantity);
    }

    refreshCartPage() {
        // If we're on the cart page, refresh it to show updated totals
        if (window.location.pathname === '/orders/cart/') {
            window.location.reload();
        }
    }

    debouncedUpdateQuantity(itemId, quantity) {
        // Clear existing timeout for this item
        if (this.updateTimeouts[itemId]) {
            clearTimeout(this.updateTimeouts[itemId]);
        }

        // Set new timeout
        this.updateTimeouts[itemId] = setTimeout(() => {
            this.updateQuantityDirect(itemId, quantity);
            delete this.updateTimeouts[itemId];
        }, 300); // Reduced to 300ms delay
    }

    updateQuantityDirect(itemId, quantity) {
        if (quantity < 1) {
            this.removeItem(itemId);
            return;
        }

        const formData = new FormData();
        formData.append('quantity', quantity);
        formData.append('csrfmiddlewaretoken', this.csrfToken);

        fetch(`/orders/update-cart-item/${itemId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the quantity input value in the DOM
                    const itemRow = this.findItemRow(itemId);
                    if (itemRow) {
                        const quantityInput = itemRow.querySelector('.quantity-input');
                        if (quantityInput) {
                            quantityInput.value = quantity;
                        }
                    }

                    // First update the specific row's total
                    this.updateRowTotal(itemId);
                    // Then update the overall cart total by summing all row totals
                    this.updateCartTotal();
                    // Update cart counter
                    this.updateCartCounter();
                } else {
                    this.showError(data.error || 'Failed to update quantity');
                }
            })
            .catch(error => {
                console.error('Update quantity error:', error);
                this.showError('Failed to update quantity');
            });
    }

    removeItem(itemId) {
        if (!confirm('Are you sure you want to remove this item from your cart?')) {
            return;
        }

        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.csrfToken);

        fetch(`/orders/remove-cart-item/${itemId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.removeItemFromDOM(itemId);
                    this.updateCartTotal();
                    this.updateCartCounter();
                } else {
                    this.showError(data.error || 'Failed to remove item');
                }
            })
            .catch(error => {
                console.error('Remove item error:', error);
                this.showError('Failed to remove item');
            });
    }

    updateItemTotal(itemId, totalPrice) {
        // Find the row containing the item with this ID
        const itemRow = this.findItemRow(itemId);
        if (itemRow) {
            const totalElement = itemRow.querySelector('.item-total');
            if (totalElement) {
                totalElement.textContent = `$${totalPrice.toFixed(2)}`;
            } else {
                console.warn('Could not find .item-total element in row for item ID:', itemId);
            }
        } else {
            console.warn('Could not find item row for item ID:', itemId);
        }
    }

    updateRowTotal(itemId) {
        // Calculate and update the total for a specific row based on price * quantity
        const itemRow = this.findItemRow(itemId);
        if (itemRow) {
            // Find the price in the second column (td with class "py-4 px-4 text-center")
            const priceElement = itemRow.querySelector('td:nth-child(2) span');
            // Find the quantity input in the third column
            const quantityInput = itemRow.querySelector('.quantity-input');
            // Find the total in the fourth column (td with class "py-4 px-4 text-end")
            const totalElement = itemRow.querySelector('.item-total');

            if (priceElement && quantityInput && totalElement) {
                const price = parseFloat(priceElement.textContent.replace('$', ''));
                const quantity = parseInt(quantityInput.value) || 1;
                const itemTotal = price * quantity;

                // Update only this specific row's total
                totalElement.textContent = `$${itemTotal.toFixed(2)}`;
            } else {
                console.warn('Could not find required elements for row total calculation:', {
                    priceElement: priceElement,
                    quantityInput: quantityInput,
                    totalElement: totalElement
                });
            }
        } else {
            console.warn('Could not find item row for item ID:', itemId);
        }
    }

    updateAllRowTotals() {
        // Update all row totals on page load
        const cartItems = document.querySelectorAll('.cart-item');

        cartItems.forEach((item, index) => {
            // Get the item ID from any element with data-item-id
            const itemIdElement = item.querySelector('[data-item-id]');
            if (itemIdElement) {
                const itemId = itemIdElement.dataset.itemId;
                this.updateRowTotal(itemId);
            } else {
                console.warn(`Could not find item ID for cart item ${index + 1}`);
            }
        });
    }

    findItemRow(itemId) {
        // Find the row containing the item with this ID
        const cartItems = document.querySelectorAll('.cart-item');
        for (let item of cartItems) {
            // Check if this row contains an element with the specific item ID
            const hasItemId = item.querySelector(`[data-item-id="${itemId}"]`);
            if (hasItemId) {
                return item;
            }
        }
        console.warn('Could not find item row for item ID:', itemId);
        return null;
    }

    updateCartTotal() {
        // Update overall cart total by summing all individual row totals
        const cartItems = document.querySelectorAll('.cart-item');
        let total = 0;

        cartItems.forEach((item, index) => {
            // Get the individual row total from the .item-total span
            const totalElement = item.querySelector('.item-total');

            if (totalElement) {
                const itemTotal = parseFloat(totalElement.textContent.replace('$', ''));
                total += itemTotal;
            }
            // Note: .item-total elements may not exist on all pages
        });

        // Update the order total in the summary section (id="orderTotal")
        const orderTotalElement = document.querySelector('#orderTotal');
        if (orderTotalElement) {
            orderTotalElement.textContent = `$${total.toFixed(2)}`;
        }
        // Note: #orderTotal element may not exist on all pages (e.g., admin dashboard)

        // Update subtotal elements (class="subtotal")
        const subtotalElements = document.querySelectorAll('.subtotal');
        subtotalElements.forEach(element => {
            element.textContent = `$${total.toFixed(2)}`;
        });
    }

    updateCartCounter() {
        // Update cart counter in navigation - try multiple selectors
        let counterElement = document.querySelector('#cartCount') ||
            document.querySelector('.cart-counter') ||
            document.querySelector('[id*="cart"]') ||
            document.querySelector('[class*="cart"]');

        if (counterElement) {
            fetch('/orders/cart-count/')
                .then(response => response.json())
                .then(data => {
                    if (data.count > 0) {
                        counterElement.textContent = `Cart (${data.count})`;
                        counterElement.style.display = 'inline';
                    } else {
                        counterElement.textContent = 'Cart';
                        counterElement.style.display = 'inline';
                    }
                })
                .catch(error => {
                    console.error('Error updating cart counter:', error);
                });
        } else {
            console.warn('Cart counter element not found. Available elements:', {
                cartCount: document.querySelector('#cartCount'),
                cartCounter: document.querySelector('.cart-counter'),
                allCartElements: document.querySelectorAll('[id*="cart"], [class*="cart"]')
            });
        }
    }

    removeItemFromDOM(itemId) {
        // Find the row containing the item with this ID
        const itemRow = this.findItemRow(itemId);
        if (itemRow) {
            itemRow.remove();
        } else {
            console.warn('Could not find item row for item ID:', itemId);
        }

        // Check if cart is empty
        const cartItems = document.querySelectorAll('.cart-item');

        if (cartItems.length === 0) {
            this.showEmptyCart();
        }
    }

    showEmptyCart() {
        const cartContainer = document.querySelector('#cartItems');
        if (cartContainer) {
            cartContainer.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-5">
                        <div class="text-muted">
                            <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                            <h5>Your cart is empty</h5>
                            <p>Add some delicious meals to get started!</p>
                            <a href="/meals/" class="btn btn-primary">Browse Meals</a>
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    showAddToCartPopup(message, mealData = null) {
        // Create or update popup
        let popup = document.getElementById('addToCartPopup');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'addToCartPopup';
            popup.className = 'add-to-cart-popup position-fixed';
            popup.style.cssText = 'display: none; z-index: 9999;';
            document.body.appendChild(popup);
        }

        // Create popup content based on whether we have meal data
        let popupContent;
        if (mealData && mealData.name && mealData.price) {
            const totalPrice = (mealData.price * mealData.quantity).toFixed(2);
            popupContent = `
                <div class="popup-content bg-body rounded-3 shadow-lg p-3">
                    <div class="popup-arrow-up"></div>
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        <span class="fw-bold">Item Added To Cart</span>
                    </div>
                    <p class="mb-1 fw-bold text-dark" id="popupItemName">${mealData.name}</p>
                    <p class="mb-3 text-muted small" id="popupItemDetails">Qty: ${mealData.quantity} | $${totalPrice}</p>
                    <div class="d-flex gap-2 flex-wrap">
                        <button class="btn btn-outline-primary btn-sm" onclick="window.location.href='/orders/cart/'">View Cart</button>
                        <button class="btn btn-primary btn-sm" onclick="window.location.href='/orders/checkout/'">Checkout</button>
                    </div>
                </div>
            `;
        } else {
            // Fallback to simple message
            popupContent = `
                <div class="popup-content bg-body rounded-3 shadow-lg p-3">
                    <div class="popup-arrow-up"></div>
                    <div class="d-flex align-items-center">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        <span class="fw-bold">${message}</span>
                    </div>
                </div>
            `;
        }

        popup.innerHTML = popupContent;

        // Position popup under cart icon
        this.positionPopupUnderCart(popup);

        // Show popup
        popup.style.display = 'block';

        // Handle window resize and scroll to keep popup positioned correctly
        const resizeHandler = () => {
            if (popup.style.display !== 'none') {
                this.positionPopupUnderCart(popup);
            }
        };

        const scrollHandler = () => {
            if (popup.style.display !== 'none') {
                this.positionPopupUnderCart(popup);
            }
        };

        window.addEventListener('resize', resizeHandler);
        window.addEventListener('scroll', scrollHandler);

        // Hide after 3 seconds
        setTimeout(() => {
            popup.style.display = 'none';
            window.removeEventListener('resize', resizeHandler);
            window.removeEventListener('scroll', scrollHandler);
        }, 3000);
    }

    positionPopupUnderCart(popup) {
        const cartLink = document.getElementById('cartLink');
        const navbar = document.getElementById('mainNavbar');

        if (cartLink) {
            const rect = cartLink.getBoundingClientRect();
            const popupWidth = 300; // Approximate popup width
            const popupHeight = 60; // Approximate popup height

            // Check if navbar is hidden
            let navbarOffset = 0;
            if (navbar) {
                const navbarRect = navbar.getBoundingClientRect();
                const navbarHeight = navbar.offsetHeight;

                // If navbar is hidden (translateY is negative), adjust offset
                if (navbarRect.top < 0) {
                    // Navbar is hidden, add navbar height to offset
                    navbarOffset = navbarHeight;
                }
            }

            // Position popup under the cart icon with navbar offset
            const top = rect.bottom + 10 + navbarOffset; // 10px below cart icon + navbar offset
            const left = rect.left + (rect.width / 2) - (popupWidth / 2); // Center under cart icon

            // Ensure popup doesn't go off screen
            const viewportWidth = window.innerWidth;
            const finalLeft = Math.max(10, Math.min(left, viewportWidth - popupWidth - 10));

            popup.style.top = `${top}px`;
            popup.style.left = `${finalLeft}px`;

        } else {
            // Fallback to top-right if cart link not found
            popup.style.top = '20px';
            popup.style.right = '20px';
        }
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger position-fixed';
        errorDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        errorDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-circle me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(errorDiv);

        // Remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }

    resetQuantityOnProductPage() {
        // Reset quantity to 1 on product detail page
        const quantityInput = document.getElementById('quantity');
        if (quantityInput) {
            quantityInput.value = 1;
            // Trigger the updateTotalPrice function if it exists
            if (typeof updateTotalPrice === 'function') {
                updateTotalPrice();
            }
        }
    }

    getCSRFToken() {
        // First try to get from cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }

        // Fallback to meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        console.warn('CSRF token not found in cookies or meta tag');
        return '';
    }
}

// Initialize cart manager when DOM is loaded (prevent duplicate initialization)
document.addEventListener('DOMContentLoaded', function () {
    if (!window.cartManagerInstance) {
        window.cartManagerInstance = new CartManager();
    }
});