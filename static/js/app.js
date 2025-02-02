// core app functionality classes and utilities
class EntryManager {
    constructor() {
        this.form = document.getElementById('entryForm');
        this.projectList = document.getElementById('projectList');
        this.bindEvents();
        this.loadProjectSuggestions();
    }

    bindEvents() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            this.form.querySelectorAll('input, textarea').forEach(input => {
                input.addEventListener('input', () => this.validateField(input));
            });
        }
    }

    validateField(input) {
        const isValid = input.checkValidity();
        input.classList.toggle('is-valid', isValid);
        input.classList.toggle('is-invalid', !isValid);
        return isValid;
    }

    async handleSubmit(e) {
        e.preventDefault();
        const formData = {
            project: this.form.querySelector('#project').value,
            content: this.form.querySelector('#content').value,
            repository_url: this.form.querySelector('#repository_url').value,
            start_time: this.form.querySelector('#start_time').value,
            end_time: this.form.querySelector('#end_time').value
        };

        console.log("Submitting form data:", formData); // Add this to verify data

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
                // clear form and validation states
                this.form.reset();
                this.form.querySelectorAll('input, textarea').forEach(input => {
                    input.classList.remove('is-valid', 'is-invalid');
                });
                showNotification('entry created', 'success');
                this.loadProjectSuggestions();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }


    async loadProjectSuggestions() {
        if (this.projectList) {
            try {
                const response = await fetch('/api/entries/metadata');
                const data = await response.json();
                if (data.projects) {
                    this.projectList.innerHTML = data.projects
                        .map(project => `<option value="${escapeHtml(project)}">`)
                        .join('');
                }
            } catch (error) {
                console.error('failed to load projects:', error);
            }
        }
    }
}

class SearchManager {
    constructor() {
        this.form = document.getElementById('searchForm');
        this.resultsContainer = document.getElementById('searchResults');
        this.bindEvents();
        this.loadMetadata();
        this.debounceTimer = null;
    }

    async loadMetadata() {
        const response = await fetch('/api/entries/metadata');
        const data = await response.json();
        this.populateDatalist('projectList', data.projects);
        this.populateDatalist('developerList', data.developers);
    }

    populateDatalist(id, items) {
        const datalist = document.getElementById(id);
        datalist.innerHTML = items.map(item => `<option value="${item}">`).join('');
    }

    bindEvents() {
        const filterElements = [
            'projectSearch',
            'developerSearch',
            'dateSearch',
            'sortField',
            'sortOrder'
        ];

        filterElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.addEventListener('change', () => this.handleSearch());
                if (['projectSearch', 'developerSearch'].includes(elementId)) {
                    element.addEventListener('input', () => this.debounceSearch());
                }
            }
        });
    }

    debounceSearch() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.handleSearch(), 300);
    }

    async handleSearch() {
        const params = new URLSearchParams();
        
        const filters = {
            project: document.getElementById('projectSearch')?.value,
            developer_tag: document.getElementById('developerSearch')?.value,
            date: document.getElementById('dateSearch')?.value,
            sort_field: document.getElementById('sortField')?.value,
            sort_order: document.getElementById('sortOrder')?.value
        };

        Object.entries(filters).forEach(([key, value]) => {
            if (value) params.append(key, value);
        });

        try {
            const response = await fetch(`/api/entries/search?${params}`);
            if (!response.ok) throw new Error('Search failed');
            
            const entries = await response.json();
            this.displayResults(entries);
        } catch (error) {
            this.showError('Failed to fetch search results');
        }
    }

    displayResults(entries) {
        if (!this.resultsContainer) return;

        if (entries.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="card mb-3">
                    <div class="card-body">
                        <p class="text-center">No entries found</p>
                    </div>
                </div>`;
            return;
        }

        this.resultsContainer.innerHTML = entries.map(entry => `
            <div class="card mb-3 entry-preview">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="card-title project-name">${entry.project}</h5>
                        <small class="text-muted">${new Date(entry.timestamp).toLocaleString()}</small>
                    </div>
                    <h6 class="card-subtitle mb-2 developer-tag">${entry.developer_tag}</h6>
                    <p class="card-text">${entry.content}</p>
                    ${entry.repository_url ? `
                        <a href="${entry.repository_url}" target="_blank" class="btn btn-sm btn-primary">
                            View Repository
                        </a>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    showError(message) {
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${message}
                </div>`;
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('searchForm')) {
        new SearchManager();
    }
});

class HomeManager {
    constructor() {
        this.loadProjectData();
    }

    async loadProjectData() {
        try {
            const response = await fetch('/api/entries/user-stats');
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error);
            
            // Update stats display
            document.getElementById('projectCount').textContent = data.project_count;
            document.getElementById('entryCount').textContent = data.entry_count;
            document.getElementById('devTag').textContent = data.developer_tag;
            
            // Group entries by project
            const projectGroups = this.groupEntriesByProject(data.entries);
            this.displayProjectCards(projectGroups);
        } catch (error) {
            showNotification('Failed to load projects', 'error');
        }
    }

    groupEntriesByProject(entries) {
        return entries.reduce((groups, entry) => {
            if (!groups[entry.project]) {
                groups[entry.project] = [];
            }
            groups[entry.project].push(entry);
            return groups;
        }, {});
    }

    displayProjectCards(projectGroups) {
        const container = document.getElementById('projectCards');
        if (!container) return;

        container.innerHTML = Object.entries(projectGroups).map(([project, entries]) => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${escapeHtml(project)}</h5>
                        <div class="project-entries">
                            ${entries.slice(0, 3).map(entry => this.createEntryPreview(entry)).join('')}
                            ${entries.length > 3 ? `
                                <button class="btn btn-outline-primary mt-2" 
                                        onclick="event.stopPropagation(); this.closest('.project-entries').classList.toggle('collapsed')">
                                    Show ${entries.length - 3} more entries
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    createEntryPreview(entry) {
        return `
            <div class="entry-preview mb-3">
                <small>${new Date(entry.timestamp).toLocaleDateString()}</small>
                <p class="mb-1">${escapeHtml(clipContent(entry.content, 10))}</p>
                <a href="/entry/${entry.id}" class="stretched-link"></a>
            </div>
        `;
    }
}


class EntryViewer {
    constructor() {
        if (window.location.pathname.startsWith('/entry/')) {
            this.loadEntry(window.location.pathname.split('/').pop());
        }
    }

    async loadEntry(entryId) {
        try {
            const response = await fetch(`/api/entries/${entryId}`);
            const entry = await response.json();
            
            if (!response.ok) throw new Error(entry.error);
            
            this.displayEntry(entry);
        } catch (error) {
            showNotification('failed to load entry', 'error');
        }
    }

    displayEntry(entry) {
        const elements = {
            '.entry-title': entry.project,
            '.entry-metadata': `${new Date(entry.timestamp).toLocaleString()} - ${entry.developer_tag}`,
            '.entry-content': entry.content,
            '.entry-time-worked': `Time worked: ${entry.time_worked} minutes`,
            '.entry-start-time': `Start: ${new Date(entry.start_time).toLocaleString()}`,
            '.entry-end-time': `End: ${new Date(entry.end_time).toLocaleString()}`,
            '.entry-repository': entry.repository_url ? `Repository: <a href="${escapeHtml(entry.repository_url)}" target="_blank">${escapeHtml(entry.repository_url)}</a>` : ''
        };

        Object.entries(elements).forEach(([selector, value]) => {
            const element = document.querySelector(selector);
            if (element) element.innerHTML = value;
        });
    }
}

class PrivacyManager {
    constructor() {
        this.bindPrivacyEvents();
    }

    bindPrivacyEvents() {
        const downloadBtn = document.getElementById('downloadData');
        const deleteBtn = document.getElementById('deleteAccount');

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.handleDownload());
        }
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.handleDelete());
        }
    }

    async handleDownload() {
        try {
            const response = await fetch('/api/user/data');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'my_devlog_data.json';
            a.click();
        } catch (error) {
            showNotification('failed to download data', 'error');
        }
    }

    async handleDelete() {
        if (confirm('are you sure? this action cannot be undone')) {
            try {
                const response = await fetch('/api/user/data', {
                    method: 'DELETE',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    }
                });
                if (response.ok) {
                    window.location.href = '/login';
                }
            } catch (error) {
                showNotification('failed to delete account', 'error');
            }
        }
    }
}

class ProfileManager {
    constructor() {
        this.bindApiKeyEvents();
        this.loadProfileData();
        this.bind2FAEvents();
    }

    initializeErrorHandling() {
        this.errorContainer = document.createElement('div');
        this.errorContainer.className = 'alert alert-danger';
        document.querySelector('.container').prepend(this.errorContainer);
    }

    showNotification(message, type = 'danger') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} fade show`;
        notification.textContent = message;
        document.querySelector('.container').prepend(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    logError(error, context) {
        console.error(`Error in ${context}:`, error);
        this.showNotification(`${context}: ${error.message}`);
    }

    bindApiKeyEvents() {
        document.getElementById('generateApiKey')?.addEventListener('click', () => this.handleGenerateKey());
        document.getElementById('regenerateApiKey')?.addEventListener('click', () => this.handleRegenerateKey());
    }

    bind2FAEvents() {
        const toggle = document.getElementById('twoFactorToggle');
        if (toggle) {
            toggle.addEventListener('change', async (e) => {
                if (e.target.checked) {
                    const response = await fetch('/api/auth/enable-2fa', {
                        method: 'POST',
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });
                    if (response.ok) {
                        document.getElementById('verificationSection').style.display = 'block';
                        this.showNotification('Verification code sent to your email', 'success');
                    }
                } else {
                    const response = await fetch('/api/auth/disable-2fa', {
                        method: 'POST',
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });
                    if (response.ok) {
                        document.getElementById('verificationSection').style.display = 'none';
                        this.showNotification('2FA disabled successfully', 'success');
                    }
                }
            });
        }

        document.getElementById('verifyCode')?.addEventListener('click', async () => {
            const code = document.getElementById('verificationCode').value;
            const response = await fetch('/api/auth/verify-2fa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ code })
            });
            if (response.ok) {
                document.getElementById('verificationSection').style.display = 'none';
                this.showNotification('2FA enabled successfully', 'success');
            }
        });
    }

    async handleGenerateKey() {
        try {
            const response = await fetch('/api/user/generate-key', {
                method: 'POST',
                headers: {
                    'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            
            if (response.ok) {
                this.showNotification('API key generated successfully', 'success');
                location.reload();
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Failed to generate API key');
            }
        } catch (error) {
            this.logError(error, 'API Key Generation');
        }
    }

    async handleRegenerateKey() {
        if (confirm('Are you sure? Current API key will be invalidated.')) {
            await this.handleGenerateKey();
        }
    }

    async loadProfileData() {
        try {
            const response = await fetch('/api/entries/user-stats');
            const data = await response.json();
            
            const projectCount = document.getElementById('projectCount');
            const entryCount = document.getElementById('entryCount');
            
            if (projectCount) projectCount.textContent = data.project_count;
            if (entryCount) entryCount.textContent = data.entry_count;
            
            this.displayRecentEntries(data.entries);
            
        } catch (error) {
            this.logError(error, 'Profile Data Loading');
        }
    }

    displayRecentEntries(entries) {
        const recentEntries = document.getElementById('recentEntries');
        if (!recentEntries) return;

        if (!entries?.length) {
            recentEntries.innerHTML = '<p>No entries yet</p>';
            return;
        }

        recentEntries.innerHTML = entries.map(entry => `
            <div class="card mb-3 entry-preview">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="card-title project-name">${entry.project}</h5>
                        <small class="text-muted">${new Date(entry.timestamp).toLocaleString()}</small>
                    </div>
                    <p class="card-text">${entry.content}</p>
                    ${entry.repository_url ? `
                        <a href="${entry.repository_url}" target="_blank" class="btn btn-sm btn-primary">
                            View Repository
                        </a>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
}

// utility functions
function escapeHtml(unsafe) { // prevents xss in dynamic stuff
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showNotification(message, type) {
    // create alert div
    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // insert at top of page
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);

    // auto remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}

function clipContent(content, maxLines = 3) {
    const lines = content.split('\n');
    return lines.length > maxLines ? lines.slice(0, maxLines).join('\n') + '...' : content;
}

function createEntryCard(entry) {
    return `
        <div class="card mb-3 entry-card">
            <div class="card-body">
                <h5 class="card-title text-truncate">${escapeHtml(entry.project)}</h5>
                <h6 class="card-subtitle mb-2">
                    ${new Date(entry.timestamp).toLocaleString()} - ${escapeHtml(entry.developer_tag)}
                </h6>
                <p class="card-text">${escapeHtml(clipContent(entry.content))}</p>
                <div class="entry-details">
                    <small>
                        <div>time worked: ${entry.time_worked} minutes</div>
                        <div>start: ${new Date(entry.start_time).toLocaleString()}</div>
                        <div>end: ${new Date(entry.end_time).toLocaleString()}</div>
                        ${entry.repository_url ? `<div><a href="${escapeHtml(entry.repository_url)}" target="_blank">repository</a></div>` : ''}
                    </small>
                </div>
            </div>
        </div>
    `;
}




// initialize all managers on dom load
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize managers if their respective elements exist
    if (document.getElementById('entryForm')) {
        new EntryManager();
    }
    if (document.getElementById('searchForm')) {
        new SearchManager();
    }
    if (window.location.pathname === '/home') {
        new HomeManager();
    }
    if (window.location.pathname.startsWith('/entry/')) {
        new EntryViewer();
    }
    if (window.location.pathname === '/privacy') {
        new PrivacyManager();
    }
    if (window.location.pathname === '/profile') {
        new ProfileManager();
    }
    if (document.getElementById('apiKeySection')) {
        new ProfileManager();
    }
});
