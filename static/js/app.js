// Entry Creation Module
document.addEventListener('DOMContentLoaded', () => {
    initializeEntryCreation();
    initializeSearch();
    loadProjectSuggestions();
});

function initializeEntryCreation() {
    const entryForm = document.getElementById('entryForm');
    
    if (entryForm) {
        entryForm.addEventListener('submit', handleEntrySubmission);
    }
}

async function loadProjectSuggestions() {
    try {
        console.log('Loading project suggestions...');
        const response = await fetch('/api/entries/metadata');
        const data = await response.json();
        
        const projectList = document.getElementById('projectList');
        if (projectList && data.projects) {
            projectList.innerHTML = data.projects
                .map(project => `<option value="${project}">`)
                .join('');
            console.log(`Loaded ${data.projects.length} project suggestions`);
        }
    } catch (error) {
        console.error('Failed to load project suggestions:', error);
    }
}

async function handleEntrySubmission(e) {
    e.preventDefault();
    
    const formData = {
        project: document.getElementById('project').value,
        content: document.getElementById('content').value
    };
    
    console.log('Submitting entry:', formData);

    try {
        const response = await fetch('/api/entries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        console.log('Server response:', data);

        if (response.ok) {
            entryForm.reset();
            showNotification('Entry created successfully!', 'success');
            loadProjectSuggestions(); // Refresh project list after new entry
        } else {
            throw new Error(data.error || 'Failed to create entry');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

// Search Module
function initializeSearch() {
    const searchForm = document.getElementById('searchForm');
    const sortField = document.getElementById('sortField');
    const sortOrder = document.getElementById('sortOrder');
    
    if (searchForm) {
        loadSearchMetadata();
        searchForm.addEventListener('submit', handleSearchSubmission);
        
        // Add listeners for immediate updates
        sortField.addEventListener('change', handleSearchSubmission);
        sortOrder.addEventListener('change', handleSearchSubmission);
        
        // Add listeners to search inputs for real-time filtering
        document.getElementById('dateSearch').addEventListener('change', handleSearchSubmission);
        document.getElementById('projectSearch').addEventListener('input', handleSearchSubmission);
        document.getElementById('developerSearch').addEventListener('input', handleSearchSubmission);
    }
}
async function handleSearchSubmission(e) {
    e.preventDefault();
    const params = new URLSearchParams({
        project: document.getElementById('projectSearch').value || '',
        developer_tag: document.getElementById('developerSearch').value || '',
        date: document.getElementById('dateSearch').value || '',
        sort_field: document.getElementById('sortField').value || 'date',
        sort_order: document.getElementById('sortOrder').value || 'desc'
    });

    try {
        const response = await fetch(`/api/entries/search?${params}`);
        const results = await response.json();
        
        if (!response.ok) {
            throw new Error(results.error);
        }
        
        displaySearchResults(results);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Utility Functions for Search
async function loadSearchMetadata() {
    try {
        const response = await fetch('/api/entries/metadata');
        const metadata = await response.json();
        
        populateDatalist('projectList', metadata.projects);
        populateDatalist('developerList', metadata.developers);
    } catch (error) {
        showNotification('Failed to load search options', 'warning');
    }
}

function populateDatalist(elementId, items) {
    const datalist = document.getElementById(elementId);
    if (!datalist) return;
    
    datalist.innerHTML = '';
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item;
        datalist.appendChild(option);
    });
}

function displaySearchResults(results) {
    const resultsDiv = document.getElementById('searchResults');
    if (!resultsDiv) return;

    if (results.length === 0) {
        resultsDiv.innerHTML = '<div class="alert alert-info">No results found</div>';
        return;
    }

    const resultsList = results.map(entry => `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(entry.project)}</h5>
                <h6 class="card-subtitle mb-2 text-muted">
                    ${new Date(entry.timestamp).toLocaleString()} - ${escapeHtml(entry.developer_tag)}
                </h6>
                <p class="card-text">${escapeHtml(entry.content)}</p>
            </div>
        </div>
    `).join('');

    resultsDiv.innerHTML = resultsList;
}

function showNotification(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}