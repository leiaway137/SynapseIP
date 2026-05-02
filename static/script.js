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
window.fetch = async function(...args) {
    let [resource, config] = args;
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
    
    const token = localStorage.getItem('synapseip_token');
    if(token) {
        // Broadcast immediately, and also a few times over 2 seconds to ensure extension catches it
        // (Content scripts load at document_idle which can be after DOMContentLoaded)
        const broadcast = () => window.postMessage({ type: "SYNAPSE_AUTH_TOKEN", token: token }, "*");
        broadcast();
        setTimeout(broadcast, 500);
        setTimeout(broadcast, 1000);
        setTimeout(broadcast, 2000);
    }
    
    try {
        const res = await fetch('/api/me');
        if (res.ok) {
            currentUser = await res.json();
            document.getElementById('avatar-initial').innerText = currentUser.username.charAt(0).toUpperCase();
            document.getElementById('profile-username').innerText = currentUser.username;
            document.getElementById('profile-id').innerText = `ID: #${currentUser.id.toString().padStart(4, '0')}`;
            if (currentUser.is_admin) {
                document.getElementById('token-tracker').style.display = 'block';
            }
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
        
        // Removed hover, converted to Click-dependent Slide-Out Accordion
        li.addEventListener('click', (e) => {
            // Only select project if not clicking on nested menu items
            if (e.target.closest('.nested-menu')) return;
            
            // Slide out the nested documents menu!
            li.classList.toggle('expanded');
            if (li.classList.contains('expanded')) loadProjectDocuments(p.id);
            
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
        
        nested.innerHTML = '';
        
        const createHeaderStyle = () => "padding:12px 16px; font-size:0.85rem; color:#e2e8f0; border-bottom:1px solid rgba(255,255,255,0.05); font-weight:600; cursor:pointer; display:flex; gap:8px; align-items:center; transition:background 0.2s;";
        
        // -------------------------
        // Intelligence Reports Folder
        // -------------------------
        const intelFolder = document.createElement('div');
        intelFolder.className = 'nested-folder';
        
        const intelHeader = document.createElement('div');
        intelHeader.style.cssText = createHeaderStyle();
        intelHeader.innerHTML = `<span>📁</span> Intel Report(s)`;
        
        // Hover effect inline
        intelHeader.onmouseover = () => intelHeader.style.background = 'rgba(255,255,255,0.05)';
        intelHeader.onmouseout = () => intelHeader.style.background = 'transparent';
        
        intelFolder.appendChild(intelHeader);
        
        const intelContent = document.createElement('div');
        intelContent.style.display = 'none'; // Hidden by default
        intelContent.style.background = 'rgba(0,0,0,0.2)';
        
        if (data.intelligence.length === 0) {
            intelContent.innerHTML = `<div class="nested-menu-item" style="opacity:0.5; cursor:default; padding-left: 24px;">No records found</div>`;
        } else {
            data.intelligence.forEach((report, idx) => {
                const el = document.createElement('div');
                el.className = "nested-menu-item";
                el.style.paddingLeft = "24px";
                const d = new Date(report.timestamp + (!report.timestamp.endsWith('Z') ? 'Z' : ''));
                el.innerText = `IR - ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false})}`;
                el.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (currentProjectId !== projectId) {
                        await selectProject(projectId, window.cachedProjects.find(p=>p.id===projectId)?.name || "Project");
                    }
                    renderDashboard(report.data, data.current_vibe_step);
                });
                intelContent.appendChild(el);
            });
        }
        intelFolder.appendChild(intelContent);
        
        intelHeader.addEventListener('click', (e) => {
            e.stopPropagation();
            intelContent.style.display = intelContent.style.display === 'none' ? 'block' : 'none';
        });
        nested.appendChild(intelFolder);
        
        // -------------------------
        // Architect Documents Folder
        // -------------------------
        const archFolder = document.createElement('div');
        archFolder.className = 'nested-folder';
        
        const archHeader = document.createElement('div');
        archHeader.style.cssText = createHeaderStyle();
        archHeader.innerHTML = `<span>📁</span> Architect Document(s)`;
        
        archHeader.onmouseover = () => archHeader.style.background = 'rgba(255,255,255,0.05)';
        archHeader.onmouseout = () => archHeader.style.background = 'transparent';
        
        archFolder.appendChild(archHeader);
        
        const archContent = document.createElement('div');
        archContent.style.display = 'none'; // Hidden by default
        archContent.style.background = 'rgba(0,0,0,0.2)';
        
        if (data.blueprints.length === 0) {
            archContent.innerHTML = `<div class="nested-menu-item" style="opacity:0.5; cursor:default; padding-left: 24px;">No records found</div>`;
        } else {
            data.blueprints.forEach((bp, idx) => {
                const el = document.createElement('div');
                el.className = "nested-menu-item";
                el.style.paddingLeft = "24px";
                const d = new Date(bp.timestamp + (!bp.timestamp.endsWith('Z') ? 'Z' : ''));
                el.innerText = `AD - ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false})}`;
                el.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (currentProjectId !== projectId) {
                        await selectProject(projectId, window.cachedProjects.find(p=>p.id===projectId)?.name || "Project");
                    }
                    showBlueprint(bp.data);
                });
                archContent.appendChild(el);
            });
        }
        archFolder.appendChild(archContent);
        
        archHeader.addEventListener('click', (e) => {
            e.stopPropagation();
            archContent.style.display = archContent.style.display === 'none' ? 'block' : 'none';
        });
        nested.appendChild(archFolder);
        
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

async function selectProject(projectId, projectName) {
    currentProjectId = projectId;
    currentProjectName = projectName;
    document.getElementById('active-project-name').innerText = escapeHTML(projectName);
    
    // Default: Clear screens
    document.getElementById('blueprint-viewer').style.display = 'none';
    document.getElementById('intelligence-dashboard').style.display = 'none';
    document.getElementById('onboarding-screen').style.display = 'none';
    
    // Reset agent chats
    onboardingHistory = [];
    followupHistory = [];
    document.getElementById('chat-history').innerHTML = '';
    document.getElementById('command-bar').style.display = 'none';
    document.getElementById('chat-input').disabled = false;
    document.getElementById('chat-input').placeholder = "Describe the idea you want to build...";
    document.getElementById('chat-input').style.opacity = "1";
    document.getElementById('onboarding-pre-start').style.display = 'block';
    document.getElementById('onboarding-active').style.display = 'none';
    
    // Fetch project's specific sources
    fetchSources();
    loadThemesCompass();
    
    try {
        const res = await fetch(`/api/projects/${projectId}/documents`);
        if (res.ok) {
            const data = await res.json();
            
            // Automatically surface the most recent blueprint if it exists
            if (data.blueprints && data.blueprints.length > 0) {
                window.currentVibeStep = data.current_vibe_step || 0;
                showBlueprint(data.blueprints[0].data);
                return;
            }
            // Automatically surface the most recent intelligence report if it exists
            if (data.intelligence && data.intelligence.length > 0) {
                renderDashboard(data.intelligence[0].data, data.current_vibe_step, data.followup_history);
                return; // Halt selection pipeline before onboarding kicks in
            }
        }
    } catch(e) { console.error("Error auto-loading project documents.", e); }
    
    // If no intelligence reports exist, launch the Onboarding funnel shell
    document.getElementById('onboarding-screen').style.display = 'flex';
}

function startManualOnboarding() {
    document.getElementById('onboarding-pre-start').style.display = 'none';
    document.getElementById('onboarding-active').style.display = 'block';
    sendOnboardingMessage(true);
}

async function restartOnboarding() {
    if (!currentProjectId) return;
    try {
        await fetch(`/api/projects/${currentProjectId}/clear-onboarding`, { method: 'POST' });
        
        // Reset UI
        const setDisplay = (id, val) => { const el = document.getElementById(id); if (el) el.style.display = val; };
        setDisplay('chat-history', 'flex');
        setDisplay('chat-input-area', 'flex');
        setDisplay('command-bar', 'none');
        
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.disabled = false;
            chatInput.placeholder = "Answer the agent or share your vision...";
            chatInput.style.opacity = "1";
        }
        
        onboardingHistory = [];
        sendOnboardingMessage(true);
    } catch(e) {
        console.error("Failed to clear onboarding", e);
    }
}

function restoreOnboardingConfig(configData) {
    if (typeof configData === 'string') {
        try { configData = JSON.parse(configData); } catch(e) { return false; }
    }
    if (!configData || !configData.is_complete) return false;
    const safelySet = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    safelySet('config-designer', configData.designer_name || currentUser?.username || "Designer");
    safelySet('config-appname', configData.app_name || currentProjectName);
    safelySet('config-purpose', configData.core_purpose || "");
    safelySet('config-audience', configData.target_audience || "");
    safelySet('config-apptype', configData.app_type || "Commercial");
    safelySet('config-budget', configData.budget_constraints || "Free Tier Only");
    safelySet('config-ai_integration', configData.ai_integration || "None");
    safelySet('config-security', configData.security_auth || "Basic");
    safelySet('config-environment', configData.build_environment || "Greenfield (New)");
    safelySet('config-features', JSON.stringify(configData.standout_features || []));
    
    const setDisplay = (id, val) => { const el = document.getElementById(id); if (el) el.style.display = val; };
    setDisplay('onboarding-pre-start', 'none');
    setDisplay('onboarding-active', 'block');
    setDisplay('chat-history', 'none');
    setDisplay('chat-input-area', 'none');
    setDisplay('command-bar', 'flex');
    setDisplay('restart-onboarding-btn', 'inline-block');
    
    return true;
}

// ----------------------------------------------------
// Pipeline Event Listeners & Chat Agents
// ----------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    marked.setOptions({ breaks: true });
    
    // Bind UI actions
    document.getElementById('logout-btn')?.addEventListener('click', handleLogout);
    document.getElementById('update-pass-btn')?.addEventListener('click', updatePassword);
    document.getElementById('new-project-btn')?.addEventListener('click', createNewProject);
    document.getElementById('edit-project-btn')?.addEventListener('click', handleEditProject);
    document.getElementById('restart-onboarding-btn')?.addEventListener('click', restartOnboarding);

    
    document.getElementById('chat-send').addEventListener('click', () => sendOnboardingMessage(false));
    document.getElementById('chat-refresh-sources').addEventListener('click', () => sendOnboardingMessage(true));
    document.getElementById('chat-input').addEventListener('keypress', (e) => { 
        if(e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            sendOnboardingMessage(false); 
        } 
    });
    
    document.getElementById('followup-chat-send').addEventListener('click', () => sendFollowupMessage());
    document.getElementById('followup-chat-input').addEventListener('keypress', (e) => { 
        if(e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            sendFollowupMessage(); 
        } 
    });
    
    // Routing Generation Hooks
    document.getElementById('generate-btn').addEventListener('click', checkAndReviewThemes);
    document.getElementById('regenerate-intel-btn').addEventListener('click', regenerateIntelligence);
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
    
    // Check for 128k Limit (roughly 400,000 characters)
    if (!initial && userText.length > 400000) {
        alert("⚠️ Large payload detected. This document exceeds the 128k token threshold and will be automatically chunked by the server to prevent premium billing spikes.");
    }
    
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
            body: JSON.stringify({ project_id: currentProjectId, history: onboardingHistory })
        });
        
        chatHistoryEl.removeChild(thinkingBubble);
        
        if (!response.ok) {
            throw new Error('API Error');
        }
        
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
            document.getElementById('config-appname').value = currentProjectName;
            document.getElementById('config-purpose').value = data.core_purpose || "";
            document.getElementById('config-audience').value = data.target_audience || "";
            document.getElementById('config-apptype').value = data.app_type || "Commercial";
            document.getElementById('config-budget').value = data.budget_constraints || "Free Tier Only";
            document.getElementById('config-ai_integration').value = data.ai_integration || "None";
            document.getElementById('config-security').value = data.security_auth || "Basic";
            document.getElementById('config-environment').value = data.build_environment || "Greenfield (New)";
            document.getElementById('config-features').value = JSON.stringify(data.standout_features || []);
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

// Phase 2a: Pre-Flight Theme Review
async function checkAndReviewThemes() {
    try {
        const themeRes = await fetch(`/api/projects/${currentProjectId}/themes`);
        const themes = await themeRes.json();
        
        let needsConsolidation = themes.some(t => t.has_unconsolidated_fragments);
        
        if (needsConsolidation || (themes.length > 0 && !window.themesApproved)) {
            // Hide onboarding, show workbench
            document.getElementById('onboarding-screen').style.display = 'none';
            document.getElementById('intelligence-dashboard').style.display = 'none';
            document.getElementById('architect-workbench').style.display = 'flex';
            currentArchitectLoop = -1;
            renderThemeConsolidationState(themes, needsConsolidation);
        } else {
            // No themes to review or already approved
            generateIntelligence();
        }
    } catch (e) {
        console.error("Failed to check themes:", e);
        generateIntelligence(); // fallback to intel report
    }
}

// Phase 2b: Render Intelligence Report
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
            body: JSON.stringify({ 
                target_platform: "Antigravity",
                project_id: currentProjectId,
                app_name: document.getElementById('config-appname').value,
                designer_name: document.getElementById('config-designer').value,
                app_purpose: document.getElementById('config-purpose').value,
                target_audience: document.getElementById('config-audience').value,
                app_type: document.getElementById('config-apptype').value,
                budget_constraints: document.getElementById('config-budget').value,
                ai_integration: document.getElementById('config-ai_integration').value,
                security_auth: document.getElementById('config-security').value,
                build_environment: document.getElementById('config-environment').value,
                standout_features: JSON.parse(document.getElementById('config-features').value || "[]")
            })
        });
        
        if (!response.ok) {
            let errorDetail = response.statusText;
            try {
                const errData = await response.json();
                errorDetail = errData.detail || errorDetail;
            } catch(e) {}
            throw new Error(`Analysis failed: ${errorDetail}`);
        }
        const data = await response.json();
        
        clearInterval(simInterval); clearInterval(thoughtInterval);
        fill.style.width = '100%';
        stream.innerText = "Intelligence Complete!"; stream.style.color = "#34d399";
        
        setTimeout(() => {
            renderDashboard(data);
            btn.style.display = 'flex';
            thinkingContainer.style.display = 'none';
            stream.style.color = "var(--accent-color)";
            
            // Invalidate project sub-menu cache to force-push the newly generated document
            const nested = document.getElementById(`nested-${currentProjectId}`);
            if (nested) {
                delete nested.dataset.loaded;
                loadProjectDocuments(currentProjectId);
            }
        }, 1000);
        
    } catch (e) {
        alert(e.message);
        clearInterval(simInterval); clearInterval(thoughtInterval);
        btn.style.display = 'flex'; thinkingContainer.style.display = 'none';
    }
}

function regenerateIntelligence() {
    document.getElementById('intelligence-dashboard').style.display = 'none';
    document.getElementById('onboarding-screen').style.display = 'flex';
    document.getElementById('command-bar').style.display = 'flex';
    generateIntelligence();
}

function renderDashboard(data, currentVibeStep = 0, history = []) {
    document.getElementById('onboarding-screen').style.display = 'none';
    document.getElementById('blueprint-viewer').style.display = 'none';
    document.getElementById('intelligence-dashboard').style.display = 'flex';
    
    const badge = document.getElementById('score-badge');
    badge.innerText = `${data.viability_score}/100`;
    badge.style.display = 'block';
    if (data.viability_score > 80) badge.style.color = '#34d399';
    else if (data.viability_score > 50) badge.style.color = '#fbbf24';
    else badge.style.color = '#f87171';
    
    // Attach markdown classes dynamically using explicit schema mapping
    const mappings = [
        { id: 'summary', key: 'summary' },
        { id: 'verdict', key: 'verdict' },
        { id: 'harshtruth', key: 'the_harsh_truth' },
        { id: 'pivotpath', key: 'the_pivot_path' },
        { id: 'market', key: 'market_analysis' },
        { id: 'cost', key: 'cost_benefit' },
        { id: 'swot', key: 'swot' },
        { id: 'blindspots', key: 'blindspots' }
    ];
    mappings.forEach(m => {
        document.getElementById(`rep-${m.id}`).innerHTML = marked.parse(data[m.key] || "No data provided.");
        if (m.id !== 'verdict') document.getElementById(`rep-${m.id}`).className = `markdown-content text-sm`;
    });
    
    if (data.verdict) {
        let vText = data.verdict.toUpperCase();
        let vColor = 'white';
        if (vText.includes('GREEN')) vColor = '#34d399';
        else if (vText.includes('YELLOW')) vColor = '#fbbf24';
        else if (vText.includes('RED') || vText.includes('ABANDON') || vText.includes('PIVOT')) vColor = '#f87171';
        document.getElementById('rep-verdict').style.color = vColor;
    }

    
    // Re-init Follow-up agent automatically
    followupHistory = history || [];
    const histEl = document.getElementById('followup-chat-history');
    histEl.innerHTML = '';
    
    if (followupHistory.length > 0) {
        followupHistory.forEach(msg => {
            if (msg.role === 'user') {
                histEl.innerHTML += `<div style="background:rgba(255,255,255,0.1); padding:10px; border-radius:8px; margin-bottom:8px; align-self:flex-end; color:white; font-size:0.9rem;">${escapeHTML(msg.content)}</div>`;
            } else {
                histEl.innerHTML += `<div style="background:rgba(59,130,246,0.1); border-left:3px solid #3b82f6; padding:10px; border-radius:8px; margin-bottom:8px; color:#e2e8f0; font-size:0.9rem; line-height:1.5;">${marked.parse(msg.content)}</div>`;
            }
        });
        histEl.scrollTop = histEl.scrollHeight;
    } else {
        sendFollowupMessage(true); // silent seed
    }
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

// Phase 4: Architect Generation (Interactive State Machine)
let currentArchitectLoop = 0;

async function startArchitectPipeline() {
    const btn = document.getElementById('build-blueprint-btn');
    btn.innerHTML = `<span class='loading-dots'>Allocating Resources...</span>`;
    btn.disabled = true;
    
    document.getElementById('intelligence-dashboard').style.display = 'none';
    document.getElementById('architect-workbench').style.display = 'flex';
    
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });
    await loadArchitectState();
}

async function loadArchitectState() {
    try {
        // Step 1: Normal Architect State (Theme review happens before Intel Report now)
        const res = await fetch(`/api/architect/state/${currentProjectId}`);
        const state = await res.json();
        currentArchitectLoop = state.current_loop;
        
        if (currentArchitectLoop === 0 && !state.loop0_draft) {
            await triggerArchitectLoop(0);
        } else if (currentArchitectLoop === 1 && !state.loop1_draft) {
            await triggerArchitectLoop(1);
        } else if (currentArchitectLoop === 2 && !state.loop2_draft) {
            await triggerArchitectLoop(2);
        } else {
            renderWorkbenchState(state);
        }
    } catch (e) {
        console.error(e);
        alert("Failed to load architect state.");
    }
}

function renderThemeConsolidationState(themes, needsConsolidation) {
    document.getElementById('workbench-refine-btn').style.display = 'none';
    document.getElementById('workbench-feedback').style.display = 'none';
    
    document.getElementById('workbench-loop-badge').innerText = `Pre-Flight`;
    document.getElementById('workbench-draft-title').innerText = "High-Fidelity Theme Review";
    
    if (needsConsolidation) {
        document.getElementById('workbench-approve-btn').innerText = "Consolidate Raw Themes";
        document.getElementById('workbench-draft-content').innerHTML = `
            <div style="padding: 20px;">
                <h3 style="color: #fbbf24; margin-top:0;">Raw Fragments Detected</h3>
                <p style="color:#cbd5e1;">You have captured notes and brainstorm fragments that have not yet been synthesized into a High-Fidelity story.</p>
                <p style="color:#cbd5e1;">Click <strong>Consolidate Raw Themes</strong> below to instantly process them into clean, cohesive Knowledge Base chapters before the Architect begins.</p>
            </div>
        `;
    } else {
        document.getElementById('workbench-approve-btn').innerText = "Approve Knowledge Base";
        let html = `<div style="padding: 10px;">
            <p style="color:#94a3b8; font-size:0.9rem; margin-top:0;">Please review the High-Fidelity Knowledge Base below. If you need to make changes, use the 🧠 Agentic Memory editor drawer on the right. Once satisfied, click Approve.</p>
        `;
        themes.forEach(t => {
            html += `<details style="margin-bottom: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <summary style="padding: 12px; cursor: pointer; font-weight: bold; color: #38bdf8;">${t.theme_name}</summary>
                <div style="padding: 12px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.9rem; color: #f1f5f9;">
                    ${marked.parse(t.content || "No content")}
                </div>
            </details>`;
        });
        html += `</div>`;
        document.getElementById('workbench-draft-content').innerHTML = html;
    }
}

async function triggerArchitectLoop(loopIndex, feedback = "") {
    document.getElementById('workbench-draft-content').innerHTML = `<span class='loading-dots'>Architect is thinking...</span>`;
    document.getElementById('workbench-refine-btn').disabled = true;
    document.getElementById('workbench-approve-btn').disabled = true;
    
    const ideSelectorValue = document.getElementById('ide-selector') ? document.getElementById('ide-selector').value : "Antigravity";
    
    const payload = {
        target_platform: ideSelectorValue,
        designer_name: document.getElementById('config-designer').value || "Unknown",
        app_name: currentProjectName,
        app_purpose: document.getElementById('config-purpose').value || "N/A",
        target_audience: document.getElementById('config-audience').value || "N/A",
        app_type: document.getElementById('config-apptype').value || "Commercial",
        build_environment: document.getElementById('config-environment') ? document.getElementById('config-environment').value : "Greenfield (New)",
        budget_constraints: document.getElementById('config-budget').value || "N/A",
        ai_integration: document.getElementById('config-ai_integration').value || "N/A",
        security_auth: document.getElementById('config-security').value || "N/A",
        standout_features: JSON.parse(document.getElementById('config-features').value || "[]"),
        project_id: currentProjectId,
        feedback: feedback
    };
    
    try {
        let endpoint = `/api/architect/loop${loopIndex}`;
        if (loopIndex >= 3) endpoint = `/api/architect/loop3_4`;
        
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error("Failed to generate loop");
        
        if (loopIndex >= 3) {
            document.getElementById('workbench-draft-content').innerHTML = `<div style='text-align:center; padding: 40px;'><h3 style='color:#34d399;'>Compiling Final Architect Blueprint</h3><p style='color:#94a3b8;'>Building remaining chapters (Database, API, UI). This process will take 1-2 minutes.<br>You will be automatically redirected to the PDF Viewer when complete.</p><div class='loading-state'></div></div>`;
            return;
        }
        
        const data = await res.json();
        currentArchitectLoop = data.current_loop;
        
        // Fetch full state again to render
        await loadArchitectState();
    } catch (e) {
        alert(e.message);
        document.getElementById('workbench-draft-content').innerHTML = `Error: ${e.message}`;
        document.getElementById('workbench-refine-btn').disabled = false;
    }
}

function renderWorkbenchState(state) {
    document.getElementById('workbench-refine-btn').style.display = 'block';
    document.getElementById('workbench-feedback').style.display = 'block';
    document.getElementById('workbench-refine-btn').disabled = false;
    document.getElementById('workbench-approve-btn').disabled = false;
    document.getElementById('workbench-feedback').value = "";
    
    const loopNames = ["Loop 0: Layman's App Overview", "Loop 1: System Workflow Mapping", "Loop 2: Tech Stack Skeleton", "Compiling Final Blueprint"];
    const btnNames = ["Approve Overview", "Approve Workflow", "Approve Foundation", "Processing..."];
    
    document.getElementById('workbench-loop-badge').innerText = `Loop ${state.current_loop}`;
    document.getElementById('workbench-draft-title').innerText = loopNames[state.current_loop] || "Finalizing...";
    document.getElementById('workbench-approve-btn').innerText = btnNames[state.current_loop] || "Finish";
    
    let draftHtml = "";
    if (state.current_loop === 0) draftHtml = marked.parse(state.loop0_draft || "");
    else if (state.current_loop === 1) draftHtml = marked.parse(state.loop1_draft || "");
    else if (state.current_loop === 2) draftHtml = marked.parse(state.loop2_draft || "");
    
    document.getElementById('workbench-draft-content').innerHTML = draftHtml;
    
    // Render mermaid if present
    setTimeout(() => {
        try { mermaid.init(undefined, document.querySelectorAll('.language-mermaid')); } catch(e) {}
    }, 100);
}

document.getElementById('workbench-refine-btn')?.addEventListener('click', () => {
    if (currentArchitectLoop === -1) return; // Hidden in loop -1
    const fb = document.getElementById('workbench-feedback').value;
    triggerArchitectLoop(currentArchitectLoop, fb);
});

document.getElementById('workbench-approve-btn')?.addEventListener('click', async () => {
    if (currentArchitectLoop === -1) {
        const btnText = document.getElementById('workbench-approve-btn').innerText;
        if (btnText === "Consolidate Raw Themes") {
            document.getElementById('workbench-draft-content').innerHTML = `<span class='loading-dots'>Synthesizing High-Fidelity Knowledge Base...</span>`;
            document.getElementById('workbench-approve-btn').disabled = true;
            await fetch(`/api/architect/consolidate-themes`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({project_id: currentProjectId})
            });
            await checkAndReviewThemes();
        } else {
            window.themesApproved = true;
            document.getElementById('architect-workbench').style.display = 'none';
            document.getElementById('onboarding-screen').style.display = 'flex'; // show onboarding so generateIntelligence can hide it and show progress
            await generateIntelligence();
        }
        return;
    }
    
    const nextLoop = currentArchitectLoop + 1;
    triggerArchitectLoop(nextLoop, "");
});

// Blueprint Viewer Route
function showBlueprint(markdownText) {
    document.getElementById('intelligence-dashboard').style.display = 'none';
    document.getElementById('onboarding-screen').style.display = 'none';
    document.getElementById('architect-workbench').style.display = 'none';
    document.getElementById('blueprint-viewer').style.display = 'flex';
    
    // Store the raw markdown globally for the export button
    window.currentBlueprintMarkdown = markdownText;
    
    document.getElementById('blueprint-content').innerHTML = marked.parse(markdownText);
    
    // Add Copy Buttons to Blueprint
    addCopyButtonsToPreTags('blueprint-content');
    
    // Attach blueprint checkboxes
    const checkboxes = document.querySelectorAll('.blueprint-checkbox');
    checkboxes.forEach(cb => {
        const stepIdx = parseInt(cb.getAttribute('data-idx'));
        if (stepIdx < (window.currentVibeStep || 0)) {
            cb.checked = true;
            cb.closest('h2').style.opacity = '0.6';
        }
        cb.addEventListener('change', async (e) => {
            const checked = e.target.checked;
            const newStep = checked ? stepIdx + 1 : stepIdx;
            try {
                await fetch(`/api/projects/${currentProjectId}/vibe-step`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ step: newStep })
                });
                window.currentVibeStep = newStep;
                document.querySelectorAll('.blueprint-checkbox').forEach(box => {
                    const idx = parseInt(box.getAttribute('data-idx'));
                    box.checked = (idx < newStep);
                    if (box.closest('h2')) {
                        box.closest('h2').style.opacity = box.checked ? '0.6' : '1';
                    }
                });
            } catch(err) { console.error("Failed to save blueprint step", err); }
        });
    });
    
    // Mount Markdown Exporter
    const mdBtn = document.getElementById('blueprint-export-md');
    if (mdBtn) {
        const newMdBtn = mdBtn.cloneNode(true);
        mdBtn.parentNode.replaceChild(newMdBtn, mdBtn);
        newMdBtn.addEventListener('click', () => {
            if (!window.currentBlueprintMarkdown) {
                alert("Blueprint markdown not fully loaded yet.");
                return;
            }
            const blob = new Blob([window.currentBlueprintMarkdown], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'SynapseIP_Master_Blueprint.md';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        });
    }

    // Mount PDF Exporter
    const btn = document.getElementById('blueprint-export-pdf');
    // Clone trick to remove old event listeners
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);
    
    newBtn.addEventListener('click', () => {
        newBtn.innerText = "Exporting...";
        newBtn.disabled = true;
        
        const element = document.getElementById('blueprint-content');
        
        // Create an unconstrained clone to prevent height/scroll cropping by html2canvas
        const printContainer = document.createElement('div');
        printContainer.className = 'markdown-content';
        // Place behind the main app (z-index: -9999) so it's hidden from user but visible to html2canvas (no opacity: 0)
        printContainer.style.cssText = "font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; padding: 30px; width: 800px; background: white; color: black; position: absolute; top: 0; left: 0; z-index: -9999;";
        printContainer.innerHTML = element.innerHTML;
        document.body.appendChild(printContainer);
        
        const opt = {
            margin:       15,
            filename:     `Blueprint_${currentProjectName.replace(/\s+/g, '_')}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true, logging: false, windowWidth: 800, scrollX: 0, scrollY: 0 },
            jsPDF:        { unit: 'mm', format: 'letter', orientation: 'portrait' },
            pagebreak:    { mode: 'css', avoid: ['pre', 'h1', 'h2', 'h3', 'table', 'img', 'ul', 'ol', 'blockquote'] }
        };
        
        html2pdf().set(opt).from(printContainer).save().then(() => {
            document.body.removeChild(printContainer);
            newBtn.innerText = "Export Blueprint PDF";
            newBtn.disabled = false;
        }).catch(err => {
            console.error(err);
            if(document.body.contains(printContainer)) document.body.removeChild(printContainer);
            newBtn.innerText = "Export Failed";
            newBtn.disabled = false;
        });
    });
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
            
            const date = new Date(source.timestamp + (!source.timestamp.endsWith('Z') ? 'Z' : '')).toLocaleDateString(undefined, {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
            let sourceHost = "Extension";
            if(source.source_url) { try { sourceHost = new URL(source.source_url).hostname; } catch(e){} }

            const tempDiv = document.createElement('div'); tempDiv.innerHTML = source.content;
            const plainText = tempDiv.innerText || tempDiv.textContent || "";
            
            let smartTitle = source.title;
            if (!smartTitle || smartTitle.startsWith("Gemini Response") || smartTitle.startsWith("AI Source Node")) {
                let fallback = plainText.split(/[.\n]/)[0].replace(/[*_#>]/g, '').trim();
                smartTitle = fallback.length > 3 ? fallback : "Synced Note";
            }

            let bHTML = '';
            if (!source.processed) {
                if (smartTitle.startsWith("Processing 🔄")) {
                    bHTML = `<span style="font-size:0.7rem; background:rgba(245,158,11,0.2); color:#fbbf24; padding:2px 6px; border-radius:4px; margin-left:8px;">Processing 🔄</span>`;
                    smartTitle = smartTitle.replace("Processing 🔄 ", "").trim();
                } else {
                    bHTML = `<span style="font-size:0.7rem; background:rgba(59,130,246,0.2); color:#60a5fa; padding:2px 6px; border-radius:4px; margin-left:8px;">Queued ⏳</span>`;
                }
            } else if (source.title && (source.title.startsWith("AI Source Node") || source.title.includes("Processing Failed"))) {
                bHTML = `<button class="retry-ai-btn" data-id="${source.id}" onclick="retrySourceProcessing(${source.id}, event)" style="font-size:0.65rem; background:rgba(16,185,129,0.2); color:#10b981; border:1px solid rgba(16,185,129,0.3); padding:2px 6px; border-radius:4px; margin-left:8px; cursor:pointer; transition:all 0.2s;">Retry AI 🔄</button>`;
            }
            
            if (smartTitle.length > 50) smartTitle = smartTitle.substring(0, 50) + "...";
            card.id = `source-card-${source.id}`;
            card.innerHTML = `
                <div class="source-title"><span style="color:var(--accent-color); margin-right:6px;">#${index+1}</span>${escapeHTML(smartTitle)}${bHTML}</div>
                <div class="source-time">${sourceHost} &bull; ${date}</div>
                <div class="source-preview">${escapeHTML(plainText)}</div>
                <div id="card-progress-${source.id}" class="card-progress-overlay" style="display:none;">
                    <div class="card-progress-text">
                        <span id="card-progress-msg-${source.id}">Waiting...</span>
                        <span id="card-progress-pct-${source.id}" style="color: var(--accent-color);">0%</span>
                    </div>
                    <div class="progress-bar-track card-progress-track">
                        <div id="card-progress-fill-${source.id}" class="progress-bar-fill card-progress-fill" style="width: 0%;"></div>
                    </div>
                </div>
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

window.retrySourceProcessing = async function(id, event) {
    event.stopPropagation();
    try {
        const btn = event.target;
        btn.innerText = "Queuing...";
        btn.disabled = true;
        
        const res = await fetch(`/api/sources/${id}/reprocess`, {
            method: 'POST'
        });
        
        if (res.ok) {
            btn.style.background = 'rgba(59,130,246,0.2)';
            btn.style.color = '#60a5fa';
            btn.style.borderColor = 'rgba(59,130,246,0.3)';
            btn.innerText = "Queued ⏳";
        } else {
            btn.innerText = "Failed ✗";
        }
    } catch(e) {
        console.error("Retry failed:", e);
    }
}

window.reprocessMissedCards = async function() {
    if (!currentProjectId) return;
    try {
        const btn = document.getElementById('reprocess-missed-btn');
        const oldText = btn.innerText;
        btn.innerText = "⏳";
        btn.disabled = true;
        
        const res = await fetch(`/api/projects/${currentProjectId}/retry-missed`, {
            method: 'POST'
        });
        
        if (res.ok) {
            btn.innerText = "✅";
            setTimeout(() => { btn.innerText = oldText; btn.disabled = false; }, 2000);
            fetchSources();
        } else {
            btn.innerText = "❌";
            setTimeout(() => { btn.innerText = oldText; btn.disabled = false; }, 2000);
        }
    } catch(e) {
        console.error("Bulk retry failed:", e);
    }
}

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "architect_complete") {
                const btn = document.getElementById('build-blueprint-btn');
                if (btn) {
                    btn.innerHTML = `Build Architect Blueprint (PDF)`;
                    btn.disabled = false;
                }
                
                // Store raw markdown for the download button
                if (data.markdown_content) {
                    window.currentBlueprintMarkdown = data.markdown_content;
                }
                
                // Terminate global tracker
                document.getElementById('global-activity-tracker').style.display = 'none';
                
                // Force invalidate and auto-refresh project dropdown cache
                const nested = document.getElementById(`nested-${currentProjectId}`);
                if (nested) {
                    delete nested.dataset.loaded;
                    loadProjectDocuments(currentProjectId);
                }
                
                // Automatically open the PDF Architect Document View in UI
                if (data.markdown_content) {
                    showBlueprint(data.markdown_content);
                }
            } else if (data.type === "progress" || data.type === "source_progress") {
                const overlay = document.getElementById(`card-progress-${data.source_id}`);
                if (overlay) {
                    overlay.style.display = 'flex';
                    document.getElementById(`card-progress-pct-${data.source_id}`).innerText = `${data.progress}%`;
                    document.getElementById(`card-progress-msg-${data.source_id}`).innerText = data.message;
                    document.getElementById(`card-progress-fill-${data.source_id}`).style.width = `${data.progress}%`;
                } else if (data.type === "progress") {
                    // Fallback for non-source progress (like Architect generation)
                    const tracker = document.getElementById('global-activity-tracker');
                    if (tracker) {
                        tracker.style.display = 'flex';
                        document.getElementById('global-tracker-pct').innerText = `${data.progress}%`;
                        document.getElementById('global-tracker-msg').innerText = data.message;
                        document.getElementById('global-tracker-fill').style.width = `${data.progress}%`;
                    }
                }
                
            } else if (data.type === "source_progress_complete") {
                const overlay = document.getElementById(`card-progress-${data.source_id}`);
                if (overlay) overlay.style.display = 'none';
            } else if (data.type === "sources_deleted") {
                fetchSources();
            }
            return;
        } catch (e) {}

        if (event.data === "new_source") {
            if (window._syncTimer) clearTimeout(window._syncTimer);
            window._syncTimer = setTimeout(() => fetchSources(), 300);
        } else if (event.data === "themes_updated") {
            // Hide global tracker
            document.getElementById('global-activity-tracker').style.display = 'none';

            loadThemesCompass();
        } else if (event.data === "token_update") fetchTokenStats();
    };
    
    const handleDisconnect = () => {
        if (!document.getElementById('ws-warning')) {
            const warning = document.createElement('div');
            warning.id = 'ws-warning';
            warning.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; background: #ef4444; color: white; text-align: center; padding: 10px; z-index: 9999; font-weight: bold; cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.5);';
            warning.innerHTML = '⚠️ Live connection lost. Click here to refresh the page.';
            warning.onclick = () => window.location.reload();
            document.body.appendChild(warning);
        }
    };
    
    ws.onclose = handleDisconnect;
    ws.onerror = handleDisconnect;
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

function escapeHTML(str) { const p = document.createElement("p"); p.appendChild(document.createTextNode(str)); return p.innerHTML; }

// --- Brainstorming Compass ---
async function loadThemesCompass() {
    if (!currentProjectId) return;
    try {
        const res = await fetch(`/api/projects/${currentProjectId}/themes_dashboard`);
        if (!res.ok) return;
        const data = await res.json();
        
        document.getElementById('brainstorming-compass').style.display = 'block';
        
        if (data.onboarding_config) {
            restoreOnboardingConfig(data.onboarding_config);
        } else {
            // Reset UI if it was previously restored in DOM
            const setDisplay = (id, val) => { const el = document.getElementById(id); if (el) el.style.display = val; };
            setDisplay('chat-history', 'flex');
            setDisplay('chat-input-area', 'flex');
            setDisplay('command-bar', 'none');
            
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                chatInput.disabled = false;
                chatInput.placeholder = "Answer the agent or share your vision...";
                chatInput.style.opacity = "1";
            }
        }
        
        const badge = document.getElementById('consistency-badge');
        const btn = document.getElementById('btn-consistency-check');
        if (data.is_consistent) {
            badge.style.display = 'inline-block';
            btn.innerHTML = 'Check Passed ✅';
            btn.style.opacity = '0.5';
            btn.style.pointerEvents = 'none';
        } else {
            badge.style.display = 'none';
            btn.innerHTML = '✨ Run Global Consistency Check';
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        }
        
        const activeUl = document.getElementById('compass-active-themes');
        const suggestedUl = document.getElementById('compass-suggested-themes');
        
        activeUl.innerHTML = '';
        suggestedUl.innerHTML = '';
        
        if (data.active_themes.length === 0) {
            activeUl.innerHTML = '<li style="opacity: 0.5;">No themes captured yet. Sync a note to begin.</li>';
        } else {
            data.active_themes.forEach(t => {
                activeUl.innerHTML += `<li><span style="color: #34d399; margin-right: 8px;">✓</span> ${escapeHTML(t)}</li>`;
            });
        }
        
        if (data.suggested_themes.length === 0) {
            if (data.active_themes.length > 0) {
                suggestedUl.innerHTML = '<li style="opacity: 0.5;">Syncing more notes...</li>';
            } else {
                suggestedUl.innerHTML = '<li style="opacity: 0.5;">Waiting for first sync...</li>';
            }
        } else {
            data.suggested_themes.forEach(t => {
                suggestedUl.innerHTML += `<li><span style="color: #f59e0b; margin-right: 8px;">!</span> ${escapeHTML(t)}</li>`;
            });
        }
    } catch(e) { console.error("Themes compass error:", e); }
}

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

// --- Consistency Check ---
document.getElementById('btn-consistency-check')?.addEventListener('click', async () => {
    if (!currentProjectId) {
        alert("Please select a project first.");
        return;
    }
    const btn = document.getElementById('btn-consistency-check');
    const originalText = btn.innerText;
    btn.innerText = "✨ Running Check...";
    btn.disabled = true;
    
    try {
        const response = await fetch(`/api/projects/${currentProjectId}/consistency-check`, { method: 'POST' });
        if (!response.ok) throw new Error("Consistency Check failed to start.");
        // The backend will broadcast progress via WebSocket, which the UI picks up automatically!
    } catch (e) {
        alert(e.message);
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

// --- UI Mockup Generator ---
document.getElementById('btn-generate-mockup').addEventListener('click', async () => {
    if (!currentProjectId) {
        alert("Please select a project first.");
        return;
    }
    const btn = document.getElementById('btn-generate-mockup');
    const span = btn.querySelector('span');
    const originalText = span.innerText;
    span.innerText = "Generating Prompt...";
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/mockup/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: currentProjectId })
        });
        
        if (!response.ok) throw new Error("Generation failed.");
        const data = await response.json();
        
        document.getElementById('mockup-prompt-text').value = data.prompt;
        document.getElementById('mockup-modal').style.display = 'flex';
        
    } catch (e) {
        alert(e.message);
    } finally {
        span.innerText = originalText;
        btn.disabled = false;
    }
});

document.getElementById('close-mockup-modal').addEventListener('click', () => {
    document.getElementById('mockup-modal').style.display = 'none';
});

document.getElementById('btn-copy-mockup').addEventListener('click', async () => {
    const text = document.getElementById('mockup-prompt-text').value;
    try {
        await navigator.clipboard.writeText(text);
        const copyBtn = document.getElementById('btn-copy-mockup');
        copyBtn.innerText = "Copied!";
        copyBtn.style.background = "#34d399";
        setTimeout(() => {
            copyBtn.innerText = "Copy to Clipboard";
            copyBtn.style.background = "";
        }, 2000);
    } catch (err) {
        alert("Failed to copy clipboard");
    }
});

async function handleEditProject(e) {
    e.stopPropagation();
    if (!currentProjectId) return;
    
    const span = document.getElementById('active-project-name');
    const oldName = span.innerText;
    
    // Prevent double clicking
    if (span.querySelector('input')) return;
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'inline-edit-input';
    input.value = oldName;
    
    span.innerHTML = '';
    span.appendChild(input);
    input.focus();
    input.select();
    
    const saveNewName = async () => {
        const newName = input.value.trim();
        if (!newName || newName === oldName) {
            span.innerText = oldName;
            return;
        }
        
        // Optimistic UI update
        span.innerText = newName;
        document.getElementById('edit-project-btn').style.pointerEvents = 'none';
        
        try {
            const res = await fetch(`/api/projects/${currentProjectId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: newName})
            });
            if (!res.ok) throw new Error("Failed to rename");
            
            // Update cache
            const p = window.cachedProjects.find(p => p.id === currentProjectId);
            if (p) p.name = newName;
            
            // Re-render list
            renderProjectList(window.cachedProjects);
        } catch (e) {
            console.error(e);
            span.innerText = oldName;
            alert("Error renaming project");
        } finally {
            document.getElementById('edit-project-btn').style.pointerEvents = 'auto';
        }
    };
    
    input.addEventListener('blur', saveNewName);
    input.addEventListener('keypress', (evt) => {
        if (evt.key === 'Enter') {
            input.blur(); // Triggers saveNewName
        }
    });
}

// Utility: Add Copy Buttons to Code Blocks
function addCopyButtonsToPreTags(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const preTags = container.querySelectorAll('pre');
    preTags.forEach(pre => {
        if (pre.parentNode.classList.contains('code-wrapper')) return;
        
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';
        wrapper.style.position = 'relative';
        
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        copyBtn.innerText = 'Copy';
        copyBtn.title = 'Copy to clipboard';
        copyBtn.style.cssText = 'position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #cbd5e1; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; z-index: 10; display: flex; align-items: center; gap: 4px;';
        copyBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
        
        copyBtn.addEventListener('click', () => {
            const textToCopy = pre.innerText;
            navigator.clipboard.writeText(textToCopy).then(() => {
                copyBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;
                copyBtn.style.background = '#10b981';
                copyBtn.style.color = '#ffffff';
                copyBtn.style.borderColor = '#10b981';
                setTimeout(() => {
                    copyBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
                    copyBtn.style.background = 'rgba(255,255,255,0.1)';
                    copyBtn.style.color = '#cbd5e1';
                    copyBtn.style.borderColor = 'rgba(255,255,255,0.2)';
                }, 2000);
            });
        });
        
        wrapper.appendChild(copyBtn);
    });
}

// === Global Floating Chat & Highlight-to-Ask Logic ===
document.addEventListener('DOMContentLoaded', () => {
    const fab = document.getElementById('global-chat-fab');
    const panel = document.getElementById('floating-chat-panel');
    const closeBtn = document.getElementById('floating-chat-close');
    const chatInput = document.getElementById('followup-chat-input');
    
    // Toggle Chat Panel & Drag Logic
    if (fab && panel && closeBtn) {
        let isDragging = false;
        let startX, startY, initialX, initialY;

        fab.addEventListener('mousedown', (e) => {
            isDragging = false;
            startX = e.clientX;
            startY = e.clientY;
            initialX = fab.offsetLeft;
            initialY = fab.offsetTop;
            fab.style.transition = 'none'; // Disable transition for smooth dragging

            const onMouseMove = (moveEvent) => {
                const dx = moveEvent.clientX - startX;
                const dy = moveEvent.clientY - startY;

                if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
                    isDragging = true;
                    fab.style.bottom = 'auto';
                    fab.style.right = 'auto';
                    
                    let newX = initialX + dx;
                    let newY = initialY + dy;
                    
                    const maxW = window.innerWidth - fab.offsetWidth;
                    const maxH = window.innerHeight - fab.offsetHeight;
                    
                    if (newX < 0) newX = 0;
                    if (newY < 0) newY = 0;
                    if (newX > maxW) newX = maxW;
                    if (newY > maxH) newY = maxH;
                    
                    fab.style.left = `${newX}px`;
                    fab.style.top = `${newY}px`;
                    
                    // Keep panel anchored to the pill if possible
                    panel.style.bottom = 'auto';
                    panel.style.left = `${Math.max(10, Math.min(newX, window.innerWidth - panel.offsetWidth - 10))}px`;
                    panel.style.top = `${Math.max(10, newY - panel.offsetHeight - 10)}px`;
                }
            };

            const onMouseUp = () => {
                fab.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        fab.addEventListener('click', (e) => {
            if (isDragging) {
                e.preventDefault();
                e.stopPropagation();
                return;
            }
            panel.classList.toggle('active');
            if (panel.classList.contains('active') && chatInput) {
                setTimeout(() => chatInput.focus(), 100);
            }
        });
        
        closeBtn.addEventListener('click', () => {
            panel.classList.remove('active');
        });
    }
    
    // Highlight-to-Ask & Edit Tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'selection-tooltip';
    tooltip.innerHTML = `
        <div style="display: flex; gap: 8px;">
            <button id="tooltip-ask-ai" style="background: transparent; border: none; color: white; display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 13px; font-weight: 500; padding: 4px 8px; border-radius: 4px; transition: background 0.2s;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg> Ask AI
            </button>
            <div style="width: 1px; background: rgba(255,255,255,0.2);"></div>
            <button id="tooltip-edit-draft" style="background: transparent; border: none; color: white; display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 13px; font-weight: 500; padding: 4px 8px; border-radius: 4px; transition: background 0.2s;">
                ✨ Edit Draft
            </button>
        </div>
    `;
    tooltip.style.opacity = '0';
    tooltip.style.pointerEvents = 'none';
    document.body.appendChild(tooltip);
    
    // Add hover effects via JS since it's dynamically inserted inline styles
    const btnAskAi = document.getElementById('tooltip-ask-ai');
    const btnEditDraft = document.getElementById('tooltip-edit-draft');
    [btnAskAi, btnEditDraft].forEach(btn => {
        btn.addEventListener('mouseenter', () => btn.style.background = 'rgba(255,255,255,0.1)');
        btn.addEventListener('mouseleave', () => btn.style.background = 'transparent');
    });
    
    let currentSelection = '';
    
    document.addEventListener('mouseup', (e) => {
        // Prevent tooltip from showing when clicking inside tooltip or chat panel or modal
        if (e.target.closest('.selection-tooltip') || e.target.closest('.floating-chat-panel') || e.target.closest('#blueprint-edit-modal')) return;
        
        setTimeout(() => {
            const selection = window.getSelection();
            const text = selection.toString().trim();
            
            // Only show if we are inside blueprint-viewer (for edit) or generally (for ask ai)
            // But let's restrict it to the whole document for Ask AI, and just enable Edit Draft if in blueprint.
            if (text.length > 5) {
                currentSelection = text;
                const range = selection.getRangeAt(0);
                const rect = range.getBoundingClientRect();
                
                // Position tooltip above the selection
                tooltip.style.left = `${rect.left + (rect.width / 2)}px`;
                tooltip.style.top = `${rect.top + window.scrollY - 45}px`;
                tooltip.style.transform = 'translateX(-50%)';
                tooltip.style.opacity = '1';
                tooltip.style.pointerEvents = 'auto';
                
                // Show/hide Edit Draft depending on if selection is in blueprint content
                const blueprintContent = document.getElementById('blueprint-content');
                if (blueprintContent && blueprintContent.contains(selection.anchorNode)) {
                    btnEditDraft.style.display = 'flex';
                    tooltip.querySelector('div > div').style.display = 'block'; // the separator
                } else {
                    btnEditDraft.style.display = 'none';
                    tooltip.querySelector('div > div').style.display = 'none';
                }
            } else {
                tooltip.style.opacity = '0';
                tooltip.style.pointerEvents = 'none';
            }
        }, 10);
    });
    
    // Hide tooltip on mousedown
    document.addEventListener('mousedown', (e) => {
        if (!e.target.closest('.selection-tooltip') && !e.target.closest('.floating-chat-panel') && !e.target.closest('#blueprint-edit-modal')) {
            tooltip.style.opacity = '0';
            tooltip.style.pointerEvents = 'none';
        }
    });
    
    // Ask AI Click Handler
    btnAskAi.addEventListener('click', () => {
        tooltip.style.opacity = '0';
        tooltip.style.pointerEvents = 'none';
        
        if (panel && chatInput) {
            panel.classList.add('active');
            chatInput.value = `> "${currentSelection}"\n\n`;
            chatInput.focus();
            
            // Clear selection
            window.getSelection().removeAllRanges();
        }
    });
    
    // Edit Draft Click Handler
    btnEditDraft.addEventListener('click', () => {
        tooltip.style.opacity = '0';
        tooltip.style.pointerEvents = 'none';
        
        const blueprintEditModal = document.getElementById('blueprint-edit-modal');
        const blueprintEditPreview = document.getElementById('blueprint-edit-preview');
        const blueprintEditInstructions = document.getElementById('blueprint-edit-instructions');
        
        if (blueprintEditModal) {
            blueprintEditPreview.textContent = currentSelection;
            blueprintEditInstructions.value = "";
            blueprintEditModal.style.display = 'flex';
        }
    });

    // Theme Editor Drawer
    const btnThemeEditor = document.getElementById('btn-theme-editor');
    const themeDrawer = document.getElementById('theme-drawer');
    const themeDrawerOverlay = document.getElementById('theme-drawer-overlay');
    const closeThemeDrawer = document.getElementById('close-theme-drawer');
    const drawerThemeList = document.getElementById('drawer-theme-list');
    
    const themeListView = document.getElementById('theme-list-view');
    const themeEditView = document.getElementById('theme-edit-view');
    const backToThemesBtn = document.getElementById('back-to-themes');
    const editingThemeName = document.getElementById('editing-theme-name');
    const themeEditTextarea = document.getElementById('theme-edit-textarea');
    const btnSyncTheme = document.getElementById('btn-sync-theme');
    const editingThemeId = document.getElementById('editing-theme-id');

    async function fetchAndRenderThemes() {
        if (!currentProjectId) return;
        const token = localStorage.getItem('synapseip_token');
        try {
            drawerThemeList.innerHTML = '<div style="color: #64748b; text-align: center; padding: 20px;">Loading themes...</div>';
            const res = await fetch(`/api/projects/${currentProjectId}/themes`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error("Failed to load themes");
            const themes = await res.json();
            
            drawerThemeList.innerHTML = '';
            if (themes.length === 0) {
                drawerThemeList.innerHTML = '<div style="color: #64748b; text-align: center; padding: 20px;">No themes synthesized yet.</div>';
                return;
            }
            
            themes.forEach(t => {
                const div = document.createElement('div');
                div.style.padding = '15px';
                div.style.background = 'rgba(255,255,255,0.02)';
                div.style.border = '1px solid var(--glass-border)';
                div.style.borderRadius = '8px';
                div.style.cursor = 'pointer';
                div.style.transition = 'all 0.2s';
                
                div.addEventListener('mouseover', () => div.style.background = 'rgba(255,255,255,0.05)');
                div.addEventListener('mouseout', () => div.style.background = 'rgba(255,255,255,0.02)');
                
                div.innerHTML = `<h4 style="margin: 0 0 5px 0; color: #f1f5f9;">${t.theme_name}</h4>
                                 <p style="margin: 0; font-size: 0.8rem; color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${t.content.substring(0, 80)}...</p>`;
                
                div.addEventListener('click', () => {
                    themeListView.style.display = 'none';
                    themeEditView.style.display = 'flex';
                    editingThemeName.innerText = t.theme_name;
                    themeEditTextarea.value = t.content;
                    editingThemeId.value = t.id;
                });
                
                drawerThemeList.appendChild(div);
            });
            
        } catch (e) {
            console.error(e);
            drawerThemeList.innerHTML = '<div style="color: #ef4444; text-align: center; padding: 20px;">Failed to load themes.</div>';
        }
    }

    if (btnThemeEditor) {
        btnThemeEditor.addEventListener('click', () => {
            themeDrawer.style.right = '0';
            themeDrawerOverlay.style.display = 'block';
            setTimeout(() => themeDrawerOverlay.style.opacity = '1', 10);
            fetchAndRenderThemes();
        });
    }

    const closeDrawer = () => {
        themeDrawer.style.right = '-450px';
        themeDrawerOverlay.style.opacity = '0';
        setTimeout(() => themeDrawerOverlay.style.display = 'none', 300);
        setTimeout(() => {
            themeListView.style.display = 'block';
            themeEditView.style.display = 'none';
        }, 300);
    };

    if (closeThemeDrawer) closeThemeDrawer.addEventListener('click', closeDrawer);
    if (themeDrawerOverlay) themeDrawerOverlay.addEventListener('click', closeDrawer);

    if (backToThemesBtn) {
        backToThemesBtn.addEventListener('click', () => {
            themeListView.style.display = 'block';
            themeEditView.style.display = 'none';
        });
    }

    if (btnSyncTheme) {
        btnSyncTheme.addEventListener('click', async () => {
            const tId = editingThemeId.value;
            const content = themeEditTextarea.value;
            if (!tId || !currentProjectId) return;
            
            btnSyncTheme.innerText = 'Syncing...';
            btnSyncTheme.style.opacity = '0.7';
            
            const token = localStorage.getItem('synapseip_token');
            try {
                const res = await fetch(`/api/projects/${currentProjectId}/themes/${tId}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content: content })
                });
                
                if (res.ok) {
                    btnSyncTheme.innerText = 'Synced! ✅';
                    setTimeout(() => {
                        btnSyncTheme.innerText = 'Sync to Brain 🧠';
                        btnSyncTheme.style.opacity = '1';
                        fetchAndRenderThemes();
                        themeListView.style.display = 'block';
                        themeEditView.style.display = 'none';
                    }, 1500);
                } else {
                    throw new Error("Failed");
                }
            } catch (e) {
                console.error(e);
                btnSyncTheme.innerText = 'Error ❌';
                setTimeout(() => {
                    btnSyncTheme.innerText = 'Sync to Brain 🧠';
                    btnSyncTheme.style.opacity = '1';
                }, 2000);
            }
        });
    }
    const btnPruneVectors = document.getElementById('btn-prune-vectors');
    if (btnPruneVectors) {
        btnPruneVectors.addEventListener('click', async () => {
            const token = localStorage.getItem('synapseip_token');
            btnPruneVectors.innerText = 'Pruning...';
            btnPruneVectors.style.opacity = '0.7';
            
            try {
                const res = await fetch('/api/admin/prune-vectors', {
                    method: 'POST',
                    headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                });
                if (res.ok) {
                    btnPruneVectors.innerText = 'Pruning Started ✅';
                } else {
                    throw new Error("Failed");
                }
            } catch (e) {
                console.error(e);
                btnPruneVectors.innerText = 'Error ❌';
            }
            
            setTimeout(() => {
                btnPruneVectors.innerText = 'Prune Drift 🧹';
                btnPruneVectors.style.opacity = '1';
            }, 3000);
        });
    }
    
    // --- Blueprint Interactive Editor Logic ---
    const blueprintViewer = document.getElementById('blueprint-viewer');
    const blueprintContent = document.getElementById('blueprint-content');
    const blueprintEditModal = document.getElementById('blueprint-edit-modal');
    const blueprintEditPreview = document.getElementById('blueprint-edit-preview');
    const blueprintEditInstructions = document.getElementById('blueprint-edit-instructions');
    const btnCloseBlueprintModal = document.getElementById('close-blueprint-modal');
    const btnCancelBlueprintModal = document.getElementById('cancel-blueprint-modal');
    const btnSubmitBlueprintEdit = document.getElementById('submit-blueprint-edit');

    if (blueprintContent && blueprintEditModal) {
        const closeEditModal = () => {
            blueprintEditModal.style.display = 'none';
        };
        
        if (btnCloseBlueprintModal) btnCloseBlueprintModal.addEventListener('click', closeEditModal);
        if (btnCancelBlueprintModal) btnCancelBlueprintModal.addEventListener('click', closeEditModal);
        
        if (btnSubmitBlueprintEdit) {
            btnSubmitBlueprintEdit.addEventListener('click', async () => {
                const instructions = blueprintEditInstructions.value.trim();
                
                // Get the formatting preference
                const formatPrefRadio = document.querySelector('input[name="format-pref"]:checked');
                const containerPref = formatPrefRadio ? formatPrefRadio.value : "auto";
                
                if (!instructions && containerPref === "auto") {
                    alert("Please provide instructions for the AI, or select a formatting preference to auto-reformat the text.");
                    return;
                }
                
                btnSubmitBlueprintEdit.innerText = "Applying... ⏳";
                btnSubmitBlueprintEdit.disabled = true;
                btnSubmitBlueprintEdit.style.opacity = '0.7';
                
                try {
                    const res = await fetch('/api/architect/edit-blueprint', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            project_id: currentProjectId,
                            highlighted_text: blueprintEditPreview.textContent,
                            instructions: instructions,
                            container_preference: containerPref
                        })
                    });
                    
                    const data = await res.json();
                    if (data.success) {
                        alert("Blueprint updated successfully!");
                        closeEditModal();
                        
                        // Re-render blueprint
                        window.currentBlueprintMarkdown = data.updated_markdown;
                        document.getElementById('blueprint-content').innerHTML = marked.parse(data.updated_markdown);
                        addCopyButtonsToPreTags('blueprint-content');
                        
                        // We do not refresh checkboxes here to prevent wiping out state, unless needed.
                    } else {
                        throw new Error(data.error || "Failed to update blueprint");
                    }
                } catch (e) {
                    console.error(e);
                    alert("Error editing blueprint: " + e.message);
                } finally {
                    btnSubmitBlueprintEdit.innerText = "Apply Changes";
                    btnSubmitBlueprintEdit.disabled = false;
                    btnSubmitBlueprintEdit.style.opacity = '1';
                }
            });
        }
    }
});
