// Admin Dashboard Restaurant Management JavaScript

function initializeRestaurantManagement() {
    // Restaurant management functions are called from the main admin dashboard
    // This file contains all restaurant-related functionality
}

// Restaurant Management Functions
function showRestaurantList() {
    // Create restaurant list content
    const content = `
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <h3 class="fw-bold mb-0">All Restaurants</h3>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-primary" onclick="refreshRestaurantList()">
                            <ion-icon name="refresh-outline" class="me-1"></ion-icon>
                            Refresh
                        </button>
                        <button class="btn btn-success" onclick="showAddRestaurantModal()">
                            <ion-icon name="add-outline" class="me-1"></ion-icon>
                            Add Restaurant
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-3">
            <div class="col-md-6">
                <div class="input-group">
                    <span class="input-group-text">
                        <ion-icon name="search-outline"></ion-icon>
                    </span>
                    <input type="text" class="form-control" id="restaurantSearch" placeholder="Search restaurants...">
                </div>
            </div>
            <div class="col-md-3">
                <select class="form-select" id="restaurantStatusFilter">
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                </select>
            </div>
            <div class="col-md-3">
                <select class="form-select" id="restaurantSortBy">
                    <option value="name">Sort by Name</option>
                    <option value="created_at">Sort by Date</option>
                    <option value="orders_count">Sort by Orders</option>
                </select>
            </div>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover" id="restaurantsTable">
                        <thead>
                            <tr>
                                <th>
                                    <input type="checkbox" id="selectAllRestaurants" onchange="toggleSelectAllRestaurants()">
                                </th>
                                <th>Restaurant</th>
                                <th>Owner</th>
                                <th>Location</th>
                                <th>Status</th>
                                <th>Orders</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="restaurantsTableBody">
                            <tr>
                                <td colspan="8" class="text-center py-4">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <p class="mt-2 text-muted">Loading restaurants...</p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="row mt-3" id="restaurantBulkActions" style="display: none;">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex align-items-center gap-3">
                            <span class="text-muted">Bulk Actions:</span>
                            <button class="btn btn-outline-warning btn-sm" onclick="bulkToggleRestaurantStatus()">
                                <ion-icon name="eye-outline" class="me-1"></ion-icon>
                                Toggle Status
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="bulkDeleteRestaurants()">
                                <ion-icon name="trash-outline" class="me-1"></ion-icon>
                                Delete Selected
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Replace the current content
    document.getElementById('mainContent').innerHTML = content;

    // Load restaurant data
    loadRestaurantList();

    // Add event listeners
    document.getElementById('restaurantSearch').addEventListener('input', filterRestaurants);
    document.getElementById('restaurantStatusFilter').addEventListener('change', filterRestaurants);
    document.getElementById('restaurantSortBy').addEventListener('change', filterRestaurants);
}

function showAddRestaurantModal() {
    // Create add restaurant modal
    const modal = `
        <div class="modal fade" id="addRestaurantModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <ion-icon name="add-outline" class="me-2"></ion-icon>
                            Add New Restaurant
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addRestaurantForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Restaurant Name</label>
                                    <input type="text" class="form-control" id="restaurantName" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Owner Email</label>
                                    <input type="email" class="form-control" id="ownerEmail" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Phone Number</label>
                                    <input type="tel" class="form-control" id="restaurantPhone">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Location</label>
                                    <input type="text" class="form-control" id="restaurantLocation" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">Description</label>
                                <textarea class="form-control" id="restaurantDescription" rows="3"></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Delivery Time</label>
                                    <input type="text" class="form-control" id="deliveryTime" placeholder="e.g., 30-45 minutes">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Opening Hours</label>
                                    <input type="text" class="form-control" id="openingHours" placeholder="e.g., Mon-Sun: 9:00 AM - 10:00 PM">
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="isActive" checked>
                                    <label class="form-check-label" for="isActive">
                                        Active Restaurant
                                    </label>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-success" onclick="saveNewRestaurant()">
                            <ion-icon name="save-outline" class="me-1"></ion-icon>
                            Create Restaurant
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('addRestaurantModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modal);

    // Show modal
    const modalElement = new bootstrap.Modal(document.getElementById('addRestaurantModal'));
    modalElement.show();
}

function showRestaurantAnalytics() {
    // Create restaurant analytics content
    const content = `
        <div class="row mb-4">
            <div class="col-12">
                <h3 class="fw-bold mb-0">Restaurant Analytics</h3>
                <p class="text-body-secondary mb-0">Performance metrics and insights for all restaurants</p>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="mb-0" id="totalRestaurantsCount">-</h4>
                                <p class="mb-0">Total Restaurants</p>
                            </div>
                            <ion-icon name="restaurant-outline" style="font-size: 2rem;"></ion-icon>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="mb-0" id="activeRestaurantsCount">-</h4>
                                <p class="mb-0">Active Restaurants</p>
                            </div>
                            <ion-icon name="checkmark-circle-outline" style="font-size: 2rem;"></ion-icon>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="mb-0" id="totalOrdersCount">-</h4>
                                <p class="mb-0">Total Orders</p>
                            </div>
                            <ion-icon name="receipt-outline" style="font-size: 2rem;"></ion-icon>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="mb-0" id="avgOrderValue">-</h4>
                                <p class="mb-0">Avg Order Value</p>
                            </div>
                            <ion-icon name="cash-outline" style="font-size: 2rem;"></ion-icon>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Top Performing Restaurants</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover" id="topRestaurantsTable">
                                <thead>
                                    <tr>
                                        <th>Restaurant</th>
                                        <th>Orders</th>
                                        <th>Revenue</th>
                                        <th>Rating</th>
                                    </tr>
                                </thead>
                                <tbody id="topRestaurantsTableBody">
                                    <tr>
                                        <td colspan="4" class="text-center py-4">
                                            <div class="spinner-border text-primary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Restaurant Status Distribution</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="restaurantStatusChart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Replace the current content
    document.getElementById('mainContent').innerHTML = content;

    // Load analytics data
    loadRestaurantAnalytics();
}

// Supporting functions for restaurant management
function loadRestaurantList() {
    fetch('/admin-api/restaurants/list/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayRestaurantList(data.restaurants);
            } else {
                showNotification('Error loading restaurants: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showNotification('Error loading restaurants', 'error');
        });
}

function displayRestaurantList(restaurants) {
    const tbody = document.getElementById('restaurantsTableBody');
    if (restaurants.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <ion-icon name="restaurant-outline" style="font-size: 3rem; color: #ccc;"></ion-icon>
                    <p class="mt-2 text-muted">No restaurants found</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = restaurants.map(restaurant => `
        <tr>
            <td>
                <input type="checkbox" class="restaurant-checkbox" value="${restaurant.id}">
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        ${restaurant.logo ?
            `<img src="${restaurant.logo}" alt="${restaurant.name}" class="rounded" style="width: 40px; height: 40px; object-fit: cover;">` :
            `<div class="bg-light rounded d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <ion-icon name="restaurant-outline" style="font-size: 1.5rem; color: #ccc;"></ion-icon>
                            </div>`
        }
                    </div>
                    <div>
                        <div class="fw-bold">${restaurant.name}</div>
                        <small class="text-muted">${restaurant.description || 'No description'}</small>
                    </div>
                </div>
            </td>
            <td>
                <div>
                    <div class="fw-medium">${restaurant.owner_name || 'N/A'}</div>
                    <small class="text-muted">${restaurant.owner_email || ''}</small>
                </div>
            </td>
            <td>
                <span class="text-truncate d-inline-block" style="max-width: 150px;" title="${restaurant.location}">
                    ${restaurant.location || 'N/A'}
                </span>
            </td>
            <td>
                <span class="badge ${restaurant.is_active ? 'bg-success' : 'bg-danger'}">
                    ${restaurant.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <span class="fw-bold">${restaurant.orders_count || 0}</span>
            </td>
            <td>
                <small class="text-muted">${new Date(restaurant.created_at).toLocaleDateString()}</small>
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary" onclick="showRestaurantEditModal(${restaurant.id}, '${restaurant.name}')" title="Edit">
                        <ion-icon name="create-outline"></ion-icon>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="toggleRestaurantStatus(${restaurant.id}, ${restaurant.is_active})" title="Toggle Status">
                        <ion-icon name="${restaurant.is_active ? 'eye-off-outline' : 'eye-outline'}"></ion-icon>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteRestaurant(${restaurant.id}, '${restaurant.name}')" title="Delete">
                        <ion-icon name="trash-outline"></ion-icon>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    // Add event listeners for checkboxes
    document.querySelectorAll('.restaurant-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateRestaurantBulkActions);
    });
}

function loadRestaurantAnalytics() {
    fetch('/admin-api/restaurants/analytics/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayRestaurantAnalytics(data.analytics);
            } else {
                showNotification('Error loading analytics: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showNotification('Error loading analytics', 'error');
        });
}

function displayRestaurantAnalytics(analytics) {
    // Update stats cards
    document.getElementById('totalRestaurantsCount').textContent = analytics.total_restaurants || 0;
    document.getElementById('activeRestaurantsCount').textContent = analytics.active_restaurants || 0;
    document.getElementById('totalOrdersCount').textContent = analytics.total_orders || 0;
    document.getElementById('avgOrderValue').textContent = analytics.avg_order_value ? '$' + analytics.avg_order_value.toFixed(2) : '$0.00';

    // Update top restaurants table
    const tbody = document.getElementById('topRestaurantsTableBody');
    if (analytics.top_restaurants && analytics.top_restaurants.length > 0) {
        tbody.innerHTML = analytics.top_restaurants.map(restaurant => `
            <tr>
                <td>
                    <div class="fw-bold">${restaurant.name}</div>
                    <small class="text-muted">${restaurant.location}</small>
                </td>
                <td><span class="badge bg-primary">${restaurant.orders_count}</span></td>
                <td><span class="fw-bold">$${restaurant.revenue || 0}</span></td>
                <td>
                    <div class="d-flex align-items-center">
                        <span class="me-1">${restaurant.rating || 0}</span>
                        <ion-icon name="star" style="color: #ffc107;"></ion-icon>
                    </div>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center py-4">
                    <p class="text-muted">No data available</p>
                </td>
            </tr>
        `;
    }
}

function saveNewRestaurant() {
    const formData = {
        name: document.getElementById('restaurantName').value,
        owner_email: document.getElementById('ownerEmail').value,
        phone: document.getElementById('restaurantPhone').value,
        location: document.getElementById('restaurantLocation').value,
        description: document.getElementById('restaurantDescription').value,
        delivery_time: document.getElementById('deliveryTime').value,
        opening_hours: document.getElementById('openingHours').value,
        is_active: document.getElementById('isActive').checked
    };

    fetch('/admin-api/restaurants/create/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Restaurant created successfully!', 'success');
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addRestaurantModal'));
                modal.hide();
                // Refresh restaurant list if it's open
                if (document.getElementById('restaurantsTableBody')) {
                    loadRestaurantList();
                }
            } else {
                showNotification('Error creating restaurant: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showNotification('Error creating restaurant', 'error');
        });
}

function refreshRestaurantList() {
    loadRestaurantList();
}

function filterRestaurants() {
    const searchTerm = document.getElementById('restaurantSearch').value.toLowerCase();
    const statusFilter = document.getElementById('restaurantStatusFilter').value;
    const sortBy = document.getElementById('restaurantSortBy').value;

    // This would typically make an API call with filters
    // For now, we'll just reload the data
    loadRestaurantList();
}

function toggleSelectAllRestaurants() {
    const selectAll = document.getElementById('selectAllRestaurants');
    const checkboxes = document.querySelectorAll('.restaurant-checkbox');

    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });

    updateRestaurantBulkActions();
}

function updateRestaurantBulkActions() {
    const checkedBoxes = document.querySelectorAll('.restaurant-checkbox:checked');
    const bulkActions = document.getElementById('restaurantBulkActions');

    if (checkedBoxes.length > 0) {
        bulkActions.style.display = 'block';
    } else {
        bulkActions.style.display = 'none';
    }
}

function bulkToggleRestaurantStatus() {
    const checkedBoxes = document.querySelectorAll('.restaurant-checkbox:checked');
    if (checkedBoxes.length === 0) {
        showNotification('Please select restaurants to toggle status', 'warning');
        return;
    }

    const restaurantIds = Array.from(checkedBoxes).map(cb => cb.value);

    fetch('/admin-api/restaurants/bulk-toggle-status/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ restaurant_ids: restaurantIds })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Status toggled for ${restaurantIds.length} restaurants`, 'success');
                loadRestaurantList();
            } else {
                showNotification('Error toggling status: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showNotification('Error toggling status', 'error');
        });
}

function bulkDeleteRestaurants() {
    const checkedBoxes = document.querySelectorAll('.restaurant-checkbox:checked');
    if (checkedBoxes.length === 0) {
        showNotification('Please select restaurants to delete', 'warning');
        return;
    }

    if (!confirm(`Are you sure you want to delete ${checkedBoxes.length} restaurants? This action cannot be undone.`)) {
        return;
    }

    const restaurantIds = Array.from(checkedBoxes).map(cb => cb.value);

    fetch('/admin-api/restaurants/bulk-delete/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ restaurant_ids: restaurantIds })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`${restaurantIds.length} restaurants deleted successfully`, 'success');
                loadRestaurantList();
            } else {
                showNotification('Error deleting restaurants: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showNotification('Error deleting restaurants', 'error');
        });
}
