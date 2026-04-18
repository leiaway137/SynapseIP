let isDeleteMode = false;
let selectedForDeletion = new Set();
let ws = null; // Declare websocket globally

// Authentication Gateway Network Override
const originalFetch = window.fetch;
window.fetch = async function() {
    let [resource, config] = arguments;
    if(typeof resource === 'string' && resource.startsWith('/api')) {
        const token = localStorage.getItem('synapseip_token');
        if(token) {
            config = config || {};
            config.headers = config.headers || {};
            if(!config.headers['Authorization']) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
        }
    }
    const response = await originalFetch(resource, config);
    if(response.status === 401 && typeof resource === 'string' && resource.startsWith('/api') && !resource.startsWith('/api/auth')) {
        localStorage.removeItem('synapseip_token');
        document.getElementById('main-app').style.display = 'none';
        document.getElementById('login-gateway').style.display = 'flex';
    }
    return response;
};

async function handleAuth(type) {
    const username = document.getElementById('auth-user').value.trim();
    const password = document.getElementById('auth-pass').value.trim();
    const errorDiv = document.getElementById('auth-error');
    
    if(!username || !password) {
        errorDiv.textContent = 'Please enter both username and password';
        errorDiv.style.display = 'block';
        return;
    }
    
    try {
        let response;
        if(type === 'login') {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            response = await originalFetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
        } else {
            response = await originalFetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
        }
        
        const data = await response.json();
        
        if(!response.ok) {
            throw new Error(data.detail || 'Authentication failed');
        }
        
        localStorage.setItem('synapseip_token', data.access_token);
        document.getElementById('login-gateway').style.display = 'none';
        document.getElementById('main-app').style.display = '';
        
        initApp(); // Boot up!
        
    } catch(err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = 'block';
    }
}

function initApp() {
    fetchSources();
    fetchTokenStats();
    setTimeout(() => {
        sendOnboardingMessage(true);
    }, 500);
    initWebSocket();
}

document.addEventListener('DOMContentLoaded', () => {
    // Enable single line breaks in Markdown
    marked.setOptions({ breaks: true });
    
    if(localStorage.getItem('synapseip_token')) {
        document.getElementById('login-gateway').style.display = 'none';
        document.getElementById('main-app').style.display = '';
        initApp();
    }
    
    document.getElementById('generate-btn').addEventListener('click', generateIntelligence);
    document.getElementById('architect-btn').addEventListener('click', startArchitectPipeline);
    
    document.getElementById('btn-return-home').addEventListener('click', () => {
        document.getElementById('analysis-dashboard').style.display = 'none';
        document.getElementById('welcome-screen').style.display = 'flex';
    });
    
    document.getElementById('btn-export-pdf').addEventListener('click', () => {
        const originalTitle = document.title;
        const appName = document.getElementById('config-appname').value.trim() || 'SynapseIP';
        const designer = document.getElementById('config-designer').value.trim() || 'Unknown';
        const dateStr = new Date().toISOString().split('T')[0];
        
        document.title = `${appName} - ${designer} - ${dateStr}`;
        
        // Timeout is legally necessary in Chrome so it doesn't cache the old title during synchronous UI halting
        setTimeout(() => {
            window.print();
            document.title = originalTitle;
        }, 50);
    });
    
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
            sourceCountBadge.innerText = `0 Note(s)`;
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

            let badgeHTML = '';
            if (source.processed === false) {
                badgeHTML = `<span style="font-size: 0.75rem; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 2px 6px; border-radius: 4px; margin-left: 8px;">Queued ⏳</span>`;
            }

            card.innerHTML = `
                <div class="source-title"><span style="color: var(--accent-color); margin-right: 6px;">#${index + 1}</span>${escapeHTML(smartTitle)}${badgeHTML}</div>
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
function initWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);

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
            } else if (data.type === "sources_deleted") {
                fetchSources();
            }
            return;
        } catch (e) {
            // String fallback handler
        }

        if (event.data === "new_source") {
            console.log("Real-time update received! Debouncing fetch...");
            if (window._syncTimer) clearTimeout(window._syncTimer);
            window._syncTimer = setTimeout(() => {
                fetchSources();
            }, 300);
        } else if (event.data === "new_report") {
            console.log("New report broadcast received.");
            fetchLatestReport();
        } else if (event.data === "token_update") {
            fetchTokenStats();
        }
    };

    ws.onclose = function() {
        console.log("WebSocket connection closed.");
    };
}

async function fetchTokenStats() {
    try {
        const res = await fetch('/api/stats/tokens');
        if (!res.ok) return;
        const data = await res.json();
        
        document.getElementById('tt-tokens').innerText = data.tokens.toLocaleString();
        document.getElementById('tt-cost').innerText = "$" + data.cost.toFixed(4);
    } catch(e) {
        console.error("Token sync failed", e);
    }
}

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

async function startArchitectPipeline() {
    const designer = document.getElementById('config-designer').value.trim();
    const appName = document.getElementById('config-appname').value.trim();
    const purpose = document.getElementById('config-purpose').value.trim();

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
    
    document.getElementById('rep-summary').innerHTML = marked.parse(data.summary);
    document.getElementById('rep-market').innerHTML = marked.parse(data.market_analysis);
    document.getElementById('rep-cost').innerHTML = marked.parse(data.cost_benefit);
    document.getElementById('rep-swot').innerHTML = marked.parse(data.swot);
    document.getElementById('rep-blindspots').innerHTML = marked.parse(data.blindspots || "No systemic blindspots identified.");
    
    // Add specific markdown styling class
    document.getElementById('rep-summary').className = 'markdown-content';
    document.getElementById('rep-market').className = 'markdown-content text-sm';
    document.getElementById('rep-cost').className = 'markdown-content text-sm';
    document.getElementById('rep-swot').className = 'markdown-content text-sm';
    document.getElementById('rep-blindspots').className = 'markdown-content text-sm';
    
    const timeline = document.getElementById('rep-timeline');
    timeline.innerHTML = '';
    
    if (data.vibe_coding_pipeline) {
        data.vibe_coding_pipeline.forEach((step, idx) => {
            const el = document.createElement('div');
            el.className = 'timeline-step';
            el.innerHTML = `
                <h4>Step ${idx + 1}</h4>
                <div class="step-prompt">${escapeHTML(step.prompt_text)}</div>
                <div class="step-why"><strong>Why:</strong> ${marked.parse(step.why)}</div>
                <div class="step-expect"><strong>Expectation:</strong> ${marked.parse(step.expectation)}</div>
                <div class="step-error"><strong>Watch Out:</strong> ${marked.parse(step.error_warnings)}</div>
            `;
            timeline.appendChild(el);
        });
    }
}

// ------------------------------------------------------------------
// Onboarding Chat Agent System
// ------------------------------------------------------------------
let onboardingHistory = [];

async function sendOnboardingMessage(initial = false) {
    const chatInput = document.getElementById('chat-input');
    const chatHistoryEl = document.getElementById('chat-history');
    if (!chatHistoryEl) return;
    
    const userText = chatInput ? chatInput.value.trim() : "";
    
    // Prevent empty sends from user
    if (!initial && !userText) return;
    
    if (!initial) {
        onboardingHistory.push({ role: "user", content: userText });
        const userBubble = document.createElement('div');
        userBubble.style.cssText = "background: rgba(255,255,255,0.1); padding: 12px 16px; border-radius: 12px; align-self: flex-end; max-width: 85%; color: white; font-size: 0.95rem; line-height: 1.5;";
        userBubble.textContent = userText;
        chatHistoryEl.appendChild(userBubble);
        if (chatInput) chatInput.value = "";
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    } else {
        chatHistoryEl.innerHTML = `
            <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); padding: 12px 16px; border-radius: 12px; align-self: flex-start; max-width: 85%; color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;">
                <em>Evaluating sources...</em>
            </div>
        `;
    }
    
    // Render loading state
    const thinkingBubble = document.createElement('div');
    thinkingBubble.id = "chat-thinking";
    thinkingBubble.style.cssText = "align-self: flex-start; margin-left: 10px; color: #9ca3af; font-size: 0.85rem; font-style: italic;";
    thinkingBubble.innerHTML = "Agent is typing <span class='loading-dots'>...</span>";
    chatHistoryEl.appendChild(thinkingBubble);
    chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    
    try {
        const response = await fetch('/api/chat/onboarding', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ history: onboardingHistory })
        });
        
        chatHistoryEl.removeChild(thinkingBubble);
        
        if (!response.ok) {
            throw new Error('API Error');
        }
        
        const data = await response.json();
        
        if (initial) {
            chatHistoryEl.innerHTML = ""; // Clear the evaluation placeholder
        }
        
        onboardingHistory.push({ role: "model", content: data.message });
        
        const agentBubble = document.createElement('div');
        agentBubble.style.cssText = "background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); padding: 12px 16px; border-radius: 12px; align-self: flex-start; max-width: 85%; color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;";
        agentBubble.innerHTML = marked.parse(data.message);
        chatHistoryEl.appendChild(agentBubble);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
        
        // Handle successfully fulfilled configurations
        if (data.is_complete) {
            document.getElementById('config-designer').value = data.designer_name || "Unknown";
            document.getElementById('config-appname').value = data.app_name || "SynapseIP";
            document.getElementById('config-purpose').value = data.core_purpose || "";
            
            if (chatInput) {
                chatInput.disabled = true;
                chatInput.placeholder = "Configuration Complete.";
                chatInput.style.opacity = "0.5";
            }
            
            // Pop the action bar
            document.getElementById('command-bar').style.display = 'flex';
        }
    } catch (e) {
        if(document.getElementById("chat-thinking")) chatHistoryEl.removeChild(document.getElementById("chat-thinking"));
        alert("Agent connection failed. Check backend.");
    }
}
