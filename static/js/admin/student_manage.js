// Search functionality
document.getElementById('searchInput').addEventListener('keyup', function() {
    const searchText = this.value.toLowerCase();
    const table = document.getElementById('studentTableBody');
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const nameCell = rows[i].getElementsByTagName('td')[1];
        const emailCell = rows[i].getElementsByTagName('td')[2];
        
        if (nameCell && emailCell) {
            const name = nameCell.textContent.toLowerCase();
            const email = emailCell.textContent.toLowerCase();
            
            if (name.includes(searchText) || email.includes(searchText)) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
});

// Login status filter
document.getElementById('loginStatusFilter').addEventListener('change', function() {
    const filterValue = this.value.toLowerCase();
    const table = document.getElementById('studentTableBody');
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const statusCell = rows[i].getElementsByTagName('td')[3]; // Login status column
        
        if (statusCell) {
            const status = statusCell.textContent.toLowerCase();
            
            if (filterValue === '' || status.includes(filterValue)) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
});

// Account lock status filter
document.getElementById('lockStatusFilter').addEventListener('change', function() {
    const filterValue = this.value.toLowerCase();
    const table = document.getElementById('studentTableBody');
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const lockStatusCell = rows[i].getElementsByTagName('td')[4]; // Account lock status column
        
        if (lockStatusCell) {
            const status = lockStatusCell.textContent.toLowerCase();
            
            if (filterValue === '' || status.includes(filterValue)) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
});

// Sort functionality
document.getElementById('sortBy').addEventListener('change', function() {
    const sortBy = this.value;
    const table = document.getElementById('studentTableBody');
    const rows = Array.from(table.getElementsByTagName('tr'));
    
    if (sortBy === '') return;
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        if (sortBy === 'name') {
            aValue = a.getElementsByTagName('td')[1].textContent.toLowerCase();
            bValue = b.getElementsByTagName('td')[1].textContent.toLowerCase();
        } else if (sortBy === 'email') {
            aValue = a.getElementsByTagName('td')[2].textContent.toLowerCase();
            bValue = b.getElementsByTagName('td')[2].textContent.toLowerCase();
        } else if (sortBy === 'login_status') {
            aValue = a.getElementsByTagName('td')[3].textContent.toLowerCase();
            bValue = b.getElementsByTagName('td')[3].textContent.toLowerCase();
        } else if (sortBy === 'lock_status') {
            aValue = a.getElementsByTagName('td')[4].textContent.toLowerCase();
            bValue = b.getElementsByTagName('td')[4].textContent.toLowerCase();
        } else if (sortBy === 'date_registered') {
            aValue = new Date(a.getElementsByTagName('td')[6].textContent);
            bValue = new Date(b.getElementsByTagName('td')[6].textContent);
        }
        
        if (aValue < bValue) return -1;
        if (aValue > bValue) return 1;
        return 0;
    });
    
    // Remove all existing rows
    while (table.firstChild) {
        table.removeChild(table.firstChild);
    }
    
    // Add sorted rows
    rows.forEach(row => table.appendChild(row));
});

// Function to toggle student account lock
function toggleStudentLock(studentId, shouldLock) {
    // Update confirmation message to be clearer about what's happening
    const action = shouldLock ? 'lock' : 'unlock';
    const reasonPrompt = shouldLock ? prompt("Please provide a reason for locking this account:", "") : "";
    
    // If user cancels the prompt for lock reason or the lock action itself
    if (shouldLock && reasonPrompt === null) {
        return;
    }
    
    if (!confirm(`Are you sure you want to ${action} this student account?`)) {
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch('/admin/toggle_student_lock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            student_id: studentId,
            should_lock: shouldLock,
            reason: reasonPrompt
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the button text and style without reloading the page
            updateLockStatus(studentId, data.account_locked, data.lock_reason, data.locked_at);
            
            // Show success message
            createFlashMessage('success', 
                `Student account ${data.account_locked ? 'locked' : 'unlocked'} successfully`);
        } else {
            // Show error message
            createFlashMessage('error', 'Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        createFlashMessage('error', 'An unexpected error occurred. Please try again.');
    });
}

// Helper function to update lock status without page reload
function updateLockStatus(studentId, isLocked, lockReason, lockedAt) {
    // Find the row for this student
    const row = document.querySelector(`tr[data-student-id="${studentId}"]`) || 
                // Fallback selector if data attribute isn't present
                Array.from(document.querySelectorAll('button'))
                .find(btn => btn.onclick && btn.onclick.toString().includes(`toggleStudentLock(${studentId}`))
                ?.closest('tr');
    
    if (!row) return;
    
    // Find the lock button
    const lockButton = row.querySelector('.lock-button');
    if (!lockButton) return;
    
    // Update button appearance
    if (isLocked) {
        lockButton.className = lockButton.className.replace(/bg-orange-\d00/g, 'bg-green-500');
        lockButton.className = lockButton.className.replace(/hover:bg-orange-\d00/g, 'hover:bg-green-600');
        lockButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            UNLOCK
        `;
        lockButton.onclick = function() { toggleStudentLock(studentId, false); };
        
        // Add tooltip with lock reason if available
        if (lockReason) {
            lockButton.setAttribute('title', `Locked: ${lockReason} (${lockedAt})`);
        }
    } else {
        lockButton.className = lockButton.className.replace(/bg-green-\d00/g, 'bg-orange-500');
        lockButton.className = lockButton.className.replace(/hover:bg-green-\d00/g, 'hover:bg-orange-600');
        lockButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>
            LOCK
        `;
        lockButton.onclick = function() { toggleStudentLock(studentId, true); };
        lockButton.removeAttribute('title');
    }
    
    // Also update the lock status cell if it exists
    const lockStatusCell = row.querySelector('.lock-status');
    if (lockStatusCell) {
        if (isLocked) {
            lockStatusCell.innerHTML = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800" title="' + (lockReason || 'No reason provided') + '">Locked</span>';
        } else {
            lockStatusCell.innerHTML = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Unlocked</span>';
        }
    }
}

// Keep the original toggleStudentStatus for activation/deactivation
function toggleStudentStatus(studentId, newStatus) {
    // Update confirmation message to be clearer about what's happening
    const action = newStatus ? 'enable access to' : 'restrict access to';
    if (!confirm(`Are you sure you want to ${action} this student account?`)) {
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch('/admin/toggle_student_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            student_id: studentId,
            is_active: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the button text and style without reloading the page
            updateButtonStatus(studentId, data.is_active);
            
            // Show success message
            createFlashMessage('success', 
                `Student account ${data.is_active ? 'activated' : 'deactivated'} successfully`);
        } else {
            // Show error message
            createFlashMessage('error', 'Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        createFlashMessage('error', 'An unexpected error occurred. Please try again.');
    });
}

// Helper function to create flash messages
function createFlashMessage(type, message) {
    const flashContainer = document.createElement('div');
    flashContainer.className = `mb-6 p-4 rounded-lg shadow-sm ${type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} flex justify-between items-center`;
    
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    flashContainer.appendChild(messageSpan);
    
    const closeButton = document.createElement('button');
    closeButton.className = 'text-gray-500 hover:text-gray-700 focus:outline-none transition-colors duration-200';
    closeButton.innerHTML = '<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
    closeButton.onclick = function() {
        this.parentElement.style.display = 'none';
    };
    flashContainer.appendChild(closeButton);
    
    // Insert at the top of the content
    const contentContainer = document.querySelector('.container');
    contentContainer.insertBefore(flashContainer, contentContainer.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (flashContainer.parentNode) {
            flashContainer.parentNode.removeChild(flashContainer);
        }
    }, 5000);
}

// Helper function to update button without page reload
function updateButtonStatus(studentId, isActive) {
    // Find the button for this student
    const row = document.querySelector(`tr[data-student-id="${studentId}"]`) || 
                // Fallback selector if data attribute isn't present
                Array.from(document.querySelectorAll('button'))
                .find(btn => btn.onclick && btn.onclick.toString().includes(`toggleStudentStatus(${studentId}`))
                ?.closest('tr');
    
    if (!row) return;
    
    const button = row.querySelector('button');
    if (!button) return;
    
    // Update button appearance
    if (isActive) {
        button.className = button.className.replace(/bg-green-\d00/g, 'bg-red-500');
        button.className = button.className.replace(/hover:bg-green-\d00/g, 'hover:bg-red-600');
        button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
            DEACTIVATE
        `;
        button.onclick = function() { toggleStudentStatus(studentId, 0); };
    } else {
        button.className = button.className.replace(/bg-red-\d00/g, 'bg-green-500');
        button.className = button.className.replace(/hover:bg-red-\d00/g, 'hover:bg-green-600');
        button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            ACTIVATE
        `;
        button.onclick = function() { toggleStudentStatus(studentId, 1); };
    }
    
    // Also update the status cell
    const statusCell = row.querySelector('td:nth-child(4)');
    if (statusCell) {
        if (isActive) {
            statusCell.innerHTML = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>';
        } else {
            statusCell.innerHTML = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Inactive</span>';
        }
    }
}


