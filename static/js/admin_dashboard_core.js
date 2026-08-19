// Admin Dashboard Core JavaScript
document.addEventListener('DOMContentLoaded', function () {
    console.log('🎛️ Admin Dashboard loaded');

    // Initialize core functionality
    initializeAdminDashboard();
    initializeEventListeners();
    initializeViewToggle();
    
    // Initialize platform settings if available
    if (typeof initializePlatformSettings === 'function') {
        initializePlatformSettings();
    }
});

// Also initialize when window loads (after all scripts are loaded)
window.addEventListener('load', function() {
    console.log('🎛️ All scripts loaded, re-initializing...');
    
    // Re-initialize event listeners in case they weren't set up properly
    initializeEventListeners();
});

function initializeAdminDashboard() {
    // User table row selection
    const tableRows = document.querySelectorAll('.user-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function () {
            // Remove active class from all rows
            tableRows.forEach(r => r.classList.remove('table-active'));
            // Add active class to clicked row
            this.classList.add('table-active');
        });
    });

    // Save button functionality
    const saveButtons = document.querySelectorAll('.btn-save');
    saveButtons.forEach(button => {
        button.addEventListener('click', function () {
            const section = this.closest('.settings-section');
            const sectionName = section.querySelector('h4').textContent;

            // Show success message
            showNotification(`${sectionName} saved successfully!`, 'success');

            // Add loading state
            this.innerHTML = '<ion-icon name="hourglass-outline" class="me-1"></ion-icon>Saving...';
            this.disabled = true;

            // Reset after 2 seconds
            setTimeout(() => {
                this.innerHTML = '<ion-icon name="save-outline" class="me-1"></ion-icon>Save';
                this.disabled = false;
            }, 2000);
        });
    });

    // Filter functionality
    const filterDropdowns = document.querySelectorAll('.filter-dropdown');
    filterDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function () {
            console.log('Filter changed:', this.value);
            // Implement filtering logic here
        });
    });
}

function initializeEventListeners() {
    // Dynamic Sidebar Navigation
    const adminNavLinks = document.querySelectorAll('.admin-nav-link');
    console.log('Found admin nav links:', adminNavLinks.length);
    
    adminNavLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Sidebar link clicked:', this.getAttribute('data-section'));

            // Remove active class from all links
            adminNavLinks.forEach(l => l.classList.remove('active'));
            // Add active class to clicked link
            this.classList.add('active');

            // Get section name
            const section = this.getAttribute('data-section');
            console.log('Calling showAdminSection with:', section);
            showAdminSection(section);
        });
    });

    // User Management Actions
    if (typeof initializeUserManagement === 'function') {
        initializeUserManagement();
    }

    // Order Management Actions
    if (typeof initializeOrderManagement === 'function') {
        initializeOrderManagement();
    }
}

function initializeViewToggle() {
    // Check if simple view is requested
    const urlParams = new URLSearchParams(window.location.search);
    const viewType = urlParams.get('view');

    if (viewType === 'simple') {
        toggleView('simple');
    } else {
        toggleView('comprehensive');
    }
}

// Core utility functions
function getCSRFToken() {
    // Try to get from meta tag first
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }

    // Fallback to cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }

    return null;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Section management function
function showAdminSection(sectionName) {
    console.log('showAdminSection called with:', sectionName);
    
    // Hide all sections
    const allSections = document.querySelectorAll('.admin-section');
    console.log('Found sections to hide:', allSections.length);
    
    allSections.forEach(section => {
        section.style.display = 'none';
    });

    // Show the requested section
    const targetSection = document.getElementById(`${sectionName}-section`);
    console.log('Target section found:', !!targetSection);
    
    if (targetSection) {
        targetSection.style.display = 'block';
        console.log('Showing existing section');
    } else {
        // Create section if it doesn't exist
        console.log('Creating new section');
        createAdminSection(sectionName);
    }

    // Update active navigation
    const navLinks = document.querySelectorAll('.admin-nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === sectionName) {
            link.classList.add('active');
        }
    });

    // If showing a section other than dashboard, switch to comprehensive view
    if (sectionName !== 'dashboard') {
        toggleView('comprehensive');
    }
}

function createAdminSection(sectionName) {
    const mainContent = document.getElementById('mainContent');
    let sectionContent = '';

    // Check if content generation functions are available
    const contentFunctions = {
        'dashboard': () => typeof getDashboardContent === 'function' ? getDashboardContent() : '<div class="alert alert-info">Dashboard content loading...</div>',
        'users': () => typeof getUserManagementContent === 'function' ? getUserManagementContent() : '<div class="alert alert-info">User management content loading...</div>',
        'restaurants': () => typeof getRestaurantManagementContent === 'function' ? getRestaurantManagementContent() : '<div class="alert alert-info">Restaurant management content loading...</div>',
        'orders': () => typeof getOrderManagementContent === 'function' ? getOrderManagementContent() : '<div class="alert alert-info">Order management content loading...</div>',
        'meals': () => typeof getMealManagementContent === 'function' ? getMealManagementContent() : '<div class="alert alert-info">Meal management content loading...</div>',
        'analytics': () => typeof getAnalyticsContent === 'function' ? getAnalyticsContent() : '<div class="alert alert-info">Analytics content loading...</div>',
        'settings': () => typeof getSettingsContent === 'function' ? getSettingsContent() : '<div class="alert alert-info">Settings content loading...</div>'
    };

    sectionContent = contentFunctions[sectionName] ? contentFunctions[sectionName]() : '<div class="alert alert-info">Section coming soon!</div>';

    // Create section element
    const section = document.createElement('div');
    section.id = `${sectionName}-section`;
    section.className = 'admin-section';
    section.innerHTML = sectionContent;

    // Add to main content
    mainContent.appendChild(section);
    section.style.display = 'block';
}

// View Toggle Functions
function toggleView(viewType) {
    const simpleViewBtn = document.getElementById('simpleViewBtn');
    const comprehensiveViewBtn = document.getElementById('comprehensiveViewBtn');
    const simpleViewSection = document.getElementById('simple-view-section');
    const dashboardSection = document.getElementById('dashboard-section');

    if (viewType === 'simple') {
        // Show simple view
        if (simpleViewSection) simpleViewSection.style.display = 'block';
        if (dashboardSection) dashboardSection.style.display = 'none';

        // Update button states
        simpleViewBtn.classList.remove('btn-outline-primary');
        simpleViewBtn.classList.add('btn-primary');
        comprehensiveViewBtn.classList.remove('btn-primary');
        comprehensiveViewBtn.classList.add('btn-outline-primary');

        // Update sidebar to show simple navigation
        updateSidebarForSimpleView();

    } else {
        // Show comprehensive view
        if (simpleViewSection) simpleViewSection.style.display = 'none';
        if (dashboardSection) dashboardSection.style.display = 'block';

        // Update button states
        comprehensiveViewBtn.classList.remove('btn-outline-primary');
        comprehensiveViewBtn.classList.add('btn-primary');
        simpleViewBtn.classList.remove('btn-primary');
        simpleViewBtn.classList.add('btn-outline-primary');

        // Update sidebar to show comprehensive navigation
        updateSidebarForComprehensiveView();
    }
}

function updateSidebarForSimpleView() {
    // Hide detailed management sections in sidebar
    const sidebarLinks = document.querySelectorAll('.admin-nav-link');
    sidebarLinks.forEach(link => {
        const section = link.getAttribute('data-section');
        if (['users', 'orders', 'restaurants', 'meals', 'analytics', 'settings'].includes(section)) {
            link.style.display = 'none';
        }
    });

    // Show only overview
    const overviewLink = document.querySelector('[data-section="dashboard"]');
    if (overviewLink) {
        overviewLink.classList.add('active');
    }
}

function updateSidebarForComprehensiveView() {
    // Show all sidebar links
    const sidebarLinks = document.querySelectorAll('.admin-nav-link');
    sidebarLinks.forEach(link => {
        link.style.display = 'block';
    });
}
