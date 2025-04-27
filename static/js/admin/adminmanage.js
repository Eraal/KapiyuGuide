document.addEventListener('DOMContentLoaded', function() {
    // Initialize filters
    initializeFilters();
    // Initialize forms
    initializeForms();
    // Setup modal handlers
    setupModalHandlers();
    // Setup WebSocket connection
    setupWebSocket();
});

function initializeFilters() {
    const statusFilter = document.getElementById('statusFilter');
    const sortFilter = document.getElementById('sortFilter');
    const searchInput = document.getElementById('adminSearchInput');
    
    if (statusFilter) statusFilter.addEventListener('change', filterAdmins);
    if (sortFilter) sortFilter.addEventListener('change', filterAdmins);
    if (searchInput) searchInput.addEventListener('input', filterAdmins);
}

function filterAdmins() {
    const statusFilter = document.getElementById('statusFilter');
    const sortFilter = document.getElementById('sortFilter');
    const searchInput = document.getElementById('adminSearchInput');
    
    const statusValue = statusFilter.value;
    const sortValue = sortFilter.value;
    const searchValue = searchInput.value.toLowerCase();
    const rows = document.querySelectorAll('#adminTableBody tr');
    
    rows.forEach(row => {
        const office = row.cells[0].textContent.trim().toLowerCase();
        const name = row.cells[1].textContent.trim().toLowerCase();
        const email = row.cells[2].textContent.trim().toLowerCase();
        const status = row.cells[3].textContent.trim().toLowerCase();
        
        let showRow = true;
        if (statusValue !== 'all') {
            showRow = status === statusValue;
        }
        
        if (showRow && searchValue) {
            showRow = office.includes(searchValue) || 
                      name.includes(searchValue) || 
                      email.includes(searchValue);
        }
        
        row.style.display = showRow ? '' : 'none';
    });
}

function initializeForms() {
    // Initialize the add admin form
    const addAdminForm = document.getElementById('addAdminForm');
    if (addAdminForm) {
        addAdminForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Initialize the edit admin form
    const editAdminForm = document.getElementById('editAdminForm');
    if (editAdminForm) {
        editAdminForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Setup profile picture preview
    const profilePicInput = document.getElementById('edit_profile_pic');
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(event) {
            updateProfilePreview(event, 'edit_profile_preview');
        });
    }
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    if (this.id === 'addAdminForm' && !validateForm()) {
        return false;
    }
    
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    
    const formData = new FormData(this);
    
    // Debug: Log form data
    console.log('Form action:', this.action);
    console.log('Form ID:', this.id);
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }
    
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            // Don't set Content-Type for FormData
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => {
        // Check if response is ok before trying to parse JSON
        if (!response.ok) {
            return response.text().then(text => {
                console.error('Server error response:', text);
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            });
        }
        
        if (response.redirected) {
            window.location.href = response.url;
            return { success: true, redirected: true };
        } 
        
        return response.json();
    })
    .then(data => {
        if (data.redirected) return; // Already handled
        
        if (data.success) {
            const message = this.id === 'addAdminForm' ? 
                'Admin added successfully' : 'Admin updated successfully';
            showNotification(message, 'success');
            
            if (this.id === 'addAdminForm') {
                closeAddAdminModal();
            } else {
                closeEditAdminModal();
            }
        } else {
            const errorMsg = data.message || 
                (this.id === 'addAdminForm' ? 'Error adding admin' : 'Error updating admin');
            showNotification(errorMsg, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMsg = this.id === 'addAdminForm' ? 
            'An error occurred while adding admin' : 'An error occurred while updating admin';
        showNotification(errorMsg, 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
}

function setupModalHandlers() {
    // Add event listeners for delete confirmation
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', function() {
            document.getElementById('deleteConfirmModal').classList.add('hidden');
        });
    }
}

// WebSocket Setup and Handlers
function setupWebSocket() {
    // Check if socket.io library is loaded
    if (typeof io === 'undefined') {
        console.error('Socket.io library not loaded');
        return;
    }

    // Get current user email from the page (you'll need to add this)
    const userEmail = document.getElementById('currentUserEmail')?.value || 'Unknown user';
    
    // Connect to WebSocket server
    const socket = io();
    
    // Connection opened
    socket.on('connect', function() {
        
        
        console.log('WebSocket connection established');
        console.log('Connected to WebSocket server with ID:', socket.id);
        socket.emit('join', { room: 'join_admin_room' });
    });
    
    // Connection error
    socket.on('connect_error', function(error) {
        console.error('WebSocket connection error:', error);
        showNotification('WebSocket connection failed. Real-time updates disabled.', 'error');
    });
    
    // Listen for admin updated event
    socket.on('admin_updated', function(data) {
        
        adminManage_updateAdminRow(data.admin);
        showNotification(`Admin ${data.admin.first_name} ${data.admin.last_name} has been updated`, 'info');
    });
    
    // Listen for admin added event
    socket.on('admin_added', function(data) {
        console.log('Received admin_added event:', data);
        adminManage_addAdminRow(data.admin);
        adminManage_updateStatsCounter(data.stats);
        showNotification(`New admin ${data.admin.first_name} ${data.admin.last_name} has been added`, 'success');
    });
    
    // Listen for admin deleted event
    socket.on('admin_deleted', function(data) {
        adminManage_removeAdminRow(data.admin_id);
        adminManage_updateStatsCounter(data.stats);
        showNotification(`Admin has been deleted`, 'info');
    });
    
    // Listen for admin office assignment updated
    socket.on('admin_office_updated', function(data) {
        adminManage_updateAdminOffice(data.admin_id, data.office);
        showNotification(`Admin office assignment updated`, 'info');
    });
    
    // Listen for admin status updated
    socket.on('admin_status_updated', function(data) {
        adminManage_updateAdminStatus(data.admin_id, data.is_active);
        adminManage_updateStatsCounter(data.stats);
        showNotification(`Admin status updated`, 'info');
    });
}

// WebSocket event handlers with prefixed function names
function adminManage_updateAdminRow(admin) {
    const row = document.querySelector(`#adminTableBody tr[data-admin-id="${admin.id}"]`);
    if (row) {
        // Update office
        if (admin.office_name) {
            row.cells[0].textContent = admin.office_name;
        } else {
            row.cells[0].innerHTML = '<span class="text-gray-400 italic">Unassigned</span>';
        }
        
        // Update name
        row.cells[1].textContent = `${admin.first_name} ${admin.middle_name ? admin.middle_name + ' ' : ''}${admin.last_name}`;
        
        // Update email
        row.cells[2].textContent = admin.email;
        
        // Update status
        const statusCell = row.cells[3];
        if (admin.is_active) {
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>';
        } else {
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Inactive</span>';
        }
    }
}

function adminManage_addAdminRow(admin) {
    const tableBody = document.getElementById('adminTableBody');
    if (tableBody) {
        const newRow = document.createElement('tr');
        newRow.setAttribute('data-admin-id', admin.id);
        newRow.className = 'bg-white border-b hover:bg-gray-50';
        
        // Office column
        const officeCell = document.createElement('td');
        officeCell.className = 'px-6 py-4 whitespace-nowrap';
        if (admin.office_name) {
            officeCell.textContent = admin.office_name;
        } else {
            officeCell.innerHTML = '<span class="text-gray-400 italic">Unassigned</span>';
        }
        newRow.appendChild(officeCell);
        
        // Name column
        const nameCell = document.createElement('td');
        nameCell.className = 'px-6 py-4 whitespace-nowrap';
        nameCell.textContent = `${admin.first_name} ${admin.middle_name ? admin.middle_name + ' ' : ''}${admin.last_name}`;
        newRow.appendChild(nameCell);
        
        // Email column
        const emailCell = document.createElement('td');
        emailCell.className = 'px-6 py-4 whitespace-nowrap';
        emailCell.textContent = admin.email;
        newRow.appendChild(emailCell);
        
        // Status column
        const statusCell = document.createElement('td');
        statusCell.className = 'px-6 py-4 whitespace-nowrap';
        if (admin.is_active) {
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>';
        } else {
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Inactive</span>';
        }
        newRow.appendChild(statusCell);
        
        // Actions column
        const actionsCell = document.createElement('td');
        actionsCell.className = 'px-6 py-4 whitespace-nowrap text-right text-sm font-medium';
        actionsCell.innerHTML = `
            <a href="#" onclick="openEditAdminModal(${admin.id})" class="text-blue-600 hover:text-blue-900 mr-3">Edit</a>
            <a href="#" onclick="confirmDeleteAdmin(${admin.id})" class="text-red-600 hover:text-red-900">Delete</a>
        `;
        newRow.appendChild(actionsCell);
        
        // Add the new row to the table
        tableBody.appendChild(newRow);
    }
}

function adminManage_removeAdminRow(adminId) {
    const row = document.querySelector(`#adminTableBody tr[data-admin-id="${adminId}"]`);
    if (row) {
        row.remove();
    }
}

function adminManage_updateAdminOffice(adminId, office) {
    const row = document.querySelector(`#adminTableBody tr[data-admin-id="${adminId}"]`);
    if (row) {
        const officeCell = row.cells[0];
        if (office && office.name) {
            officeCell.textContent = office.name;
        } else {
            officeCell.innerHTML = '<span class="text-gray-400 italic">Unassigned</span>';
        }
    }
}

function adminManage_updateAdminStatus(adminId, isActive) {
    const row = document.querySelector(`#adminTableBody tr[data-admin-id="${adminId}"]`);
    if (row) {
        const statusCell = row.cells[3];
        if (isActive) {
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>';
        } else {
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Inactive</span>';
        }
    }
}

function adminManage_updateStatsCounter(stats) {
    if (stats) {
        // Update the stats counters in the dashboard
        if (stats.total_offices !== undefined) {
            document.getElementById('totalOfficesCounter').textContent = stats.total_offices;
        }
        if (stats.active_office_admins !== undefined) {
            document.getElementById('activeAdminsCounter').textContent = stats.active_office_admins;
        }
        if (stats.unassigned_offices !== undefined) {
            document.getElementById('unassignedOfficesCounter').textContent = stats.unassigned_offices;
        }
        if (stats.unassigned_admins !== undefined) {
            document.getElementById('unassignedAdminsCounter').textContent = stats.unassigned_admins;
        }
    }
}

// Multi-step form navigation
let currentStep = 1;

function nextStep(step) {
    document.getElementById(`step${currentStep}Content`).classList.add('hidden');
    document.getElementById(`step${step}Content`).classList.remove('hidden');
    updateStepIndicators(step);
    currentStep = step;
}

function prevStep(step) {
    document.getElementById(`step${currentStep}Content`).classList.add('hidden');
    document.getElementById(`step${step}Content`).classList.remove('hidden');  
    updateStepIndicators(step);
    currentStep = step;
}

function updateStepIndicators(activeStep) {
    const stepElements = [
        { id: 'step-info', step: 1 },
        { id: 'step-security', step: 2 },
        { id: 'step-role', step: 3 }
    ];
    
    stepElements.forEach(element => {
        const el = document.getElementById(element.id);
        const isActive = activeStep >= element.step;
        
        // Update main element class
        el.className = isActive ? 
            `flex ${element.id !== 'step-role' ? 'w-full' : ''} items-center text-blue-800 ${element.id !== 'step-role' ? 'after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-blue-800 after:border-2 after:inline-block' : ''}` :
            `flex ${element.id !== 'step-role' ? 'w-full' : ''} items-center text-gray-400 ${element.id !== 'step-role' ? 'after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-gray-300 after:border-2 after:inline-block' : ''}`;
        
        // Update span class
        const span = el.querySelector('span:first-child');
        span.className = isActive ?
            'flex items-center justify-center w-8 h-8 bg-blue-800 rounded-full shrink-0 text-white' :
            'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
    });
}

function validatePasswordAndNext() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const passwordError = document.getElementById('password-error');
    
    if (password !== confirmPassword) {
        passwordError.classList.remove('hidden');
        return false;
    } else {
        passwordError.classList.add('hidden');
        nextStep(3);
        return true;
    }
}

function validateForm() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        nextStep(2);
        document.getElementById('password-error').classList.remove('hidden');
        return false;
    }
    
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const email = document.getElementById('email').value;
    const officeId = document.getElementById('office').value;
    
    if (!firstName || !lastName || !email || !password || !officeId) {
        showNotification('Please fill all required fields', 'error');
        return false;
    }
    
    return true;
}

// Modal Functions
function openAddAdminModal() {
    document.getElementById('addAdminModal').classList.remove('hidden');
    currentStep = 1;
    updateStepIndicators(1);
    
    document.getElementById('step1Content').classList.remove('hidden');
    document.getElementById('step2Content').classList.add('hidden');
    document.getElementById('step3Content').classList.add('hidden');
    
    document.getElementById('addAdminForm').reset();
    document.getElementById('password-error').classList.add('hidden');
}

function closeAddAdminModal() {
    document.getElementById('addAdminModal').classList.add('hidden');
}

function openEditAdminModal(adminId) {
    fetch(`/admin/api/admin/${adminId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const admin = data.admin;
                
                document.getElementById('edit_admin_id').value = admin.id;
                document.getElementById('edit_first_name').value = admin.first_name || '';
                document.getElementById('edit_middle_name').value = admin.middle_name || '';
                document.getElementById('edit_last_name').value = admin.last_name || '';
                document.getElementById('edit_email').value = admin.email || '';

                // Handle profile picture
                const profilePreview = document.getElementById('edit_profile_preview');
                if (admin.profile_pic) {
                    profilePreview.src = `/static/${admin.profile_pic}`;
                } else {
                    profilePreview.src = '/static/images/default-avatar.png';
                }
                
                if (admin.office_id) {
                    document.getElementById('edit_office').value = admin.office_id;
                }

                // Set active status
                if (admin.is_active) {
                    document.getElementById('edit_active').checked = true;
                } else {
                    document.getElementById('edit_inactive').checked = true;
                }
                
                document.getElementById('editAdminModal').classList.remove('hidden');
            } else {
                showNotification(data.message || 'Error fetching admin data', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred while fetching admin data', 'error');
        });
}

function closeEditAdminModal() {
    document.getElementById('editAdminModal').classList.add('hidden');
}

function openOfficeModal(officeId, officeName) {
    document.getElementById('officeModalTitle').textContent = officeName + ' Office';
    document.getElementById('officeAdminsContainer').innerHTML = '<div class="animate-pulse">Loading admins...</div>';
    document.getElementById('viewOfficeModal').classList.remove('hidden');
    
    fetch('/admin/api/office/' + officeId + '/admins')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('officeAdminsContainer');
            
            if (data.admins && data.admins.length > 0) {
                let html = '<ul class="divide-y divide-gray-200">';
                data.admins.forEach(admin => {
                    html += `
                        <li class="py-3 flex justify-between items-center">
                            <div>
                                <p class="font-medium">${admin.full_name}</p>
                                <p class="text-sm text-gray-500">${admin.email}</p>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="${admin.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} py-1 px-2 rounded-full text-xs">
                                    ${admin.is_active ? 'Active' : 'Inactive'}
                                </span>
                                <button onclick="removeOfficeAdmin(${officeId}, ${admin.id})" 
                                        class="bg-red-500 hover:bg-red-600 text-white py-1 px-2 rounded text-xs">
                                    Remove
                                </button>
                            </div>
                        </li>
                    `;
                });
                html += '</ul>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="text-gray-500 italic">No administrators assigned to this office.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching office admins:', error);
            document.getElementById('officeAdminsContainer').innerHTML = 
                '<p class="text-red-500">Error loading administrators. Please try again.</p>';
        });
}

function closeOfficeModal() {
    document.getElementById('viewOfficeModal').classList.add('hidden');
}

function removeOfficeAdmin(officeId, adminId) {
    if (confirm('Are you sure you want to remove this admin from the office?')) {
        // Get CSRF token from meta tag
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        
        fetch('/admin/remove_office_admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                office_id: officeId,
                admin_id: adminId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Refresh the admins list
                openOfficeModal(officeId, document.getElementById('officeModalTitle').textContent.replace(' Office', ''));
                showNotification(data.message, 'success');
            } else {
                showNotification(data.message || 'Error removing admin', 'error');
            }
        })
        .catch(error => {
            console.error('Error removing admin:', error);
            showNotification('An error occurred while removing the admin', 'error');
        });
    }
}

function confirmDeleteAdmin(adminId) {
    document.getElementById('deleteAdminId').value = adminId;
    document.getElementById('deleteConfirmModal').classList.remove('hidden');
}

function resetAdminPassword() {
    const adminId = document.getElementById('edit_admin_id').value;
    
    if (!adminId) {
        showPasswordResetMessage('No admin selected', false);
        return;
    }
    
    if (!confirm('Are you sure you want to reset this admin\'s password to a default code?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('admin_id', adminId);
    
    fetch('/admin/reset_admin_password', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showPasswordResetMessage(`Password reset successfully. New password:`, true, data.password);
        } else {
            showPasswordResetMessage(data.message, false);
        }
    })
    .catch(error => {
        console.error('Error resetting password:', error);
        showPasswordResetMessage('Error resetting password. Please try again.', false);
    });
}

// Utility functions
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded shadow-lg ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        type === 'info' ? 'bg-blue-500' : 'bg-gray-500'} text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function showPasswordResetMessage(message, success, password = null) {
    // Remove any existing message
    const existingMessage = document.getElementById('passwordResetMessage');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create flash message container
    const flashMessage = document.createElement('div');
    flashMessage.id = 'passwordResetMessage';
    flashMessage.className = success 
        ? 'fixed top-4 right-4 bg-white shadow-lg rounded-lg p-4 max-w-sm w-full flex flex-col items-center border-l-4 border-green-500 z-50'
        : 'fixed top-4 right-4 bg-white shadow-lg rounded-lg p-4 max-w-sm w-full flex flex-col items-center border-l-4 border-red-500 z-50';
    
    // Create message content
    const messageContent = document.createElement('div');
    messageContent.className = 'w-full';
    
    // Add header
    const header = document.createElement('div');
    header.className = 'flex justify-between items-center mb-2';
    
    const title = document.createElement('h3');
    title.className = success ? 'font-medium text-green-700' : 'font-medium text-red-700';
    title.textContent = success ? 'Success' : 'Error';
    
    const closeButton = document.createElement('button');
    closeButton.className = 'text-gray-400 hover:text-gray-600';
    closeButton.innerHTML = '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>';
    closeButton.onclick = function() {
        document.getElementById('passwordResetMessage').remove();
    };
    
    header.appendChild(title);
    header.appendChild(closeButton);
    messageContent.appendChild(header);
    
    // Add message
    const messageText = document.createElement('p');
    messageText.className = 'text-sm text-gray-600 mb-2';
    messageText.textContent = message;
    messageContent.appendChild(messageText);
    
    // Add password display if provided
    if (password) {
        const passwordContainer = document.createElement('div');
        passwordContainer.className = 'bg-gray-50 p-4 rounded-md flex justify-center items-center my-2';
        
        const digits = password.split('');
        digits.forEach(digit => {
            const digitBox = document.createElement('div');
            digitBox.className = 'w-12 h-16 bg-white border border-gray-300 rounded-md mx-1 flex items-center justify-center text-2xl font-bold text-gray-800';
            digitBox.textContent = digit;
            passwordContainer.appendChild(digitBox);
        });
        
        messageContent.appendChild(passwordContainer);
        
        // Add copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'w-full mt-2 bg-blue-500 hover:bg-blue-600 text-white text-sm py-2 px-4 rounded transition duration-300';
        copyButton.textContent = 'Copy Password';
        copyButton.onclick = function() {
            navigator.clipboard.writeText(password).then(() => {
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.textContent = 'Copy Password';
                }, 2000);
            });
        };
        messageContent.appendChild(copyButton);
    }
    
    flashMessage.appendChild(messageContent);
    document.body.appendChild(flashMessage);
    
    // Auto-dismiss after 10 seconds if it's a success message
    if (success) {
        setTimeout(() => {
            const message = document.getElementById('passwordResetMessage');
            if (message) {
                message.remove();
            }
        }, 10000);
    }
}

function updateProfilePreview(event, previewId) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}