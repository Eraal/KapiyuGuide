// JavaScript to handle the Date Range filter
document.addEventListener('DOMContentLoaded', function() {
    const dateFilter = document.getElementById('date-filter');
    const customDateContainer = document.getElementById('custom-date-container');
    
    dateFilter.addEventListener('change', function() {
        if (this.value === 'custom') {
            customDateContainer.classList.remove('hidden');
        } else {
            customDateContainer.classList.add('hidden');
        }
    });
    
    // Export dropdown toggle
    const exportBtn = document.getElementById('exportBtn');
    const exportOptions = document.getElementById('exportOptions');
    
    exportBtn.addEventListener('click', function() {
        exportOptions.classList.toggle('hidden');
    });
    
    // Close export dropdown when clicking elsewhere
    document.addEventListener('click', function(event) {
        if (!exportBtn.contains(event.target)) {
            exportOptions.classList.add('hidden');
        }
    });
    
    // Modal handling for view details
    const modalButtons = document.querySelectorAll('.text-blue-600[title="View Details"]');
    const inquiryDetailModal = document.getElementById('inquiryDetailModal');
    const modalCloseButtons = document.querySelectorAll('.modal-close');
    const modalContent = document.getElementById('modal-content');
    
    modalButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            inquiryDetailModal.classList.remove('hidden');
            
            // Fetch inquiry details
            fetch(button.getAttribute('href'))
                .then(response => response.text())
                .then(data => {
                    modalContent.innerHTML = data;
                })
                .catch(error => {
                    modalContent.innerHTML = '<div class="text-center py-10 text-red-500">Error loading inquiry details.</div>';
                });
        });
    });
    
    modalCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            inquiryDetailModal.classList.add('hidden');
            modalContent.innerHTML = '<div class="flex justify-center items-center py-10"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-800"></div></div>';
        });
    });
    
    // Refresh button functionality
    document.getElementById('refreshBtn').addEventListener('click', function() {
        window.location.reload();
    });
});