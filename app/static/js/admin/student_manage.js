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

// Status filter
document.getElementById('statusFilter').addEventListener('change', function() {
    const filterValue = this.value.toLowerCase();
    const table = document.getElementById('studentTableBody');
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const statusCell = rows[i].getElementsByTagName('td')[3];
        
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
        } else if (sortBy === 'date_registered') {
            aValue = new Date(a.getElementsByTagName('td')[5].textContent);
            bValue = new Date(b.getElementsByTagName('td')[5].textContent);
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

// Function to toggle student active status
function toggleStudentStatus(studentId, newStatus) {

    if (!confirm('Are you sure you want to ' + (newStatus ? 'activate' : 'deactivate') + ' this student account?')) {
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
            // Reload page to show updated status
            window.location.reload();
        } else {
            // Create a flash-like message
            const flashContainer = document.createElement('div');
            flashContainer.className = 'mb-6 p-4 rounded-lg shadow-sm bg-red-100 text-red-800 flex justify-between items-center';
            
            const messageSpan = document.createElement('span');
            messageSpan.textContent = 'Error: ' + data.message;
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
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Create a flash-like message for errors
        const flashContainer = document.createElement('div');
        flashContainer.className = 'mb-6 p-4 rounded-lg shadow-sm bg-red-100 text-red-800 flex justify-between items-center';
        flashContainer.innerHTML = `
            <span>An unexpected error occurred. Please try again.</span>
            <button type="button" class="text-gray-500 hover:text-gray-700 focus:outline-none transition-colors duration-200" onclick="this.parentElement.style.display='none'">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        `;
        
        // Insert at the top of the content
        const contentContainer = document.querySelector('.container');
        contentContainer.insertBefore(flashContainer, contentContainer.firstChild);
    });
}