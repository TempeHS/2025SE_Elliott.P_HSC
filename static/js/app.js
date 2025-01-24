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
                this.form.reset();
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
        this.loadUserStats();
    }

    async loadUserStats() {
        try {
            const response = await fetch('/api/entries/user-stats');
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error);
            
            this.updateStats(data);
            this.displayUserEntries(data.entries);
        } catch (error) {
            console.error('stats load failed:', error);
        }
    }

    updateStats(data) {
        const elements = {
            '.developer-tag': data.developer_tag,
            '.project-count': `${data.project_count} projects`,
            '.entry-count': `${data.entry_count} entries`
        };

        Object.entries(elements).forEach(([selector, value]) => {
            const element = document.querySelector(selector);
            if (element) element.textContent = value;
        });
    }

    displayUserEntries(entries) {
        const container = document.getElementById('userEntries');
        if (container) {
            container.innerHTML = entries.map(entry => createEntryCard(entry)).join('');
        }
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

// utility functions
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
});
