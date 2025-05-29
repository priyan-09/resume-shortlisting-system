// Handle resume upload
function setupUploadForm() {
    const uploadForm = document.getElementById('uploadForm');
    if (!uploadForm) return;

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = uploadForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        submitBtn.disabled = true;
        
        const formData = new FormData();
        const fileInput = document.getElementById('resume');
        const messageDiv = document.getElementById('message');
        
        try {
            // Validate file size (5MB max)
            if (fileInput.files[0].size > 5 * 1024 * 1024) {
                throw new Error('File size exceeds 5MB limit');
            }
            
            formData.append('resume', fileInput.files[0]);
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                // Handle duplicate email error specially
                if (response.status === 409 && data.existing_candidate_id) {
                    showDuplicateEmailError(messageDiv, data);
                } else {
                    showAlert(messageDiv, 'danger', data.error);
                }
            } else {
                showSuccessMessage(data);
                uploadForm.reset();
                addRecentUpload(data);
            }
        } catch (error) {
            showAlert(messageDiv, 'danger', error.message || 'Failed to process resume');
        } finally {
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
            
            if (data.error) {
                showAlert(resultDiv, 'danger', data.error);
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        ${data.message}
                        <button class="btn btn-sm btn-success ms-2" onclick="window.location.reload()">Refresh</button>
                    </div>
                `;
            }
        } catch (error) {
            showAlert(resultDiv, 'danger', error.message || 'Failed to shortlist candidates');
        }
    });
}

// Helper functions
function showAlert(container, type, message) {
    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
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
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
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
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
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

// Initialize all event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupUploadForm();
    setupShortlistForm();
});