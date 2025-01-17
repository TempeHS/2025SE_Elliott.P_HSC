document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll(".nav-link");
    const currentUrl = window.location.pathname;

    navLinks.forEach((link) => {
        const linkUrl = link.getAttribute("href");
        if (linkUrl === currentUrl) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });

    // Initialize Auth class
    new Auth();

    // Handle diary entry form submission
    const entryForm = document.getElementById('entryForm');
    if (entryForm) {
        entryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(entryForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/api/entries', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(data),
                    credentials: 'same-origin'
                });

                const result = await response.json();
                if (response.ok) {
                    alert('Entry created successfully');
                    // Optionally, redirect or update the UI
                } else {
                    alert(result.error || 'Failed to create entry');
                }
            } catch (error) {
                alert('Failed to create entry. Please try again.');
            }
        });
    }
});

// Search functionality
if (document.getElementById('searchForm')) {
    document.getElementById('searchForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const date = document.getElementById('dateSearch').value;
        const project = document.getElementById('projectSearch').value;
        const content = document.getElementById('contentSearch').value;
        
        const params = new URLSearchParams();
        if (date) params.append('date', date);
        if (project) params.append('project', project);
        if (content) params.append('content', content);
        
        try {
            const response = await fetch(`/api/entries/search?${params.toString()}`);
            const results = await response.json();
            
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '';
            
            if (results.length === 0) {
                resultsDiv.innerHTML = '<div class="alert alert-info">No results found</div>';
                return;
            }
            
            const resultsList = results.map(entry => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${entry.project}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">
                            ${new Date(entry.timestamp).toLocaleString()} - ${entry.developer}
                        </h6>
                        <p class="card-text">${entry.content}</p>
                    </div>
                </div>
            `).join('');
            
            resultsDiv.innerHTML = resultsList;
        } catch (error) {
            console.error('Search failed:', error);
            document.getElementById('searchResults').innerHTML = 
                '<div class="alert alert-danger">Search failed. Please try again.</div>';
        }
    });
}
