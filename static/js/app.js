<<<<<<< HEAD
import { Auth } from './auth.js';
import { LogEntry } from './logEntry.js';

if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("/static/js/serviceWorker.js")
      .then((res) => console.log("Service worker registered"))
      .catch((err) => console.log("Service worker not registered", err));
  });
}

document.addEventListener("DOMContentLoaded", async function () {
  const response = await fetch('/api/user');
  if (!response.ok) {
    window.location.href = '/login';
    return;
  }

  const auth = new Auth();
  auth.checkAuthStatus();

  const logEntry = new LogEntry();

  const navLinks = document.querySelectorAll(".nav-link");
  const currentUrl = window.location.pathname;

  navLinks.forEach((link) => {
    if (link.getAttribute("href") === currentUrl) {
      link.classList.add("active");
    }
  });

  document.getElementById('newEntryNav').addEventListener('click', () => {
    logEntry.setupUI();
  });

  document.getElementById('searchNav').addEventListener('click', () => {
    logEntry.setupSearchUI();
  });
});

// this basically checks if the service worker is supported by the browser
=======

document.addEventListener('DOMContentLoaded', () => {
    // api/entries
    initializeEntryCreation();
    loadProjectSuggestions();
    // api/search
    initializeSearch();
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

// front-end stuff for entries and search, just dont touch
// handles form submission and exceptions
async function handleEntrySubmission(e) {
    e.preventDefault();
    
    const formData = {
        project: document.getElementById('project').value,
        content: document.getElementById('content').value
    };
    
    // validates form data
    if (!formData.project || !formData.content) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    // sends to api
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

        // shows success/error message
        if (response.ok) {
            entryForm.reset();
            showNotification('Entry created successfully!', 'success');
            loadProjectSuggestions();
        } else {
            throw new Error(data.error || 'Failed to create entry');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// search handling - talks to /api/search
async function handleSearchSubmission(e) {
    e.preventDefault();

    // builds search params
    const params = new URLSearchParams({
        project: document.getElementById('projectSearch').value || '',
        developer_tag: document.getElementById('developerSearch').value || '',
        date: document.getElementById('dateSearch').value || '',
        sort_field: document.getElementById('sortField').value || 'date',
        sort_order: document.getElementById('sortOrder').value || 'desc'
    });

    // gets results from api
    try {
        const response = await fetch(`/api/entries/search?${params}`);
        const results = await response.json();
        
        if (!response.ok) {
            throw new Error(results.error);
        }
        
        // updates results display
        displaySearchResults(results);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// search utils 
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
>>>>>>> fork/main
