let isDeleteMode = false;
let selectedForDeletion = new Set();
let ws = null;

// Global App State
let currentUser = null;
let currentProjectId = null;
let currentProjectName = null;
let currentIntelligenceReportId = null;

let onboardingHistory = [];
let followupHistory = [];

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
        handleLogout();
    }
    return response;
};

// ----------------------------------------------------
// Authentication & Profile Boot Sequence
// ----------------------------------------------------
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
        if(!response.ok) throw new Error(data.detail || 'Authentication failed');
        
        localStorage.setItem('synapseip_token', data.access_token);
        bootSequence(); // Init app
    } catch(err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = 'block';
    }
}

function handleLogout() {
    localStorage.removeItem('synapseip_token');
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('login-gateway').style.display = 'flex';
}

async function updatePassword() {
    const pwd = document.getElementById('new-password').value;
    const msg = document.getElementById('pass-msg');
    if (!pwd) return;
    try {
        const res = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({new_password: pwd})
        });
        if (res.ok) {
            msg.style.color = '#34d399';
            msg.innerText = "Password Updated!";
            setTimeout(() => { msg.innerText = ""; document.getElementById('new-password').value = ""; }, 3000);
        } else { throw new Error("Failed"); }
    } catch(e) {
        msg.style.color = '#f87171';
        msg.innerText = "Update Failed.";
    }
}

async function bootSequence() {
    document.getElementById('login-gateway').style.display = 'none';
    document.getElementById('main-app').style.display = 'flex';
    
    try {
        const res = await fetch('/api/me');
        if (res.ok) {
            currentUser = await res.json();
            document.getElementById('avatar-initial').innerText = currentUser.username.charAt(0).toUpperCase();
            document.getElementById('profile-username').innerText = currentUser.username;
            document.getElementById('profile-id').innerText = `ID: #${currentUser.id.toString().padStart(4, '0')}`;
        }
    } catch(e) {}
    
    await loadProjectsDropdown();
    
    // Auto-select latest project if exists, otherwise ask to start new
    if (window.cachedProjects && window.cachedProjects.length > 0) {
        selectProject(window.cachedProjects[0].id, window.cachedProjects[0].name);
    } else {
        createNewProject();
    }
    
    fetchTokenStats();
    initWebSocket();
}

// ----------------------------------------------------
// Project Dropdown & Navigation Context
// ----------------------------------------------------
async function loadProjectsDropdown() {
    try {
        const res = await fetch('/api/projects');
        if (res.ok) {
            const projects = await res.json();
            window.cachedProjects = projects;
            renderProjectList(projects);
        }
    } catch(e) { console.error(e); }
}

function renderProjectList(projects) {
    const list = document.getElementById('project-list');
    list.innerHTML = '';
    
    projects.forEach(p => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${escapeHTML(p.name)}</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
            <div class="nested-menu" id="nested-${p.id}">
                <div style="padding:10px 16px; font-size:0.75rem; color:#6b7280; border-bottom:1px solid rgba(255,255,255,0.05); text-transform:uppercase; font-weight:700;">Loading Details...</div>
            </div>
        `;
        
        li.addEventListener('mouseenter', () => loadProjectDocuments(p.id));
        li.addEventListener('click', (e) => {
            // Only select project if not clicking on nested menu items
            if (e.target.closest('.nested-menu')) return;
            selectProject(p.id, p.name);
        });
        
        list.appendChild(li);
    });
}

// Hover trigger to fetch the project's sub-documents
async function loadProjectDocuments(projectId) {
    const nested = document.getElementById(`nested-${projectId}`);
    if (nested.dataset.loaded) return;
    
    try {
        const res = await fetch(`/api/projects/${projectId}/documents`);
        if (!res.ok) return;
        const data = await res.json();
        
        nested.innerHTML = '';
        
        // Add Intelligence Models
        const intLabel = document.createElement('div');
        intLabel.style.cssText = "padding:10px 16px; font-size:0.75rem; color:#6b7280; border-bottom:1px solid rgba(255,255,255,0.05); text-transform:uppercase; font-weight:700;";
        intLabel.innerText = "🧠 Intelligence Reports";
        nested.appendChild(intLabel);
        
        if (data.intelligence.length === 0) {
            nested.innerHTML += `<div class="nested-menu-item" style="opacity:0.5; cursor:default;">No records found</div>`;
        } else {
            data.intelligence.forEach((report, idx) => {
                const el = document.createElement('div');
                el.className = "nested-menu-item";
                el.innerText = `Report #${data.intelligence.length - idx} (${new Date(report.timestamp).toLocaleDateString()})`;
                el.addEventListener('click', () => {
                    selectProject(projectId, window.cachedProjects.find(p=>p.id===projectId)?.name || "Project");
                    renderDashboard(report.data);
                });
                nested.appendChild(el);
            });
        }
        
        // Add Blueprints
        const bpLabel = document.createElement('div');
        bpLabel.style.cssText = "padding:10px 16px; font-size:0.75rem; color:#6b7280; border-bottom:1px solid rgba(255,255,255,0.05); border-top:1px solid rgba(255,255,255,0.05); text-transform:uppercase; font-weight:700;";
        bpLabel.innerText = "🏗️ Architecture Blueprints";
        nested.appendChild(bpLabel);
        
        if (data.blueprints.length === 0) {
            nested.innerHTML += `<div class="nested-menu-item" style="opacity:0.5; cursor:default;">No records found</div>`;
        } else {
            data.blueprints.forEach((bp, idx) => {
                const el = document.createElement('div');
                el.className = "nested-menu-item";
                el.innerText = `Blueprint #${data.blueprints.length - idx} (${new Date(bp.timestamp).toLocaleDateString()})`;
                el.addEventListener('click', () => {
                    selectProject(projectId, window.cachedProjects.find(p=>p.id===projectId)?.name || "Project");
                    showBlueprint(bp.data);
                });
                nested.appendChild(el);
            });
        }
        
        nested.dataset.loaded = "true";
    } catch(e) { console.error("Error loading nested doc", e); }
}

async function createNewProject() {
    const name = prompt("Enter a name for your new Project:");
    if (!name) return;
    
    try {
        const res = await fetch('/api/projects', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: name})
        });
        if (res.ok) {
            const p = await res.json();
            await loadProjectsDropdown();
            selectProject(p.id, p.name);
        }
    } catch(e) { alert("Failed to create project."); }
}

function selectProject(projectId, projectName) {
    currentProjectId = projectId;
    currentProjectName = projectName;
    document.getElementById('active-project-name').innerText = escapeHTML(projectName);
    
    // Clear screens and return to Onboarding funnel
    document.getElementById('blueprint-viewer').style.display = 'none';
    document.getElementById('intelligence-dashboard').style.display = 'none';
    document.getElementById('onboarding-screen').style.display = 'flex';
    
    // Reset agent chats
    onboardingHistory = [];
    followupHistory = [];
    document.getElementById('chat-history').innerHTML = '';
    document.getElementById('command-bar').style.display = 'none';
    document.getElementById('chat-input').disabled = false;
    document.getElementById('chat-input').placeholder = "Describe the idea you want to build...";
    document.getElementById('chat-input').style.opacity = "1";
    
    // Fetch project's specific sources
    fetchSources();
    setTimeout(() => { sendOnboardingMessage(true); }, 500);
}

// ----------------------------------------------------
// Pipeline Event Listeners & Chat Agents
// ----------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    marked.setOptions({ breaks: true });
    
    // Bind UI actions
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('update-pass-btn').addEventListener('click', updatePassword);
    document.getElementById('new-project-btn').addEventListener('click', createNewProject);
    
    document.getElementById('chat-send').addEventListener('click', () => sendOnboardingMessage(false));
    document.getElementById('chat-input').addEventListener('keypress', (e) => { if(e.key === 'Enter') sendOnboardingMessage(false); });
    
    document.getElementById('followup-chat-send').addEventListener('click', () => sendFollowupMessage());
    document.getElementById('followup-chat-input').addEventListener('keypress', (e) => { if(e.key === 'Enter') sendFollowupMessage(); });
    
    // Routing Generation Hooks
    document.getElementById('generate-btn').addEventListener('click', generateIntelligence);
    document.getElementById('regenerate-intel-btn').addEventListener('click', () => selectProject(currentProjectId, currentProjectName));
    document.getElementById('build-blueprint-btn').addEventListener('click', startArchitectPipeline);
    
    document.getElementById('btn-export-pdf').addEventListener('click', () => {
        const originalTitle = document.title;
        document.title = `Intelligence Report - ${currentProjectName} - ${new Date().toISOString().split('T')[0]}`;
        setTimeout(() => { window.print(); document.title = originalTitle; }, 50);
    });

    if(localStorage.getItem('synapseip_token')) bootSequence();
    
    // Source Binding Delete mechanics ...
    bindDeleteMechanics();
});

// Phase 1: Onboarding Agent
async function sendOnboardingMessage(initial = false) {
    const chatInput = document.getElementById('chat-input');
    const chatHistoryEl = document.getElementById('chat-history');
    if (!chatHistoryEl) return;
    
    const userText = chatInput ? chatInput.value.trim() : "";
    if (!initial && !userText) return;
    
    if (!initial) {
        onboardingHistory.push({ role: "user", content: userText });
        const userBubble = document.createElement('div');
        userBubble.style.cssText = "background: rgba(255,255,255,0.1); padding: 12px 16px; border-radius: 12px; align-self: flex-end; max-width: 85%; color: white; font-size: 0.95rem; line-height: 1.5;";
        userBubble.textContent = userText;
        chatHistoryEl.appendChild(userBubble);
        if (chatInput) chatInput.value = "";
    } else {
        chatHistoryEl.innerHTML = `<div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); padding: 12px 16px; border-radius: 12px; align-self: flex-start; max-width: 85%; color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;"><em>Evaluating project constraints...</em></div>`;
    }
    
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
        if (!response.ok) throw new Error('API Error');
        
        const data = await response.json();
        if (initial) chatHistoryEl.innerHTML = ""; 
        
        onboardingHistory.push({ role: "model", content: data.message });
        
        const agentBubble = document.createElement('div');
        agentBubble.style.cssText = "background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); padding: 12px 16px; border-radius: 12px; align-self: flex-start; max-width: 85%; color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;";
        agentBubble.innerHTML = marked.parse(data.message);
        chatHistoryEl.appendChild(agentBubble);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
        
        if (data.is_complete) {
            document.getElementById('config-designer').value = data.designer_name || currentUser.username;
            document.getElementById('config-appname').value = data.app_name || currentProjectName;
            document.getElementById('config-purpose').value = data.core_purpose || "";
            if (chatInput) {
                chatInput.disabled = true;
                chatInput.placeholder = "Configuration Complete.";
                chatInput.style.opacity = "0.5";
            }
            document.getElementById('command-bar').style.display = 'flex';
        }
    } catch (e) {
        if(document.getElementById("chat-thinking")) chatHistoryEl.removeChild(document.getElementById("chat-thinking"));
        alert("Agent connection failed. Check backend.");
    }
}

// Phase 2: Render Intelligence Report
const THOUGHTS = ["Correlating raw project memories...", "Conducting live Market SWOT...", "Building Vibe Coding Pipeline..."];
async function generateIntelligence() {
    const btn = document.getElementById('generate-btn');
    const thinkingContainer = document.getElementById('thinking-container');
    const fill = document.getElementById('progress-bar-fill');
    const stream = document.getElementById('consciousness-stream');
    
    btn.style.display = 'none';
    thinkingContainer.style.display = 'flex';
    fill.style.width = '0%';
    
    let progress = 0; let thoughtIndex = 0; stream.innerText = THOUGHTS[0];
    const simInterval = setInterval(() => { if (progress < 90) { progress += 1.5; fill.style.width = `${progress}%`; } }, 100);
    const thoughtInterval = setInterval(() => { stream.style.opacity='0'; setTimeout(()=>{ thoughtIndex=(thoughtIndex+1)%THOUGHTS.length; stream.innerText=THOUGHTS[thoughtIndex]; stream.style.opacity='1'; },300); }, 2500);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ target_platform: "Antigravity" })
        });
        
        if (!response.ok) throw new Error("Analysis failed");
        const data = await response.json();
        
        clearInterval(simInterval); clearInterval(thoughtInterval);
        fill.style.width = '100%';
        stream.innerText = "Intelligence Complete!"; stream.style.color = "#34d399";
        
        setTimeout(() => {
            renderDashboard(data);
            btn.style.display = 'flex';
            thinkingContainer.style.display = 'none';
            stream.style.color = "var(--accent-color)";
        }, 1000);
        
    } catch (e) {
        alert(e.message);
        clearInterval(simInterval); clearInterval(thoughtInterval);
        btn.style.display = 'flex'; thinkingContainer.style.display = 'none';
    }
}

function renderDashboard(data) {
    document.getElementById('onboarding-screen').style.display = 'none';
    document.getElementById('blueprint-viewer').style.display = 'none';
    document.getElementById('intelligence-dashboard').style.display = 'flex';
    
    const badge = document.getElementById('score-badge');
    badge.innerText = `${data.viability_score}/100`;
    badge.style.display = 'block';
    if (data.viability_score > 80) badge.style.color = '#34d399';
    else if (data.viability_score > 50) badge.style.color = '#fbbf24';
    else badge.style.color = '#f87171';
    
    // Attach markdown classes dynamically
    ['summary', 'market', 'cost', 'swot', 'blindspots'].forEach(id => {
        document.getElementById(`rep-${id}`).innerHTML = marked.parse(data[id] || "No data provided.");
        document.getElementById(`rep-${id}`).className = `markdown-content text-sm`;
    });
    
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
    
    // Re-init Follow-up agent automatically
    followupHistory = [];
    document.getElementById('followup-chat-history').innerHTML = '';
    sendFollowupMessage(true); // silent seed
}

// Phase 3: Follow-Up Architect
async function sendFollowupMessage(silentSeed = false) {
    const inputEl = document.getElementById('followup-chat-input');
    const histEl = document.getElementById('followup-chat-history');
    
    let text = "";
    if (!silentSeed) {
        text = inputEl.value.trim();
        if (!text) return;
        followupHistory.push({role: "user", content: text});
        histEl.innerHTML += `<div style="background:rgba(255,255,255,0.1); padding:10px; border-radius:8px; margin-bottom:8px; align-self:flex-end; color:white; font-size:0.9rem;">${escapeHTML(text)}</div>`;
        inputEl.value = "";
    }
    
    const loader = document.createElement('div');
    loader.id = "fu-load"; loader.style.cssText = "color:#9ca3af; font-size:0.8rem; font-style:italic; margin-bottom:8px;"; loader.innerText = "Synthesizing Strategy...";
    histEl.appendChild(loader);
    histEl.scrollTop = histEl.scrollHeight;
    
    try {
        const res = await fetch('/api/chat/followup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ project_id: currentProjectId, history: followupHistory })
        });
        histEl.removeChild(loader);
        
        if (res.ok) {
            const data = await res.json();
            followupHistory.push({role: "model", content: data.message});
            histEl.innerHTML += `<div class="markdown-content" style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); padding:12px; border-radius:8px; margin-bottom:8px; color:#e2e8f0; font-size:0.9rem;">${marked.parse(data.message)}</div>`;
        }
    } catch(e) {
        if(document.getElementById("fu-load")) histEl.removeChild(document.getElementById("fu-load"));
    }
    histEl.scrollTop = histEl.scrollHeight;
}

// Phase 4: Architect Generation
async function startArchitectPipeline() {
    const btn = document.getElementById('build-blueprint-btn');
    btn.innerHTML = `<span class='loading-dots'>Allocating Resources...</span>`;
    btn.disabled = true;
    
    try {
        const res = await fetch('/api/architect/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                target_platform: "Antigravity",
                designer_name: currentUser ? currentUser.username : "Unknown",
                app_name: currentProjectName,
                app_purpose: "Automated via Follow-Up"
            })
        });
        if (!res.ok) throw new Error("Failed to start logic router.");
    } catch(e) {
        btn.innerHTML = `Build Architect Blueprint (.md)`;
        btn.disabled = false;
        alert(e.message);
    }
    // Result hand-handled by WebSocket
}

// Blueprint Viewer Route
function showBlueprint(markdownText) {
    document.getElementById('intelligence-dashboard').style.display = 'none';
    document.getElementById('onboarding-screen').style.display = 'none';
    document.getElementById('blueprint-viewer').style.display = 'flex';
    
    document.getElementById('blueprint-content').innerHTML = marked.parse(markdownText);
    
    // Create downloadable blob
    const blob = new Blob([markdownText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.getElementById('blueprint-download-link');
    link.href = url;
    link.download = `Blueprint_${currentProjectName.replace(/\s+/g, '_')}.md`;
}

// ----------------------------------------------------
// Memory Source Fetching & WebSockets
// ----------------------------------------------------
async function fetchSources() {
    if (!currentProjectId) return;
    const listContainer = document.getElementById('sources-list');
    const badge = document.getElementById('source-count');

    try {
        const response = await fetch(`/api/projects/${currentProjectId}/sources`);
        const data = await response.json();
        listContainer.innerHTML = '';

        if (data.length === 0) {
            listContainer.innerHTML = '<div class="loading-state">Project memory is empty.<br>Use your Extension to sync contexts.</div>';
            window.currentSources = [];
            badge.innerText = `0 Note(s)`;
            return;
        }

        window.currentSources = data;
        badge.innerText = `${data.length} Note(s)`;

        data.forEach((source, index) => {
            const card = document.createElement('div');
            card.className = 'source-card';
            
            const date = new Date(source.timestamp).toLocaleDateString(undefined, {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
            let sourceHost = "Extension";
            if(source.source_url) { try { sourceHost = new URL(source.source_url).hostname; } catch(e){} }

            const tempDiv = document.createElement('div'); tempDiv.innerHTML = source.content;
            const plainText = tempDiv.innerText || tempDiv.textContent || "";
            
            let smartTitle = source.title;
            if (!smartTitle || smartTitle.startsWith("Gemini Response")) {
                let fallback = plainText.split(/[.\n]/)[0].replace(/[*_#>]/g, '').trim();
                smartTitle = fallback.length > 3 ? fallback : "Synced Note";
            }
            if (smartTitle.length > 55) smartTitle = smartTitle.substring(0, 55) + "...";

            let bHTML = !source.processed ? `<span style="font-size:0.7rem; background:rgba(59,130,246,0.2); color:#60a5fa; padding:2px 6px; border-radius:4px; margin-left:8px;">Queued ⏳</span>` : '';
            card.innerHTML = `
                <div class="source-title"><span style="color:var(--accent-color); margin-right:6px;">#${index+1}</span>${escapeHTML(smartTitle)}${bHTML}</div>
                <div class="source-time">${sourceHost} &bull; ${date}</div>
                <div class="source-preview">${escapeHTML(plainText)}</div>
            `;
            
            if (isDeleteMode && selectedForDeletion.has(source.id)) card.classList.add('selected-for-deletion');
            
            card.addEventListener('click', (e) => {
                if (isDeleteMode) {
                    if (selectedForDeletion.has(source.id)) { selectedForDeletion.delete(source.id); card.classList.remove('selected-for-deletion'); }
                    else { selectedForDeletion.add(source.id); card.classList.add('selected-for-deletion'); }
                    document.getElementById('delete-count-text').innerText = `${selectedForDeletion.size} selected`;
                    return;
                }
                document.getElementById('modal-title').innerText = sourceHost + ' Insight';
                document.getElementById('modal-body-text').innerHTML = source.content;
                document.getElementById('source-modal').style.display = 'flex';
            });
            listContainer.appendChild(card);
        });

    } catch (error) { listContainer.innerHTML = '<div class="loading-state" style="color: #ef4444;">Connection failed.</div>'; }
}

function initWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "architect_complete") {
                const btn = document.getElementById('build-blueprint-btn');
                btn.innerHTML = `Build Architect Blueprint (.md)`;
                btn.disabled = false;
                
                // Show modal overlay or direct logic
                window.open(data.download_url, '_blank');
                
                // Refresh project dropdown cache instantly so it appears
                loadProjectDocuments(currentProjectId);
            } else if (data.type === "sources_deleted") fetchSources();
            return;
        } catch (e) {}

        if (event.data === "new_source") {
            if (window._syncTimer) clearTimeout(window._syncTimer);
            window._syncTimer = setTimeout(() => fetchSources(), 300);
        } else if (event.data === "token_update") fetchTokenStats();
    };
}

async function fetchTokenStats() {
    try {
        const res = await fetch('/api/stats/tokens');
        if (!res.ok) return;
        const data = await res.json();
        document.getElementById('tt-tokens').innerText = data.tokens.toLocaleString();
        document.getElementById('tt-cost').innerText = "$" + data.cost.toFixed(4);
    } catch(e){}
}
setInterval(() => fetchSources(), 3000);

function escapeHTML(str) { const p = document.createElement("p"); p.appendChild(document.createTextNode(str)); return p.innerHTML; }

// --- Delete Modals Component ---
function bindDeleteMechanics() {
    document.getElementById('modal-close').addEventListener('click', () => document.getElementById('source-modal').style.display='none');
    
    const tog = document.getElementById('toggle-trash-btn');
    const bar = document.getElementById('delete-actions-bar');
    const cfm = document.getElementById('confirm-delete-btn');
    const cnl = document.getElementById('cancel-delete-btn');
    const all = document.getElementById('select-all-btn');
    
    function exitDel() {
        isDeleteMode=false; selectedForDeletion.clear(); bar.style.display='none'; tog.classList.remove('active');
        document.querySelectorAll('.source-card.selected-for-deletion').forEach(c=>c.classList.remove('selected-for-deletion'));
    }
    
    tog.addEventListener('click', () => {
        isDeleteMode = !isDeleteMode;
        if(isDeleteMode){ bar.style.display='flex'; tog.classList.add('active'); document.getElementById('delete-count-text').innerText="0 selected"; selectedForDeletion.clear(); }
        else exitDel();
    });
    cnl.addEventListener('click', exitDel);
    all.addEventListener('click', () => {
        if(!window.currentSources)return;
        window.currentSources.forEach(s=>selectedForDeletion.add(s.id));
        document.querySelectorAll('.source-card').forEach(c=>c.classList.add('selected-for-deletion'));
        document.getElementById('delete-count-text').innerText=`${selectedForDeletion.size} selected`;
    });
    cfm.addEventListener('click', async () => {
        if(selectedForDeletion.size===0)return;
        if(!confirm(`Delete ${selectedForDeletion.size} notes permanently?`))return;
        cfm.innerText="Deleting...";
        try {
            const res = await fetch('/api/sources/bulk-delete', {
                method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({source_ids:Array.from(selectedForDeletion)})
            });
            if(res.ok){ exitDel(); fetchSources(); }
        } catch(e){} finally{ cfm.innerText="Delete"; }
    });
}
