// Handle resume upload
function setupUploadForm() {
    const uploadForm = document.getElementById('uploadForm');
    if (!uploadForm) return;

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = uploadForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        const fileInput = document.getElementById('resume');
        const messageDiv = document.getElementById('message');
        
        // Clear any previous messages
        messageDiv.innerHTML = '';
        
        // Show loading state
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        submitBtn.disabled = true;
        
        try {
            // Validate file selection
            if (!fileInput.files || fileInput.files.length === 0) {
                throw new Error('Please select a file to upload');
            }
            
            // Validate file size (5MB max)
            if (fileInput.files[0].size > 5 * 1024 * 1024) {
                throw new Error('File size exceeds 5MB limit');
            }
            
            const formData = new FormData();
            formData.append('resume', fileInput.files[0]);
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok || data.error) {
                // Handle different types of errors
                if (response.status === 409 && data.existing_candidate_id) {
                    // Duplicate email error
                    showDuplicateEmailError(messageDiv, data);
                } else {
                    // Other errors
                    showAlert(messageDiv, 'danger', data.error || 'An error occurred while processing the resume');
                }
            } else {
                // Success case
                showSuccessMessage(data);
                uploadForm.reset();
                addRecentUpload(data);
            }
        } catch (error) {
            console.error('Upload error:', error);
            showAlert(messageDiv, 'danger', error.message || 'Failed to process resume. Please try again.');
        } finally {
            // Always reset button state
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
        }
    });
}

// Handle shortlist form
function setupShortlistForm() {
    const shortlistForm = document.getElementById('shortlistForm');
    if (!shortlistForm) return;

    shortlistForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const jobDescription = document.getElementById('jobDescription').value;
        const resultDiv = document.getElementById('shortlistResult');
        const submitBtn = shortlistForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        
        // Clear previous results
        resultDiv.innerHTML = '';
        
        // Show loading state
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        submitBtn.disabled = true;
        
        try {
            if (!jobDescription.trim()) {
                throw new Error('Job description is required');
            }
            
            const response = await fetch('/shortlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `job_description=${encodeURIComponent(jobDescription)}`
            });
            
            const data = await response.json();
            
            if (!response.ok || data.error) {
                showAlert(resultDiv, 'danger', data.error || 'Failed to shortlist candidates');
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        <h4 class="alert-heading">
                            <i class="bi bi-check-circle-fill me-2"></i>Shortlisting Complete!
                        </h4>
                        <p>${data.message}</p>
                        <hr>
                        <div class="d-flex justify-content-between">
                            <button class="btn btn-sm btn-success" onclick="window.location.reload()">
                                <i class="bi bi-arrow-clockwise me-1"></i>Refresh Page
                            </button>
                            <a href="/job_descriptions" class="btn btn-sm btn-outline-success">
                                <i class="bi bi-list-ul me-1"></i>View All Job Descriptions
                            </a>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Shortlist error:', error);
            showAlert(resultDiv, 'danger', error.message || 'Failed to shortlist candidates');
        } finally {
            // Always reset button state
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
        }
    });
}

// Helper functions
function showAlert(container, type, message) {
    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show">
            <strong>${type === 'danger' ? 'Error!' : 'Notice:'}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

function showDuplicateEmailError(container, data) {
    container.innerHTML = `
        <div class="alert alert-warning alert-dismissible fade show">
            <h4 class="alert-heading">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>Duplicate Email Found
            </h4>
            <p><strong>${data.error}</strong></p>
            <p class="mb-0">
                Existing candidate: <strong>${data.existing_candidate_name}</strong>
            </p>
            <hr>
            <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted">Would you like to view the existing candidate instead?</span>
                <div>
                    <a href="/candidate/${data.existing_candidate_id}" class="btn btn-sm btn-warning">
                        <i class="bi bi-person-fill me-1"></i>View Existing Candidate
                    </a>
                    <a href="/candidates" class="btn btn-sm btn-outline-secondary ms-2">
                        <i class="bi bi-people-fill me-1"></i>View All Candidates
                    </a>
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

function showSuccessMessage(data) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show">
            <h4 class="alert-heading">
                <i class="bi bi-check-circle-fill me-2"></i>Success!
            </h4>
            <p>Resume processed successfully for candidate: <strong>${data.full_name || 'Unknown'}</strong></p>
            <p class="mb-0">
                <small class="text-muted">
                    Email: ${data.email || 'N/A'} | Experience: ${data.years_experience || '0'} years
                </small>
            </p>
            <hr>
            <div class="d-flex justify-content-between">
                <a href="/candidate/${data.candidate_id}" class="btn btn-sm btn-success">
                    <i class="bi bi-person-fill me-1"></i>View Candidate Details
                </a>
                <button onclick="location.reload()" class="btn btn-sm btn-outline-success">
                    <i class="bi bi-upload me-1"></i>Upload Another
                </button>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

function addRecentUpload(data) {
    const recentUploads = document.getElementById('recentUploads');
    if (!recentUploads) return;
    
    const noUploadsMsg = recentUploads.querySelector('.text-center');
    
    if (noUploadsMsg) {
        recentUploads.removeChild(noUploadsMsg);
    }
    
    const uploadTime = new Date().toLocaleTimeString();
    
    const uploadItem = document.createElement('a');
    uploadItem.href = `/candidate/${data.candidate_id}`;
    uploadItem.className = 'list-group-item list-group-item-action';
    uploadItem.innerHTML = `
        <div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${data.full_name || 'New Candidate'}</h5>
            <small class="text-success">${uploadTime}</small>
        </div>
        <p class="mb-1">${data.email || 'No email provided'}</p>
        <small class="text-muted">
            <i class="bi bi-briefcase me-1"></i>${data.years_experience || '0'} years experience
        </small>
    `;
    
    recentUploads.insertBefore(uploadItem, recentUploads.firstChild);
    
    // Limit to 5 recent uploads
    const items = recentUploads.querySelectorAll('.list-group-item-action');
    if (items.length > 5) {
        recentUploads.removeChild(items[items.length - 1]);
    }
}

// Delete functionality using data attributes
function setupDeleteButtons() {
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const id = this.dataset.id;
            const name = this.dataset.name;
            
            if (confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`)) {
                deleteItem(type, id, name);
            }
        });
    });
}

async function deleteItem(type, id, name) {
    const url = type === 'shortlist' 
        ? `/shortlist/${id}/delete` 
        : `/${type}/${id}/delete`;
    
    const btn = document.querySelector(`.delete-btn[data-id="${id}"]`);
    const originalBtnText = btn.innerHTML;
    
    try {
        // Show loading state
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
        btn.disabled = true;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success message and refresh the appropriate page
            alert(data.message);
            if (type === 'candidate') {
                window.location.href = '/candidates';
            } else if (type === 'shortlist') {
                window.location.reload(); 
            } else {
                window.location.href = '/job_descriptions';
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Failed to delete. Please try again.');
    } finally {
        btn.innerHTML = originalBtnText;
        btn.disabled = false;
    }
}

// Initialize all event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupUploadForm();
    setupShortlistForm();
    setupDeleteButtons();
});