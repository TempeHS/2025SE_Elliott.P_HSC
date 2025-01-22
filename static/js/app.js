document.addEventListener('DOMContentLoaded', () => {
    initializeEntryCreation();
    loadProjectSuggestions();
    initializeSearch();
});

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showNotification(message, type) {
    console.log(`${type}: ${message}`);
}

function initializeSearch() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        loadSearchMetadata();
        searchForm.addEventListener('submit', handleSearchSubmission);
    }
}

async function loadSearchMetadata() {
    try {
        const response = await fetch('/api/entries/metadata');
        const data = await response.json();
        
        if (data.projects) {
            const projectList = document.getElementById('projectList');
            if (projectList) {
                projectList.innerHTML = data.projects
                    .map(project => `<option value="${project}">`)
                    .join('');
            }
        }
        
        if (data.developers) {
            const developerList = document.getElementById('developerList');
            if (developerList) {
                developerList.innerHTML = data.developers
                    .map(dev => `<option value="${dev}">`)
                    .join('');
            }
        }
    } catch (error) {
        console.error('Failed to load metadata:', error);
    }
}

async function handleSearchSubmission(e) {
    e.preventDefault();
    console.log('Search form submitted');
    
    const searchParams = new URLSearchParams({
        project: document.getElementById('projectSearch')?.value || '',
        developer_tag: document.getElementById('developerSearch')?.value || '',
        date: document.getElementById('dateSearch')?.value || '',
        sort_field: 'date',
        sort_order: 'desc'
    });

    try {
        const response = await fetch(`/api/entries/search?${searchParams}`);
        const results = await response.json();
        console.log('Search results:', results);
        
        displaySearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
        showNotification(error.message, 'error');
    }
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    console.log('Displaying results in container:', resultsContainer);
    
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }

    if (!results || results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info">
                No matching entries found
            </div>`;
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

    console.log('Rendering results HTML');
    resultsContainer.innerHTML = resultsList;
}

function initializeEntryCreation() {
    const entryForm = document.getElementById('entryForm');
    if (entryForm) {
        entryForm.addEventListener('submit', handleEntrySubmission);
    }
}

async function loadProjectSuggestions() {
    try {
        const response = await fetch('/api/entries/metadata');
        const data = await response.json();
        
        const projectList = document.getElementById('projectList');
        if (projectList && data.projects) {
            projectList.innerHTML = data.projects
                .map(project => `<option value="${project}">`)
                .join('');
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

        if (response.ok) {
            document.getElementById('entryForm').reset();
            showNotification('Entry created successfully!', 'success');
            loadProjectSuggestions();
        } else {
            throw new Error(data.error || 'Failed to create entry');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}
