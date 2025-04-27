// Modal control functions
function openNewAnnouncementModal() {
    document.getElementById('newAnnouncementModal').classList.remove('hidden');
}

function closeNewAnnouncementModal() {
    document.getElementById('newAnnouncementModal').classList.add('hidden');
    document.getElementById('newAnnouncementForm').reset();
    // Reset image uploads
    const container = document.getElementById('image-upload-container');
    const items = container.querySelectorAll('.image-upload-item');
    // Keep the first one, remove the rest
    for (let i = 1; i < items.length; i++) {
        container.removeChild(items[i]);
    }
    // Clear the first one's preview and hide remove button
    const firstItem = items[0];
    const preview = firstItem.querySelector('.image-preview');
    preview.innerHTML = '';
    firstItem.querySelector('.remove-image').classList.add('hidden');
}

function openEditAnnouncementModal(announcementId) {
    // Reset the form
    document.getElementById('editAnnouncementForm').reset();
    
    // Clear existing images container
    const existingImagesContainer = document.getElementById('existing-images-container');
    existingImagesContainer.innerHTML = ''; // Clear previous content
    
    // Reset new image uploads
    const container = document.getElementById('edit-image-upload-container');
    const items = container.querySelectorAll('.image-upload-item');
    // Keep the first one, remove the rest
    for (let i = 1; i < items.length; i++) {
        container.removeChild(items[i]);
    }
    // Clear the first one's preview and hide remove button
    const firstItem = items[0];
    const preview = firstItem.querySelector('.image-preview');
    preview.innerHTML = '';
    firstItem.querySelector('.remove-image').classList.add('hidden');
    
    // Fetch the announcement data from the server
    fetch(`/admin/get_announcement/${announcementId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('edit_announcement_id').value = data.id;
            document.getElementById('edit_title').value = data.title;
            document.getElementById('edit_content').value = data.content;
            
            if (data.is_public) {
                document.getElementById('edit_visibility').value = 'public';
                document.getElementById('editOfficeSelectionDiv').classList.add('hidden');
            } else {
                document.getElementById('edit_visibility').value = 'office';
                document.getElementById('editOfficeSelectionDiv').classList.remove('hidden');
                document.getElementById('edit_target_office_id').value = data.target_office_id;
            }
            
            // Populate existing images
            if (data.images && data.images.length > 0) {
                existingImagesContainer.classList.remove('hidden');
                
                data.images.forEach(image => {
                    const imageCard = document.createElement('div');
                    imageCard.className = 'bg-white p-3 rounded-lg shadow-sm border';
                    imageCard.innerHTML = `
                        <div class="relative mb-2">
                            <img src="${image.image_path}" alt="${image.caption || 'Announcement image'}" class="w-full h-32 object-cover rounded-md">
                        </div>
                        <div class="space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-sm font-medium">${image.caption || 'No caption'}</span>
                                <span class="text-xs bg-gray-100 px-2 py-1 rounded">Order: ${image.display_order}</span></div>
                            <button type="button" onclick="confirmDeleteImage('${image.id}', '${data.id}')" class="w-full text-center text-red-600 text-xs bg-red-50 hover:bg-red-100 py-1 rounded">
                                <i class="fas fa-trash-alt mr-1"></i> Remove
                            </button>
                            <input type="hidden" name="existing_image_ids[]" value="${image.id}">
                            <div class="grid grid-cols-2 gap-1 mt-2">
                                <div>
                                    <label class="block text-xs text-gray-700">Caption</label>
                                    <input type="text" name="existing_captions[]" value="${image.caption || ''}" class="w-full border border-gray-300 rounded-sm p-1 text-xs">
                                </div>
                                <div>
                                    <label class="block text-xs text-gray-700">Order</label>
                                    <input type="number" name="existing_display_orders[]" value="${image.display_order}" min="0" class="w-full border border-gray-300 rounded-sm p-1 text-xs">
                                </div>
                            </div>
                        </div>
                    `;
                    existingImagesContainer.appendChild(imageCard);
                });
            } else {
                existingImagesContainer.classList.add('hidden');
            }
            
            // Show the modal
            document.getElementById('editAnnouncementModal').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error fetching announcement data:', error);
            alert('Failed to load announcement data. Please try again.');
        });
}

function closeEditAnnouncementModal() {
    document.getElementById('editAnnouncementModal').classList.add('hidden');
}

function confirmDeleteAnnouncement(announcementId) {
    document.getElementById('delete_announcement_id').value = announcementId;
    document.getElementById('deleteConfirmationModal').classList.remove('hidden');
}

function closeDeleteConfirmationModal() {
    document.getElementById('deleteConfirmationModal').classList.add('hidden');
}

// Add this function to handle image deletion
function confirmDeleteImage(imageId, announcementId) {
    // Since deleteImageModal is missing in the HTML, we'll create a simple confirmation
    if (confirm('Are you sure you want to delete this image? This action cannot be undone.')) {
        // Create a form to submit the deletion request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/admin/delete_announcement_image';
        
        // Add CSRF token from an existing form
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = csrfToken;
        
        const imageIdInput = document.createElement('input');
        imageIdInput.type = 'hidden';
        imageIdInput.name = 'image_id';
        imageIdInput.value = imageId;
        
        const announcementIdInput = document.createElement('input');
        announcementIdInput.type = 'hidden';
        announcementIdInput.name = 'announcement_id';
        announcementIdInput.value = announcementId;
        
        form.appendChild(csrfInput);
        form.appendChild(imageIdInput);
        form.appendChild(announcementIdInput);
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Toggle office selection based on visibility
function toggleOfficeSelection() {
    const visibility = document.getElementById('visibility').value;
    const officeDiv = document.getElementById('officeSelectionDiv');
    
    if (visibility === 'office') {
        officeDiv.classList.remove('hidden');
        document.getElementById('target_office_id').setAttribute('required', 'required');
    } else {
        officeDiv.classList.add('hidden');
        document.getElementById('target_office_id').removeAttribute('required');
    }
}

function toggleEditOfficeSelection() {
    const visibility = document.getElementById('edit_visibility').value;
    const officeDiv = document.getElementById('editOfficeSelectionDiv');
    
    if (visibility === 'office') {
        officeDiv.classList.remove('hidden');
        document.getElementById('edit_target_office_id').setAttribute('required', 'required');
    } else {
        officeDiv.classList.add('hidden');
        document.getElementById('edit_target_office_id').removeAttribute('required');
    }
}

// Image upload functions
function previewImage(input) {
    const uploadItem = input.closest('.image-upload-item');
    const preview = uploadItem.querySelector('.image-preview');
    const removeButton = uploadItem.querySelector('.remove-image');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview" class="h-32 rounded-md shadow-sm">`;
            removeButton.classList.remove('hidden');
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

function createImageUploadItem(containerId) {
    const container = document.getElementById(containerId);
    const newItem = document.createElement('div');
    newItem.className = 'image-upload-item p-4 border border-dashed border-gray-300 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors duration-200';
    
    const fileInputName = containerId === 'image-upload-container' ? 'images[]' : 'new_images[]';
    const captionsName = containerId === 'image-upload-container' ? 'captions[]' : 'new_captions[]';
    const ordersName = containerId === 'image-upload-container' ? 'display_orders[]' : 'new_display_orders[]';
    
    newItem.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="col-span-1">
                <label class="block text-sm text-gray-700 mb-1">Image File*</label>
                <input type="file" name="${fileInputName}" accept="image/*" class="image-input block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer" onchange="previewImage(this)">
            </div>
            <div class="col-span-1">
                <label class="block text-sm text-gray-700 mb-1">Caption</label>
                <input type="text" name="${captionsName}" placeholder="Optional caption for this image" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div class="col-span-1">
                <label class="block text-sm text-gray-700 mb-1">Display Order</label>
                <input type="number" name="${ordersName}" min="0" value="0" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
        </div>
        <div class="image-preview mt-3 flex justify-center"></div>
        <button type="button" class="remove-image mt-2 text-red-600 hover:text-red-800 text-sm flex items-center transition-colors duration-200" onclick="removeImageUploadItem(this)">
            <i class="fas fa-trash mr-1"></i> Remove Image
        </button>
    `;
    
    container.appendChild(newItem);
    
    // Initially hide the remove button
    const removeButton = newItem.querySelector('.remove-image');
    removeButton.classList.add('hidden');
}

function removeImageUploadItem(button) {
    const item = button.closest('.image-upload-item');
    const container = item.parentElement;
    
    // Only remove if there's more than one upload item
    if (container.querySelectorAll('.image-upload-item').length > 1) {
        container.removeChild(item);
    } else {
        // Clear the input and preview instead of removing
        const input = item.querySelector('input[type="file"]');
        const preview = item.querySelector('.image-preview');
        input.value = '';
        preview.innerHTML = '';
        button.classList.add('hidden');
    }
}

function applyFilters() {
    const officeFilter = document.getElementById('officeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const dateRangeFilter = document.getElementById('dateRangeFilter').value;
    
    // Build query string
    let queryParams = new URLSearchParams();
    if (officeFilter) queryParams.append('office_id', officeFilter);  // Changed from 'office' to 'office_id'
    if (statusFilter) queryParams.append('visibility', statusFilter);  // Changed from 'status' to 'visibility'
    if (dateRangeFilter) queryParams.append('date_range', dateRangeFilter);
    
    // Redirect with filters
    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set up filter button
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    // Set up add more images buttons
    const addMoreImagesBtn = document.getElementById('add-more-images');
    if (addMoreImagesBtn) {
        addMoreImagesBtn.addEventListener('click', function() {
            createImageUploadItem('image-upload-container');
        });
    }
    
    const editAddMoreImagesBtn = document.getElementById('edit-add-more-images');
    if (editAddMoreImagesBtn) {
        editAddMoreImagesBtn.addEventListener('click', function() {
            createImageUploadItem('edit-image-upload-container');
        });
    }
    
    // Set up remove image buttons for the initial upload items
    document.querySelectorAll('.remove-image').forEach(button => {
        button.addEventListener('click', function() {
            removeImageUploadItem(this);
        });
    });
    
    // Initialize dropdowns
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        const button = dropdown.querySelector('button');
        const content = dropdown.querySelector('.dropdown-content');
        
        if (button && content) {
            // Initially hide dropdown content
            content.style.display = 'none';
            
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                if (content.style.display === 'none') {
                    // Hide all other dropdowns first
                    document.querySelectorAll('.dropdown-content').forEach(c => {
                        c.style.display = 'none';
                    });
                    // Show this dropdown
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-content').forEach(content => {
            content.style.display = 'none';
        });
    });
    
    // Initialize form validations
    const newAnnouncementForm = document.getElementById('newAnnouncementForm');
    if (newAnnouncementForm) {
        newAnnouncementForm.addEventListener('submit', function(e) {
            const visibility = document.getElementById('visibility').value;
            if (visibility === 'office') {
                const officeId = document.getElementById('target_office_id').value;
                if (!officeId) {
                    e.preventDefault();
                    alert('Please select a target office for office-specific announcements.');
                }
            }
        });
    }
    
    const editAnnouncementForm = document.getElementById('editAnnouncementForm');
    if (editAnnouncementForm) {
        editAnnouncementForm.addEventListener('submit', function(e) {
            const visibility = document.getElementById('edit_visibility').value;
            if (visibility === 'office') {
                const officeId = document.getElementById('edit_target_office_id').value;
                if (!officeId) {
                    e.preventDefault();
                    alert('Please select a target office for office-specific announcements.');
                }
            }
        });
    }
    
    // Initialize visibility toggles
    const visibilityDropdown = document.getElementById('visibility');
    if (visibilityDropdown) {
        toggleOfficeSelection();
    }
    
    const editVisibilityDropdown = document.getElementById('edit_visibility');
    if (editVisibilityDropdown) {
        toggleEditOfficeSelection();
    }
});

function closeFlashMessage(element) {
    element.parentElement.remove();
}

function searchAnnouncements() {
    const searchInput = document.getElementById('announcementSearch');
    if (searchInput) {
        const searchQuery = searchInput.value.trim();
        if (searchQuery) {
            window.location.href = `${window.location.pathname}?search=${encodeURIComponent(searchQuery)}`;
        }
    }
}