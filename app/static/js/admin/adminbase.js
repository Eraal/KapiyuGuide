function openProfileModal() {
document.getElementById('profileModal').classList.remove('hidden');
}

function closeProfileModal() {
document.getElementById('profileModal').classList.add('hidden');
}


function openEditProfileModal() {
closeProfileModal();
document.getElementById('editProfileModal').classList.remove('hidden');
}

function closeEditProfileModal() {
document.getElementById('editProfileModal').classList.add('hidden');
openProfileModal();
}

// Change Password Modal Functions
function openChangePasswordModal() {
closeProfileModal();
document.getElementById('changePasswordModal').classList.remove('hidden');
}

function closeChangePasswordModal() {
document.getElementById('changePasswordModal').classList.add('hidden');
document.getElementById('changePasswordForm').reset();
document.getElementById('password-match-error').classList.add('hidden');
openProfileModal();
}

// Change Photo Modal Functions
function openChangePhotoModal() {
closeProfileModal();
document.getElementById('changePhotoModal').classList.remove('hidden');
}

function closeChangePhotoModal() {
document.getElementById('changePhotoModal').classList.add('hidden');
document.getElementById('changePhotoForm').reset();
openProfileModal();
}

function previewPhoto(input) {
if (input.files && input.files[0]) {
    var reader = new FileReader();
    
    reader.onload = function(e) {
        var preview = document.getElementById('photoPreview');
        preview.innerHTML = '<img src="' + e.target.result + '" alt="Profile Preview" class="w-full h-full object-cover">';
    }
    
    reader.readAsDataURL(input.files[0]);
}
}

function removeProfilePhoto() {
if (confirm('Are you sure you want to remove your profile photo?')) {
    // Create a CSRF token if needed (using meta tag value or similar)
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    
    // Send fetch request to remove photo
    fetch('/admin/remove_profile_photo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var preview = document.getElementById('photoPreview');
            var initials = document.querySelector('#profile-initials-value')?.textContent || 'U';
            preview.innerHTML = initials;
            preview.className = 'w-full h-full flex items-center justify-center bg-blue-800 text-white text-4xl';
            closeChangePhotoModal();
            // Reload page to update all instances of the profile picture
            location.reload();
        } else {
            alert('Failed to remove profile photo: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to process request. Please try again.');
    });
}
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
// Password change form validation
const changePasswordForm = document.getElementById('changePasswordForm');
if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', function(e) {
        const newPassword = document.getElementById('new_password').value;
        const confirmPassword = document.getElementById('confirm_new_password').value;
        const passwordError = document.getElementById('password-match-error');
        
        if (newPassword !== confirmPassword) {
            e.preventDefault();
            passwordError.classList.remove('hidden');
            return false;
        } else {
            passwordError.classList.add('hidden');
        }
    });
}

// Edit profile form validation
const editProfileForm = document.getElementById('editProfileForm');
if (editProfileForm) {
editProfileForm.addEventListener('submit', function(e) {
    // Get form elements directly from the form
    const firstNameInput = editProfileForm.querySelector('[name="first_name"]');
    const lastNameInput = editProfileForm.querySelector('[name="last_name"]');
    const emailInput = editProfileForm.querySelector('[name="email"]');
    
    // Get values and trim
    const firstName = firstNameInput ? firstNameInput.value.trim() : '';
    const lastName = lastNameInput ? lastNameInput.value.trim() : '';
    const email = emailInput ? emailInput.value.trim() : '';
    
    console.log("Form values:", { firstName, lastName, email }); // Debug output
    
    if (!firstName || !lastName || !email) {
        e.preventDefault();
        alert('Please fill all required fields');
        return false;
    }
    
    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        e.preventDefault();
        alert('Please enter a valid email address');
        return false;
    }
});
}

// Photo form validation
const changePhotoForm = document.getElementById('changePhotoForm');
if (changePhotoForm) {
    changePhotoForm.addEventListener('submit', function(e) {
        const fileInput = document.getElementById('profile_photo');
        
        if (fileInput.files.length === 0) {
            e.preventDefault();
            alert('Please select a file to upload');
            return false;
        }
        
        const file = fileInput.files[0];
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const maxSizeInBytes = 2 * 1024 * 1024; // 2MB
        
        if (!allowedTypes.includes(file.type)) {
            e.preventDefault();
            alert('Invalid file type. Please upload a JPG, PNG, or GIF file.');
            return false;
        }
        
        if (file.size > maxSizeInBytes) {
            e.preventDefault();
            alert('File size exceeds the maximum limit of 2MB.');
            return false;
        }
    });
}

// Add flash message functionality
const flashMessages = document.querySelectorAll('.flash-message');
if (flashMessages.length > 0) {
    flashMessages.forEach(message => {
        // Auto-dismiss flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
        
        // Add close button functionality
        const closeBtn = message.querySelector('.close-flash');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 500);
            });
        }
    });
}
});
