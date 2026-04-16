let isDeleteMode = false;
let selectedForDeletion = new Set();

document.addEventListener('DOMContentLoaded', () => {
    fetchSources();
    fetchLatestReport();
    
    document.getElementById('generate-btn').addEventListener('click', generateIntelligence);
    
    // Modal Close Logic
    document.getElementById('modal-close').addEventListener('click', () => {
        document.getElementById('source-modal').style.display = 'none';
    });
    document.getElementById('source-modal').addEventListener('click', (e) => {
        if (e.target.id === 'source-modal') {
            document.getElementById('source-modal').style.display = 'none';
        }
    });

    // Bulk Delete Handlers
    const toggleTrash = document.getElementById('toggle-trash-btn');
    const deleteBar = document.getElementById('delete-actions-bar');
    const confirmBtn = document.getElementById('confirm-delete-btn');
    const cancelBtn = document.getElementById('cancel-delete-btn');
    
    function exitDeleteMode() {
        isDeleteMode = false;
        selectedForDeletion.clear();
        deleteBar.style.display = 'none';
        toggleTrash.classList.remove('active');
        document.querySelectorAll('.source-card.selected-for-deletion').forEach(c => c.classList.remove('selected-for-deletion'));
    }

    toggleTrash.addEventListener('click', () => {
        isDeleteMode = !isDeleteMode;
        if (isDeleteMode) {
            deleteBar.style.display = 'flex';
            toggleTrash.classList.add('active');
            document.getElementById('delete-count-text').innerText = `0 selected`;
            selectedForDeletion.clear();
        } else {
            exitDeleteMode();
        }
    });

    cancelBtn.addEventListener('click', exitDeleteMode);

    confirmBtn.addEventListener('click', async () => {
        if (selectedForDeletion.size === 0) return;
        if (!confirm(`Permanently delete ${selectedForDeletion.size} notes?`)) return;
        
        // Update UX so they know it is actively deleting
        confirmBtn.innerText = "Deleting...";
        
        try {
            const response = await fetch('/api/sources/bulk-delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ source_ids: Array.from(selectedForDeletion) })
            });
            if (response.ok) {
                exitDeleteMode();
                fetchSources();
            } else {
                alert("Failed to delete.");
            }
        } catch(e) { console.error(e); } finally {
            confirmBtn.innerText = "Delete";
        }
    });
});

async function fetchSources() {
    const listContainer = document.getElementById('sources-list');
    const sourceCountBadge = document.getElementById('source-count');

    try {
        const response = await fetch('/api/sources');
        const data = await response.json();

        // Clear loading state
        listContainer.innerHTML = '';

        if (data.length === 0) {
            listContainer.innerHTML = '<div class="loading-state">No sources found.<br>Use your Chrome Extension to sync some!</div>';
            return;
        }

        // Update badge
        sourceCountBadge.innerText = `${data.length} Note(s)`;

        // Render each source as a card
        data.forEach(source => {
            const card = document.createElement('div');
            card.className = 'source-card';
            
            // Format the date
            const date = new Date(source.timestamp).toLocaleDateString(undefined, { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            // Extract host name from URL if possible
            let sourceHost = "Gemini";
            try {
                if(source.source_url) {
                    sourceHost = new URL(source.source_url).hostname;
                }
            } catch (e) {
                // Ignore parse errors
            }

            // Safely strip HTML to get plaintext for titles and previews
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = source.content;
            const plainText = tempDiv.innerText || tempDiv.textContent || "";
            
            // Extract a smart title from the first sentence or line
            let smartTitle = plainText.split(/[.\n]/)[0].replace(/[*_#>]/g, '').trim();
            if (smartTitle.length > 55) smartTitle = smartTitle.substring(0, 55) + "...";
            if (smartTitle.length < 3) smartTitle = "Synced Note";

            card.innerHTML = `
                <div class="source-title">${escapeHTML(smartTitle)}</div>
                <div class="source-time">${sourceHost} &bull; ${date}</div>
                <div class="source-preview">${escapeHTML(plainText)}</div>
            `;
            
            // Reapply selection state visually if the socket refreshes during a selection
            if (isDeleteMode && selectedForDeletion.has(source.id)) {
                card.classList.add('selected-for-deletion');
            }
            
            // Click to interact
            card.addEventListener('click', (e) => {
                // Intercept for deletion tracking
                if (isDeleteMode) {
                    if (selectedForDeletion.has(source.id)) {
                        selectedForDeletion.delete(source.id);
                        card.classList.remove('selected-for-deletion');
                    } else {
                        selectedForDeletion.add(source.id);
                        card.classList.add('selected-for-deletion');
                    }
                    document.getElementById('delete-count-text').innerText = `${selectedForDeletion.size} selected`;
                    return;
                }
                
                // Normal click: open modal
                document.getElementById('modal-title').innerText = sourceHost + ' Insight';
                // Because we captured the raw innerHTML straight from Gemini, we inject it directly
                // (This matches the exact formatting, headers, bolding, and codeblocks)
                document.getElementById('modal-body-text').innerHTML = source.content;
                document.getElementById('source-modal').style.display = 'flex';
            });
            
            listContainer.appendChild(card);
        });

    } catch (error) {
        console.error('Error fetching sources:', error);
        listContainer.innerHTML = '<div class="loading-state" style="color: #ef4444;">Failed to load sources. Is the backend running?</div>';
    }
}

// Basic HTML escaping wrapper
function escapeHTML(str) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(str));
    return p.innerHTML;
}

// ---------------------------------------------------------
// WebSocket Real-time Updating
// ---------------------------------------------------------
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function(event) {
    if (event.data === "new_source") {
        console.log("Real-time update received! Refreshing sources...");
        fetchSources(); // Re-render the sidebar
    } else if (event.data === "new_report") {
        console.log("New report broadcast received.");
        fetchLatestReport();
    }
};

ws.onclose = function(event) {
    console.log("WebSocket connection closed.");
};

// Fallback polling
setInterval(() => {
    fetchSources();
}, 3000);

// ---------------------------------------------------------
// Phase 4 Intelligence Rendering
// ---------------------------------------------------------
async function fetchLatestReport() {
    try {
        const response = await fetch('/api/reports/latest');
        if (response.ok) {
            const data = await response.json();
            if (data) {
                renderDashboard(data);
            }
        }
    } catch (e) { console.error("Error fetching report", e); }
}

async function generateIntelligence() {
    const btn = document.getElementById('generate-btn');
    const tool = document.getElementById('vibe-tool').value;
    
    btn.disabled = true;
    btn.querySelector('span').innerText = 'Generating (Takes 10-30s)...';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ target_platform: tool })
        });
        
        if (!response.ok) {
            const err = await response.json();
            alert("Analysis failed: " + (err.detail || "Server Error"));
            return;
        }
        
        const data = await response.json();
        renderDashboard(data);
        
    } catch (e) {
        alert("Request error: " + e.message);
    } finally {
        btn.disabled = false;
        btn.querySelector('span').innerText = 'Generate Intelligence';
    }
}

function renderDashboard(data) {
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('analysis-dashboard').style.display = 'flex';
    
    // Viability Score Coloring
    const badge = document.getElementById('score-badge');
    badge.innerText = `${data.viability_score}/100`;
    if (data.viability_score > 80) badge.style.color = '#34d399';
    else if (data.viability_score > 50) badge.style.color = '#fbbf24';
    else badge.style.color = '#f87171';
    
    document.getElementById('rep-summary').innerHTML = escapeHTML(data.summary);
    document.getElementById('rep-market').innerHTML = escapeHTML(data.market_analysis);
    document.getElementById('rep-cost').innerHTML = escapeHTML(data.cost_benefit);
    document.getElementById('rep-swot').innerHTML = escapeHTML(data.swot);
    
    const timeline = document.getElementById('rep-timeline');
    timeline.innerHTML = '';
    
    if (data.vibe_coding_pipeline) {
        data.vibe_coding_pipeline.forEach((step, idx) => {
            const el = document.createElement('div');
            el.className = 'timeline-step';
            el.innerHTML = `
                <h4>Step ${idx + 1}</h4>
                <div class="step-prompt">${escapeHTML(step.prompt_text)}</div>
                <div class="step-why"><strong>Why:</strong> ${escapeHTML(step.why)}</div>
                <div class="step-expect"><strong>Expectation:</strong> ${escapeHTML(step.expectation)}</div>
                <div class="step-error"><strong>Watch Out:</strong> ${escapeHTML(step.error_warnings)}</div>
            `;
            timeline.appendChild(el);
        });
    }
}
