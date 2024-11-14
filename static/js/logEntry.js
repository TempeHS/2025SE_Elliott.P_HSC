export class LogEntry {
    constructor() {
        this.setupUI();
        this.bindEvents();
    }

    setupUI() {
        const logEntriesDiv = document.getElementById('logEntries');
        logEntriesDiv.innerHTML = `
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">New Log Entry</h5>
                            <form id="newEntryForm">
                                <div class="mb-3">
                                    <label for="project" class="form-label">Project</label>
                                    <input type="text" class="form-control" id="project" required pattern="^[a-zA-Z0-9-_]+$">
                                </div>
                                <div class="mb-3">
                                    <label for="content" class="form-label">Log Content</label>
                                    <textarea class="form-control" id="content" rows="3" required maxlength="1000"></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">Submit Entry</button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Search Entries</h5>
                            <div class="row g-3">
                                <div class="col-md-3">
                                    <input type="date" class="form-control" id="searchDate">
                                </div>
                                <div class="col-md-3">
                                    <input type="text" class="form-control" id="searchProject" placeholder="Project">
                                </div>
                                <div class="col-md-4">
                                    <input type="text" class="form-control" id="searchContent" placeholder="Search content">
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-secondary w-100" id="searchButton">Search</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12 mt-4">
                    <div id="entriesList"></div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.getElementById('newEntryForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createEntry();
        });

        document.getElementById('searchButton').addEventListener('click', () => {
            this.searchEntries();
        });
    }

    async createEntry() {
        const project = document.getElementById('project').value;
        const content = document.getElementById('content').value;
        const timestamp = new Date().toISOString();

        try {
            const response = await fetch('/api/entries', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ project, content, timestamp })
            });

            if (response.ok) {
                document.getElementById('newEntryForm').reset();
                this.displayEntries(await response.json());
            }
        } catch (error) {
            console.error('Error creating entry:', error);
        }
    }

    async searchEntries() {
        const date = document.getElementById('searchDate').value;
        const project = document.getElementById('searchProject').value;
        const content = document.getElementById('searchContent').value;

        const params = new URLSearchParams();
        if (date) params.append('date', date);
        if (project) params.append('project', project);
        if (content) params.append('content', content);

        try {
            const response = await fetch(`/api/entries/search?${params}`);
            if (response.ok) {
                this.displayEntries(await response.json());
            }
        } catch (error) {
            console.error('Error searching entries:', error);
        }
    }

    displayEntries(entries) {
        const entriesList = document.getElementById('entriesList');
        entriesList.innerHTML = entries.map(entry => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-subtitle mb-2 text-muted">
                        Project: ${entry.project} | Date: ${new Date(entry.timestamp).toLocaleString()}
                    </h6>
                    <p class="card-text">${entry.content}</p>
                </div>
            </div>
        `).join('');
    }
}
