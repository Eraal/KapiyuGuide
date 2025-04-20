document.addEventListener('DOMContentLoaded', function() {
    const statusFilter = document.getElementById('statusFilter');
    const sortFilter = document.getElementById('sortFilter');
    const searchInput = document.getElementById('adminSearchInput');
    
    if (statusFilter) statusFilter.addEventListener('change', filterAdmins);
    if (sortFilter) sortFilter.addEventListener('change', filterAdmins);
    if (searchInput) searchInput.addEventListener('input', filterAdmins);

    const addAdminForm = document.getElementById('addAdminForm');
    if (addAdminForm) {
        addAdminForm.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!validateForm()) {
                return false;
            }
            
            const formData = new FormData(this);

            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json().then(data => {
                        if (data.success) {
                            showNotification('Admin added successfully', 'success');
                            closeAddAdminModal();

                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        } else {
                            showNotification(data.message || 'Error adding admin', 'error');

                            submitButton.disabled = false;
                            submitButton.innerHTML = originalText;
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while adding admin', 'error');

                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
        });
    }
    
    function filterAdmins() {
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
});

// Show notification function
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded shadow-lg ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

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
    document.getElementById('step-info').className = 'flex w-full items-center text-gray-400 after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-gray-300 after:border-2 after:inline-block';
    document.getElementById('step-info').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
    
    document.getElementById('step-security').className = 'flex w-full items-center text-gray-400 after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-gray-300 after:border-2 after:inline-block';
    document.getElementById('step-security').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
    
    document.getElementById('step-role').className = 'flex items-center text-gray-400';
    document.getElementById('step-role').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
    
    if (activeStep >= 1) {
        document.getElementById('step-info').className = 'flex w-full items-center text-blue-800 after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-blue-800 after:border-2 after:inline-block';
        document.getElementById('step-info').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-blue-800 rounded-full shrink-0 text-white';
    }
    
    if (activeStep >= 2) {
        document.getElementById('step-security').className = 'flex w-full items-center text-blue-800 after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-blue-800 after:border-2 after:inline-block';
        document.getElementById('step-security').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-blue-800 rounded-full shrink-0 text-white';
    }
    
    if (activeStep >= 3) {
        document.getElementById('step-role').className = 'flex items-center text-blue-800';
        document.getElementById('step-role').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-blue-800 rounded-full shrink-0 text-white';
    }
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

// Add Admin Modal Functions
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
        // Get CSRF token from meta tag - adjust if you're using a different CSRF implementation
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
                // Show success message
                const alertElement = document.createElement('div');
                alertElement.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow z-50';
                alertElement.textContent = data.message;
                document.body.appendChild(alertElement);
                setTimeout(() => alertElement.remove(), 3000);
            } else {
                // Show error message
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error removing admin:', error);
            alert('An error occurred while removing the admin');
        });
    }
}

// Delete Admin Functions
function confirmDeleteAdmin(adminId) {
    document.getElementById('deleteAdminId').value = adminId;
    document.getElementById('deleteConfirmModal').classList.remove('hidden');
    
    document.getElementById('cancelDeleteBtn').onclick = function() {
        document.getElementById('deleteConfirmModal').classList.add('hidden');
    };
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
                
                if (admin.office_id) {
                    document.getElementById('edit_office').value = admin.office_id;
                }

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

// Helper function to update office options
function updateOfficeOptions() {
    fetch('/admin/api/offices')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const select = document.getElementById('edit_office');
                
                let options = '<option value="">Select Office</option>';
                
                data.offices.forEach(office => {
                    options += `<option value="${office.id}">${office.name}</option>`;
                });
                
                select.innerHTML = options;
                
                const previousValue = select.getAttribute('data-value');
                if (previousValue) {
                    select.value = previousValue;
                }
            }
        })
        .catch(error => console.error('Error fetching offices:', error));
}

// Add event listener for edit form submission
document.addEventListener('DOMContentLoaded', function() {
    const editAdminForm = document.getElementById('editAdminForm');
    if (editAdminForm) {
        editAdminForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Form submitted");
            
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            
            const formData = new FormData(this);
            
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
            
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                console.log("Response received", response);
                if (response.redirected) {
                    console.log("Redirecting to", response.url);
                    window.location.href = response.url;
                } else {
                    return response.json().then(data => {
                        console.log("Response data", data);
                        if (data.success) {
                            showNotification('Admin updated successfully', 'success');
                            closeEditAdminModal();

                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        } else {
                            showNotification(data.message || 'Error updating admin', 'error');

                            submitButton.disabled = false;
                            submitButton.innerHTML = originalText;
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while updating admin', 'error');

                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
        });
    } else {
        console.error("Edit admin form not found!");
    }
});