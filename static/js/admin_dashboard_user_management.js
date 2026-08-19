// Admin Dashboard User Management JavaScript

function initializeUserManagement() {
    // User Management Actions
    const editUserBtns = document.querySelectorAll('.edit-user-btn');
    editUserBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            const userName = this.getAttribute('data-user-name');
            showUserEditModal(userId, userName);
        });
    });

    const toggleUserStatusBtns = document.querySelectorAll('.toggle-user-status-btn');
    toggleUserStatusBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            const userName = this.getAttribute('data-user-name');
            const isActive = this.getAttribute('data-is-active') === 'true';
            toggleUserStatus(userId, userName, isActive);
        });
    });

    const deleteUserBtns = document.querySelectorAll('.delete-user-btn');
    deleteUserBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            const userName = this.getAttribute('data-user-name');
            deleteUser(userId, userName);
        });
    });

    // Add event listeners for checkboxes
    document.addEventListener('change', function (e) {
        if (e.target.classList.contains('user-checkbox')) {
            updateBulkActions();
        }
    });

    // Add event listener for search input
    document.addEventListener('input', function (e) {
        if (e.target.id === 'userSearchInput') {
            searchUsers();
        }
    });

    // Add event listeners for filter dropdowns
    document.addEventListener('change', function (e) {
        if (e.target.id === 'userRoleFilter' || e.target.id === 'userStatusFilter') {
            filterUsers();
        }
    });
}

// User Management Functions
function showUserEditModal(userId, userName) {
    // Fetch user data and show edit modal
    fetch(`/admin-api/users/${userId}/edit/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showUserEditForm(data.user);
            } else {
                showNotification(data.error || 'Failed to load user data', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to load user data', 'error');
        });
}

function showUserEditForm(user) {
    const modalHtml = `
        <div class="modal fade" id="userEditModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit User: ${user.username}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="userEditForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control" id="editUsername" value="${user.username}">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" id="editEmail" value="${user.email}">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">First Name</label>
                                    <input type="text" class="form-control" id="editFirstName" value="${user.first_name || ''}">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Last Name</label>
                                    <input type="text" class="form-control" id="editLastName" value="${user.last_name || ''}">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Role</label>
                                    <select class="form-select" id="editRole">
                                        <option value="customer" ${user.role === 'customer' ? 'selected' : ''}>Customer</option>
                                        <option value="owner" ${user.role === 'owner' ? 'selected' : ''}>Owner</option>
                                        <option value="delivery" ${user.role === 'delivery' ? 'selected' : ''}>Delivery</option>
                                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <div class="form-check mt-4">
                                        <input class="form-check-input" type="checkbox" id="editIsActive" ${user.is_active ? 'checked' : ''}>
                                        <label class="form-check-label">Active Account</label>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="saveUserEdit(${user.id})">Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('userEditModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('userEditModal'));
    modal.show();
}

function saveUserEdit(userId) {
    const formData = {
        username: document.getElementById('editUsername').value,
        email: document.getElementById('editEmail').value,
        first_name: document.getElementById('editFirstName').value,
        last_name: document.getElementById('editLastName').value,
        role: document.getElementById('editRole').value,
        is_active: document.getElementById('editIsActive').checked
    };

    fetch(`/admin-api/users/${userId}/edit/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('userEditModal'));
                modal.hide();
                // Refresh the page to show updated data
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification(data.error || 'Failed to update user', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to update user', 'error');
        });
}

function toggleUserStatus(userId, userName, isActive) {
    const action = isActive ? 'deactivate' : 'activate';
    if (confirm(`Are you sure you want to ${action} user "${userName}"?`)) {
        // AJAX call to toggle user status
        fetch(`/admin-api/users/${userId}/toggle-status/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ is_active: !isActive })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(`User "${userName}" ${action}d successfully!`, 'success');
                    location.reload(); // Refresh to show updated status
                } else {
                    showNotification(`Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showNotification('Error updating user status', 'error');
            });
    }
}

function deleteUser(userId, userName) {
    if (confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone!`)) {
        // AJAX call to delete user
        fetch(`/admin-api/users/${userId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(`User "${userName}" deleted successfully!`, 'success');
                    location.reload(); // Refresh to remove deleted user
                } else {
                    showNotification(`Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showNotification('Error deleting user', 'error');
            });
    }
}

// Enhanced User Management Functions
function showAddUserModal() {
    showNotification('Add User functionality coming soon!', 'info');
}

function exportUsers() {
    showNotification('Export Users functionality coming soon!', 'info');
}

function searchUsers() {
    const searchTerm = document.getElementById('userSearchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#usersTable tbody tr');

    rows.forEach(row => {
        const username = row.querySelector('h6').textContent.toLowerCase();
        const email = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        const fullName = row.querySelector('small').textContent.toLowerCase();

        if (username.includes(searchTerm) || email.includes(searchTerm) || fullName.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAllUsers');
    const checkboxes = document.querySelectorAll('.user-checkbox');

    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });

    updateBulkActions();
}

function updateBulkActions() {
    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    const bulkActions = document.getElementById('bulkActions');
    const selectedCount = document.getElementById('selectedCount');

    if (checkboxes.length > 0) {
        bulkActions.style.display = 'block';
        selectedCount.textContent = checkboxes.length;
    } else {
        bulkActions.style.display = 'none';
    }
}

function bulkToggleStatus() {
    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    if (checkboxes.length === 0) {
        showNotification('Please select users first', 'warning');
        return;
    }

    const userIds = Array.from(checkboxes).map(cb => cb.value);
    const action = confirm(`Toggle status for ${userIds.length} selected users?`);

    if (action) {
        showNotification(`Bulk toggle status for ${userIds.length} users - Coming soon!`, 'info');
    }
}

function bulkDeleteUsers() {
    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    if (checkboxes.length === 0) {
        showNotification('Please select users first', 'warning');
        return;
    }

    const userIds = Array.from(checkboxes).map(cb => cb.value);
    const action = confirm(`Delete ${userIds.length} selected users? This action cannot be undone!`);

    if (action) {
        showNotification(`Bulk delete for ${userIds.length} users - Coming soon!`, 'info');
    }
}

function filterUsers() {
    const roleFilter = document.getElementById('userRoleFilter').value;
    const statusFilter = document.getElementById('userStatusFilter').value;
    const rows = document.querySelectorAll('#usersTable tbody tr');

    rows.forEach(row => {
        const userRole = row.getAttribute('data-role');
        const userStatus = row.getAttribute('data-status');

        let showRow = true;

        if (roleFilter && userRole !== roleFilter) {
            showRow = false;
        }

        if (statusFilter && userStatus !== statusFilter) {
            showRow = false;
        }

        row.style.display = showRow ? '' : 'none';
    });
}
