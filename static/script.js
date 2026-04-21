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
        
        // Removed hover, converted to Click-dependent Slide-Out Accordion
        li.addEventListener('click', (e) => {
            // Only select project if not clicking on nested menu items
            if (e.target.closest('.nested-menu')) return;
            
            // Slide out the nested documents menu!
            li.classList.toggle('expanded');
            if (li.classList.contains('expanded')) loadProjectDocuments(p.id);
            
            selectProject(p.id, p.name, true);
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
                    renderDashboard(report.data);
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

async function selectProject(projectId, projectName, silent = false) {
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
    
    try {
        const res = await fetch(`/api/projects/${projectId}/documents`);
        if (res.ok) {
            const data = await res.json();
            
            if (silent) return; // Wait! If it's a silent select, skip the auto-redirection block entirely!
            
            // Automatically surface the most recent blueprint if it exists
            if (data.blueprints && data.blueprints.length > 0) {
                showBlueprint(data.blueprints[0].data);
                return;
            }
            // Automatically surface the most recent intelligence report if it exists
            if (data.intelligence && data.intelligence.length > 0) {
                renderDashboard(data.intelligence[0].data);
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
    document.getElementById('generate-btn').addEventListener('click', generateIntelligence);
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
        // MOCKED AI FOR TESTING
        await new Promise(r => setTimeout(r, 300));
        const data = {
            message: "AI Onboarding temporarily disabled for extension testing. Proceeding natively...",
            is_complete: true,
            designer_name: "Testing Dev",
            core_purpose: "Extension Architecture"
        };
        
        chatHistoryEl.removeChild(thinkingBubble);
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
            body: JSON.stringify({ 
                target_platform: "Antigravity",
                project_id: currentProjectId,
                app_name: document.getElementById('config-appname').value,
                designer_name: document.getElementById('config-designer').value,
                app_purpose: document.getElementById('config-purpose').value,
                target_audience: document.getElementById('config-audience').value,
                app_type: document.getElementById('config-apptype').value,
                budget_constraints: document.getElementById('config-budget').value,
                standout_features: JSON.parse(document.getElementById('config-features').value || "[]")
            })
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
                app_purpose: "Automated via Follow-Up",
                target_audience: "N/A",
                app_type: "Commercial",
                standout_features: [],
                project_id: currentProjectId
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
        printContainer.style.cssText = "font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; padding: 20px; width: 800px; position: absolute; left: -9999px; top: 0; background: white; color: black;";
        printContainer.innerHTML = element.innerHTML;
        document.body.appendChild(printContainer);
        
        const opt = {
            margin:       15,
            filename:     `Blueprint_${currentProjectName.replace(/\s+/g, '_')}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true, logging: false, windowWidth: 800 },
            jsPDF:        { unit: 'mm', format: 'letter', orientation: 'portrait' },
            pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
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

        let hasProcessing = false;
        data.forEach((source, index) => {
            const card = document.createElement('div');
            card.className = 'source-card';
            
            const date = new Date(source.timestamp + (!source.timestamp.endsWith('Z') ? 'Z' : '')).toLocaleDateString(undefined, {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
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

            let bHTML = '';
            if (!source.processed) {
                if (!hasProcessing) {
                    bHTML = `<span style="font-size:0.7rem; background:rgba(245,158,11,0.2); color:#fbbf24; padding:2px 6px; border-radius:4px; margin-left:8px;">Processing 🔄</span>`;
                    hasProcessing = true;
                } else {
                    bHTML = `<span style="font-size:0.7rem; background:rgba(59,130,246,0.2); color:#60a5fa; padding:2px 6px; border-radius:4px; margin-left:8px;">Queued ⏳</span>`;
                }
            }
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
                if (btn) {
                    btn.innerHTML = `Build Architect Blueprint (PDF)`;
                    btn.disabled = false;
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
            } else if (data.type === "progress") {
                // Ensure UI tracker is visible globally
                const tracker = document.getElementById('global-activity-tracker');
                tracker.style.display = 'flex';
                document.getElementById('global-tracker-pct').innerText = `${data.progress}%`;
                document.getElementById('global-tracker-msg').innerText = data.message;
                document.getElementById('global-tracker-fill').style.width = `${data.progress}%`;
                
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
