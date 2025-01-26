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
        this.bindSearchEvents();
    }

    bindSearchEvents() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSearch(e));
        }
    }

    async handleSearch(e) {
        e.preventDefault();
        const params = new URLSearchParams({
            project: document.getElementById('projectSearch').value,
            developer_tag: document.getElementById('developerSearch').value,
            date: document.getElementById('dateSearch').value
        });

        try {
            const response = await fetch(`/api/entries/search?${params}`);
            const data = await response.json();
            if (response.ok) {
                this.displayResults(data);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }

    displayResults(entries) {
        if (!entries.length) {
            this.resultsContainer.innerHTML = '<div class="alert alert-info">no entries found</div>';
            return;
        }
        this.resultsContainer.innerHTML = entries.map(entry => createEntryCard(entry)).join('');
    }
}


class HomeManager {
    constructor() {
        this.loadProjectData();
    }

    async loadProjectData() {
        try {
            const response = await fetch('/api/entries/user-stats');
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error);
            
            // group entries by project
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
                <div class="card project-card">
                    <div class="card-body">
                        <h5 class="card-title">${escapeHtml(project)}</h5>
                        <div class="project-entries collapsed">
                            ${entries.slice(0, 3).map(entry => this.createEntryPreview(entry)).join('')}
                        </div>
                        ${entries.length > 3 ? `
                            <button class="btn btn-outline-primary expand-button" 
                                    onclick="event.stopPropagation(); this.closest('.project-card').querySelector('.project-entries').classList.toggle('collapsed')">
                                Show ${entries.length - 3} more entries
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        // click handlers
        document.querySelectorAll('.project-card').forEach(card => {
            card.addEventListener('click', () => {
                card.querySelector('.project-entries').classList.toggle('collapsed');
            });
        });
    }

    createEntryPreview(entry) {
        return `
            <div class="entry-preview mb-3">
                <small class="text-muted">${new Date(entry.timestamp).toLocaleDateString()}</small>
                <p class="mb-1">${escapeHtml(clipContent(entry.content, 2))}</p>
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
        // only run on the profile page (!!!!)
        if (window.location.pathname === '/profile') {
            this.loadProfileData();
            this.bindLogoutEvent();
            this.bindTwoFAEvents();
        }
    }

    async loadProfileData() {
        try {
            const response = await fetch('/api/entries/user-stats');
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error);
            
            document.querySelector('.developer-tag').textContent = data.developer_tag;
            document.querySelector('.email-display').textContent = data.email;
            
            // Set 2FA toggle state
            const twoFAToggle = document.getElementById('twoFAToggle');
            if (twoFAToggle) {
                twoFAToggle.checked = data.two_fa_enabled;
            }
            
            const entriesContainer = document.getElementById('userEntries');
            if (entriesContainer) {
                entriesContainer.innerHTML = data.entries.map(entry => createEntryCard(entry)).join('');
            }
        } catch (error) {
            showNotification('failed to load profile', 'error');
        }
    }


    bindLogoutEvent() {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/auth/logout', {
                        method: 'POST',
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });
                    if (response.ok) {
                        window.location.href = '/login';
                    }
                } catch (error) {
                    showNotification('logout failed', 'error');
                }
            });
        }
    }

    bindTwoFAEvents() {
        const toggle = document.getElementById('twoFAToggle');
        toggle.addEventListener('change', async () => {
            if (toggle.checked) {
                const response = await fetch('/api/auth/enable-2fa', {
                    method: 'POST',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    }
                });
                if (response.ok) {
                    document.getElementById('verificationSection').style.display = 'block';
                    showNotification('verification code sent to your email', 'success');
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
                    showNotification('2FA disabled successfully', 'success');
                }
            }
        });

        document.getElementById('verifyCode').addEventListener('click', async () => {
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
                showNotification('2FA enabled successfully', 'success');
                document.getElementById('verificationSection').style.display = 'none';
            }
        });
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
        <div class="card mb-3 entry-card" onclick="window.location.href='/entry/${entry.id}'">
            <div class="card-body">
                <h5 class="card-title text-truncate">${escapeHtml(entry.project)}</h5>
                <h6 class="card-subtitle mb-2 text-muted">
                    ${new Date(entry.timestamp).toLocaleString()} - ${escapeHtml(entry.developer_tag)}
                </h6>
                <p class="card-text">${escapeHtml(clipContent(entry.content))}</p>
                <div class="entry-details">
                    <small class="text-muted">
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
    new EntryManager();
    new SearchManager();
    new HomeManager();
    new EntryViewer();
    new PrivacyManager();
    new ProfileManager();
});
