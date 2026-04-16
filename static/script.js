let isDeleteMode = false;
let selectedForDeletion = new Set();

document.addEventListener('DOMContentLoaded', () => {
    fetchSources();
    fetchLatestReport();
    
    document.getElementById('generate-btn').addEventListener('click', generateIntelligence);
    document.getElementById('architect-btn').addEventListener('click', openArchitectConfig);
    
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
    const selectAllBtn = document.getElementById('select-all-btn');
    
    selectAllBtn.addEventListener('click', () => {
        if (!window.currentSources) return;
        window.currentSources.forEach(s => selectedForDeletion.add(s.id));
        document.querySelectorAll('.source-card').forEach(card => card.classList.add('selected-for-deletion'));
        document.getElementById('delete-count-text').innerText = `${selectedForDeletion.size} selected`;
    });
    
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
            window.currentSources = [];
            return;
        }

        window.currentSources = data;

        // Update badge
        sourceCountBadge.innerText = `${data.length} Note(s)`;

        // Render each source as a card
        data.forEach((source, index) => {
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
            } catch (e) {}

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = source.content;
            const plainText = tempDiv.innerText || tempDiv.textContent || "";
            
            // Prioritize the rich AI title generated on the backend
            let smartTitle = source.title;
            // Fallback for legacy notes that just had "Gemini Response - [Date]"
            if (!smartTitle || smartTitle.startsWith("Gemini Response")) {
                let fallback = plainText.split(/[.\n]/)[0].replace(/[*_#>]/g, '').trim();
                // Strip the "User Prompt:" prefix if we accidentally captured it
                if (fallback.startsWith("User Prompt:")) {
                    fallback = fallback.replace("User Prompt:", "").trim();
                }
                if (fallback.startsWith("AI Response:")) {
                    fallback = fallback.replace("AI Response:", "").trim();
                }
                smartTitle = fallback.length > 3 ? fallback : "Synced Note";
            }
            
            if (smartTitle.length > 55) smartTitle = smartTitle.substring(0, 55) + "...";

            card.innerHTML = `
                <div class="source-title"><span style="color: var(--accent-color); margin-right: 6px;">#${index + 1}</span>${escapeHTML(smartTitle)}</div>
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
    try {
        const data = JSON.parse(event.data);
        if (data.type === "progress") {
            const fill = document.getElementById('progress-bar-fill');
            const stream = document.getElementById('consciousness-stream');
            if (fill && stream) {
                fill.style.width = `${data.progress}%`;
                stream.style.opacity = '0';
                setTimeout(() => {
                    stream.innerText = data.message;
                    stream.style.opacity = '1';
                }, 150);
            }
        } else if (data.type === "architect_complete") {
            const fill = document.getElementById('progress-bar-fill');
            const stream = document.getElementById('consciousness-stream');
            if (fill && stream) {
                fill.style.width = `100%`;
                stream.innerText = data.message;
                stream.style.color = "#34d399";
                
                const btnContainer = document.querySelector('.command-bar');
                if (btnContainer && !document.getElementById('download-doc-btn')) {
                    const downloadBtn = document.createElement('a');
                    downloadBtn.id = 'download-doc-btn';
                    downloadBtn.href = data.download_url;
                    downloadBtn.className = 'generate-btn';
                    downloadBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
                    downloadBtn.style.textDecoration = 'none';
                    downloadBtn.style.marginTop = '12px';
                    downloadBtn.style.display = 'flex';
                    downloadBtn.innerHTML = `<span>Download Blueprint (.md)</span>`;
                    btnContainer.appendChild(downloadBtn);
                }
            }
        }
        return;
    } catch (e) {
        // String fallback handler
    }

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

function openArchitectConfig() {
    document.getElementById('config-modal').style.display = 'flex';
}

document.getElementById('config-close').addEventListener('click', () => {
    document.getElementById('config-modal').style.display = 'none';
});

async function startArchitectPipeline() {
    const designer = document.getElementById('config-designer').value.trim();
    const appName = document.getElementById('config-appname').value.trim();
    const purpose = document.getElementById('config-purpose').value.trim();
    
    // Hide modal
    document.getElementById('config-modal').style.display = 'none';

    const btn = document.getElementById('architect-btn');
    const genBtn = document.getElementById('generate-btn');
    const select = document.getElementById('vibe-tool');
    const tool = select.value;
    const thinkingContainer = document.getElementById('thinking-container');
    const fill = document.getElementById('progress-bar-fill');
    const stream = document.getElementById('consciousness-stream');
    
    genBtn.style.display = 'none';
    btn.style.display = 'none';
    select.disabled = true;
    thinkingContainer.style.display = 'flex';
    
    fill.style.width = '0%';
    stream.innerText = "Requesting Architect Thread...";
    stream.style.color = "var(--accent-color)";
    
    try {
        const response = await fetch('/api/architect/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                target_platform: tool,
                designer_name: designer,
                app_name: appName,
                app_purpose: purpose
            })
        });
        
        if (!response.ok) {
            const err = await response.json();
            alert("Analysis failed: " + (err.detail || "Server Error"));
            return;
        }
    } catch (e) {
        alert("Request error: " + e.message);
    }
}

// Bind the config submit explicitly
document.getElementById('config-submit').addEventListener('click', startArchitectPipeline);

const THOUGHTS = [
    "Initializing SynapseIP Architecture...",
    "Correlating raw Gemini payloads...",
    "Mapping platform constraints...",
    "Conducting live Market SWOT Analysis...",
    "Evaluating competitive cost dynamics...",
    "Building Vibe Coding Pipeline...",
    "Validating strict JSON schema adherence...",
    "Finalizing actionable execution nodes..."
];

async function generateIntelligence() {
    const btn = document.getElementById('generate-btn');
    const select = document.getElementById('vibe-tool');
    const tool = select.value;
    const thinkingContainer = document.getElementById('thinking-container');
    const fill = document.getElementById('progress-bar-fill');
    const stream = document.getElementById('consciousness-stream');
    
    // Hide inputs, show loading UI
    btn.style.display = 'none';
    select.disabled = true;
    thinkingContainer.style.display = 'flex';
    
    let progress = 0;
    let thoughtIndex = 0;
    stream.innerText = THOUGHTS[0];
    
    // Simulate progressive filling
    const simInterval = setInterval(() => {
        if (progress < 96) {
            progress += (96 - progress) * 0.05 + 0.1;
            fill.style.width = `${progress}%`;
        }
    }, 100);
    
    // Rotate text
    const thoughtInterval = setInterval(() => {
        stream.style.opacity = '0';
        setTimeout(() => {
            thoughtIndex = (thoughtIndex + 1) % THOUGHTS.length;
            stream.innerText = THOUGHTS[thoughtIndex];
            stream.style.opacity = '1';
        }, 300);
    }, 2500);
    
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
        
        // Server responded! Max out bar
        clearInterval(simInterval);
        clearInterval(thoughtInterval);
        fill.style.width = '100%';
        stream.style.opacity = '0';
        setTimeout(() => {
            stream.innerText = "Architecture Complete!";
            stream.style.color = "#34d399"; // Success green
            stream.style.opacity = '1';
            
            setTimeout(() => {
                renderDashboard(data);
                
                // Reset loading UI internally allowing future generates
                btn.style.display = 'flex';
                select.disabled = false;
                thinkingContainer.style.display = 'none';
                fill.style.width = '0%';
                stream.style.color = "var(--accent-color)";
                stream.innerText = THOUGHTS[0];
            }, 800);
        }, 300);
        
    } catch (e) {
        alert("Request error: " + e.message);
        clearInterval(simInterval);
        clearInterval(thoughtInterval);
        btn.style.display = 'flex';
        select.disabled = false;
        thinkingContainer.style.display = 'none';
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
