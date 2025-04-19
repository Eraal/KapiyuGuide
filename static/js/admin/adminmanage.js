    document.addEventListener('DOMContentLoaded', function() {
        // Filter functionality (unchanged)
        const statusFilter = document.getElementById('statusFilter');
        const sortFilter = document.getElementById('sortFilter');
        const searchInput = document.getElementById('adminSearchInput');
        
        statusFilter.addEventListener('change', filterAdmins);
        sortFilter.addEventListener('change', filterAdmins);
        searchInput.addEventListener('input', filterAdmins);

        // Form validation and submission
        const addAdminForm = document.getElementById('addAdminForm');
        if (addAdminForm) {
            addAdminForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Validate form before submission
                if (!validateForm()) {
                    return false;
                }
                
                const formData = new FormData(this);
                
                // Add loading state to button
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
                                // Refresh the page after a short delay
                                setTimeout(() => {
                                    window.location.reload();
                                }, 1000);
                            } else {
                                showNotification(data.message || 'Error adding admin', 'error');
                                // Reset button state
                                submitButton.disabled = false;
                                submitButton.innerHTML = originalText;
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('An error occurred while adding admin', 'error');
                    // Reset button state
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                });
            });
        }
        
        function filterAdmins() {
            // Existing filter functionality (unchanged)
            const statusValue = statusFilter.value;
            const sortValue = sortFilter.value;
            const searchValue = searchInput.value.toLowerCase();
            const rows = document.querySelectorAll('#adminTableBody tr');
            
            rows.forEach(row => {
                const office = row.cells[0].textContent.trim().toLowerCase();
                const name = row.cells[1].textContent.trim().toLowerCase();
                const email = row.cells[2].textContent.trim().toLowerCase();
                const status = row.cells[3].textContent.trim().toLowerCase();
                
                // Filter by status
                let showRow = true;
                if (statusValue !== 'all') {
                    showRow = status === statusValue;
                }
                
                // Filter by search
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
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded shadow-lg ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`;
        notification.textContent = message;
        
        // Add to document
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Step indicator functions
    let currentStep = 1;
    
    function nextStep(step) {
        // Hide current step
        document.getElementById(`step${currentStep}Content`).classList.add('hidden');
        
        // Show next step
        document.getElementById(`step${step}Content`).classList.remove('hidden');
        
        // Update step indicators
        updateStepIndicators(step);
        
        // Update current step tracker
        currentStep = step;
    }
    
    function prevStep(step) {
        // Hide current step
        document.getElementById(`step${currentStep}Content`).classList.add('hidden');
        
        // Show previous step
        document.getElementById(`step${step}Content`).classList.remove('hidden');
        
        // Update step indicators
        updateStepIndicators(step);
        
        // Update current step tracker
        currentStep = step;
    }
    
    function updateStepIndicators(activeStep) {
        // Reset all steps to inactive
        document.getElementById('step-info').className = 'flex w-full items-center text-gray-400 after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-gray-300 after:border-2 after:inline-block';
        document.getElementById('step-info').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
        
        document.getElementById('step-security').className = 'flex w-full items-center text-gray-400 after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-gray-300 after:border-2 after:inline-block';
        document.getElementById('step-security').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
        
        document.getElementById('step-role').className = 'flex items-center text-gray-400';
        document.getElementById('step-role').querySelector('span:first-child').className = 'flex items-center justify-center w-8 h-8 bg-gray-300 rounded-full shrink-0';
        
        // Set active step
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
        // Check if passwords match
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        if (password !== confirmPassword) {
            // Show step 2 and password error
            nextStep(2);
            document.getElementById('password-error').classList.remove('hidden');
            return false;
        }
        
        // Check if required fields are filled
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const officeId = document.getElementById('office').value;
        
        if (!name || !email || !password || !officeId) {
            showNotification('Please fill all required fields', 'error');
            return false;
        }
        
        return true;
    }
    
    // Add Admin Modal Functions
    function openAddAdminModal() {
        document.getElementById('addAdminModal').classList.remove('hidden');
        // Reset to first step when opening modal
        currentStep = 1;
        updateStepIndicators(1);
        
        // Show step 1 content, hide others
        document.getElementById('step1Content').classList.remove('hidden');
        document.getElementById('step2Content').classList.add('hidden');
        document.getElementById('step3Content').classList.add('hidden');
        
        // Reset form
        document.getElementById('addAdminForm').reset();
        document.getElementById('password-error').classList.add('hidden');
    }
    
    function closeAddAdminModal() {
        document.getElementById('addAdminModal').classList.add('hidden');
    }
    
    // Office Modal Functions
    function openOfficeModal(officeId, officeName) {
        document.getElementById('officeModalTitle').textContent = officeName + ' Office';
        document.getElementById('officeAdminsContainer').innerHTML = '<div class="animate-pulse">Loading admins...</div>';
        document.getElementById('viewOfficeModal').classList.remove('hidden');
        
        // Fetch office admins data
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
                                    <p class="font-medium">${admin.name}</p>
                                    <p class="text-sm text-gray-500">${admin.email}</p>
                                </div>
                                <span class="${admin.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} py-1 px-2 rounded-full text-xs">
                                    ${admin.is_active ? 'Active' : 'Inactive'}
                                </span>
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
    
    // Delete Admin Functions
    function confirmDeleteAdmin(adminId) {
        document.getElementById('deleteAdminId').value = adminId;
        document.getElementById('deleteConfirmModal').classList.remove('hidden');
        
        document.getElementById('cancelDeleteBtn').onclick = function() {
            document.getElementById('deleteConfirmModal').classList.add('hidden');
        };
    }
    
    // Edit Admin Function (would need a similar modal to add admin)
    function openEditAdminModal(adminId) {
        // Fetch admin data and populate edit form
        alert('Edit functionality would open modal with admin ID: ' + adminId);
        // Implement similar to the add admin modal
    }

    // Add these functions to the existing JavaScript

// Edit Admin Functions
function openEditAdminModal(adminId, name, email, officeId, isActive) {
    // Set values in edit form
    document.getElementById('edit_admin_id').value = adminId;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_email').value = email;
    
    // Set office dropdown value
    if (officeId) {
        document.getElementById('edit_office').value = officeId;
    }
    
    // Set active status
    if (isActive) {
        document.getElementById('edit_active').checked = true;
    } else {
        document.getElementById('edit_inactive').checked = true;
    }
    
    // Show modal
    document.getElementById('editAdminModal').classList.remove('hidden');
}

function closeEditAdminModal() {
    document.getElementById('editAdminModal').classList.add('hidden');
}

// Add event listener for edit form submission
document.addEventListener('DOMContentLoaded', function() {
    const editAdminForm = document.getElementById('editAdminForm');
    if (editAdminForm) {
        editAdminForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Add loading state to button
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            
            const formData = new FormData(this);
            
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
                            showNotification('Admin updated successfully', 'success');
                            closeEditAdminModal();
                            // Refresh page after a short delay
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        } else {
                            showNotification(data.message || 'Error updating admin', 'error');
                            // Reset button state
                            submitButton.disabled = false;
                            submitButton.innerHTML = originalText;
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while updating admin', 'error');
                // Reset button state
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
        });
    }
});
