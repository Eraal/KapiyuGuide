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
            window.location.reload(); // Refresh the page to reflect the new status
        } else {
            console.error('Error toggling student status:', data.message);
        }
    })
    .catch(error => {
        console.error('Unexpected error:', error);
    });
}
