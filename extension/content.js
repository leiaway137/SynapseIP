console.log("SynapseIP Messenger: Stealth Content Script loaded on", window.location.hostname);

// Inject persistent CSS for the synced state
const style = document.createElement('style');
style.textContent = `
    .synapseip-synced-btn {
        background-color: rgba(16, 185, 129, 0.2) !important;
        color: #10b981 !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    .synapseip-synced-btn svg, 
    .synapseip-synced-btn path, 
    .synapseip-synced-btn mat-icon, 
    .synapseip-synced-btn span {
        fill: #10b981 !important;
        color: #10b981 !important;
    }
`;
document.head.appendChild(style);

function getMessageContainers() {
    const activeHost = window.location.hostname.replace('www.', '');
    let rawContainers = [];
    
    // NOTEBOOKLM STRUCTURAL DOM PARSER
    if (activeHost.includes("notebooklm")) {
        const actionButtons = Array.from(document.querySelectorAll('button, [role="button"], [aria-label], [title], [mattooltip]'))
            .filter(b => {
                const t = (b.innerText || "").toLowerCase();
                const a = (b.getAttribute('aria-label') || "").toLowerCase();
                const title = (b.getAttribute('title') || "").toLowerCase();
                const tooltip = (b.getAttribute('mattooltip') || "").toLowerCase();
                return t.includes('save to note') || t.includes('export') || a.includes('bad') || title.includes('bad') || tooltip.includes('bad') || a.includes('save to note') || tooltip.includes('save to note') || t.includes('copy') || a.includes('copy');
            });
        
        rawContainers = actionButtons.map(btn => {
            return btn.closest('article, div[class*="message"]:not([class*="messages"]):not([class*="wrapper"]):not([class*="container"]):not([class*="list"]), [role="listitem"]') || btn.parentElement.parentElement.parentElement.parentElement || btn.parentElement.parentElement.parentElement;
        }).filter(Boolean);
    }
    
    // Standard CSS Selector Fallback
    if (rawContainers.length === 0) {
        rawContainers = Array.from(document.querySelectorAll('message-content, .message-content, [data-message-author="model"], div[class*="model-response"], article, .prose, .ds-markdown, .markdown-body, .font-claude-message, .markdown, [data-testid="chat-message-text"], div[class*="conversation-msg"]'));
    }

    // Deduplicate exact DOM nodes (NotebookLM action bar maps multiple buttons to the same parent container)
    rawContainers = [...new Set(rawContainers)];

    return rawContainers.filter(n => !rawContainers.some(other => other !== n && n.contains(other)));
}

// Global click listener to intercept native Copy
document.addEventListener('click', (e) => {
    const btn = e.target.closest('button, [role="button"], [aria-label], [title], [mattooltip], .copy-button');
    if (!btn) return;
    
    const t = (btn.innerText || "").toLowerCase();
    const a = (btn.getAttribute('aria-label') || "").toLowerCase();
    const title = (btn.getAttribute('title') || "").toLowerCase();
    const tooltip = (btn.getAttribute('mattooltip') || "").toLowerCase();
    
    if (t.includes('copy') || a.includes('copy') || title.includes('copy') || tooltip.includes('copy')) {
        // Intercepted a Copy action!
        const messageContainers = getMessageContainers();
        let container = btn.closest('article, div[class*="message"]:not([class*="messages"]):not([class*="wrapper"]):not([class*="container"]):not([class*="list"]), [role="listitem"]');
        
        if (!container) {
            container = messageContainers.find(c => c.contains(btn));
        }
        
        // If button is outside the message (like in Gemini's footer), walk up to find shared parent
        if (!container) {
            let parent = btn.parentElement;
            while (parent && parent !== document.body) {
                const contained = messageContainers.filter(c => parent.contains(c));
                if (contained.length > 0) {
                    // Pick the closest message container that appears before the button
                    const beforeBtn = contained.filter(c => c.compareDocumentPosition(btn) & Node.DOCUMENT_POSITION_FOLLOWING);
                    container = beforeBtn.length > 0 ? beforeBtn[beforeBtn.length - 1] : contained[0];
                    break;
                }
                parent = parent.parentElement;
            }
        }
        
        if (!container) return; // Not inside or associated with a message
        if (container.closest('[data-message-author="user"], user-query, [class*="user-message"]')) return;
        
        // Prevent accidental duplicate copies if already syncing/synced
        if (btn.classList.contains('synapseip-syncing-now')) return;
        btn.classList.add('synapseip-syncing-now');
        
        // Show immediate visual feedback on the button
        const originalBg = btn.style.backgroundColor || '';
        const originalColor = btn.style.color || '';
        btn.style.backgroundColor = 'rgba(59, 130, 246, 0.2)'; // blue while syncing
        btn.style.color = '#3b82f6';
        btn.style.borderRadius = '6px';

        // Wait 300ms for NotebookLM to write the content to the clipboard
        setTimeout(async () => {
            try {
                let clipboardHTML = "";
                let clipboardText = "";
                
                try {
                    const clipboardItems = await navigator.clipboard.read();
                    for (const item of clipboardItems) {
                        if (item.types.includes('text/html')) {
                            const blob = await item.getType('text/html');
                            clipboardHTML = await blob.text();
                        }
                        if (item.types.includes('text/plain')) {
                            const blob = await item.getType('text/plain');
                            clipboardText = await blob.text();
                        }
                    }
                } catch(err) {
                    console.log("Failed to read rich clipboard, falling back to readText", err);
                    clipboardText = await navigator.clipboard.readText();
                }

                if (!clipboardHTML && !clipboardText) {
                    throw new Error("Clipboard empty or permission denied");
                }
                
                // Prefer HTML for rich formatting, fallback to plain text with <br> tags
                let finalContent = clipboardHTML || clipboardText.replace(/\n/g, '<br>');

                const sourceUrl = window.location.href;
                const myIndex = messageContainers.indexOf(container);
                const conversationalIndex = myIndex !== -1 ? myIndex + 1 : "?";

                let userPromptText = "";
                const userSelectors = 'user-query, [data-message-author="user"], div[data-message-author="user"], [class*="user-message"], [class*="UserMessage"], .query-text, [class*="query"], [class*="user-bubble"]';
                let match = container.querySelector(userSelectors);
                if (match) {
                    let text = match.innerText || match.textContent;
                    userPromptText = text.replace(/^(You said|You)\s*\n?/i, '').trim();
                } else {
                    const allUserNodes = Array.from(document.querySelectorAll(userSelectors));
                    const previousUserNodes = allUserNodes.filter(n => n.compareDocumentPosition(container) & Node.DOCUMENT_POSITION_FOLLOWING);
                    if (previousUserNodes.length > 0) {
                        match = previousUserNodes[previousUserNodes.length - 1];
                        let text = match.innerText || match.textContent;
                        userPromptText = text.replace(/^(You said|You)\s*\n?/i, '').trim();
                    }
                }

                let combinedContent = finalContent;
                if (userPromptText) {
                    const escapeUser = userPromptText.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, '<br>');
                    combinedContent = `<div class="ai-prompt"><strong>User Prompt:</strong><br><p>${escapeUser}</p></div><hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;"><div class="ai-response"><strong>AI Response:</strong><br><div class="markdown-body">${finalContent}</div></div>`;
                }

                let nodeId = container.getAttribute('data-message-id') || container.id || container.getAttribute('data-synapseip-id');
                if (!nodeId) {
                    nodeId = "hash-" + Math.random().toString(36).substr(2, 9);
                    container.setAttribute('data-synapseip-id', nodeId);
                }
                combinedContent += `<div style="display:none;" data-synth-id="${nodeId}"></div>`;

                const payload = {
                    title: `AI Source Node #${conversationalIndex} - ${new Date().toLocaleString()}`,
                    content: combinedContent,
                    source_url: sourceUrl
                };

                // Cross-browser runtime resolution
                // On Google-owned pages (gemini.google.com), the `chrome` global exists natively
                // but chrome.runtime.id is ONLY set when an extension context is active.
                // typeof checks on sendMessage fail here because Google's own chrome object
                // defines runtime but without extension methods.
                let extRuntime = null;
                try {
                    if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
                        extRuntime = chrome.runtime;
                    } else if (typeof browser !== 'undefined' && browser.runtime && browser.runtime.id) {
                        extRuntime = browser.runtime;
                    }
                } catch (e) {
                    console.warn("SynapseIP: Error accessing extension runtime.", e);
                }

                if (!extRuntime) {
                    console.error("SynapseIP Extension context not available. chrome.runtime.id =", 
                        (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime.id : 'N/A');
                    btn.classList.remove('synapseip-syncing-now');
                    btn.style.backgroundColor = originalBg;
                    btn.style.color = originalColor;
                    // Don't use alert() — it's disruptive. Just log and reset the button.
                    console.warn("SynapseIP: Extension context lost. This usually means the extension was reloaded. Please refresh this tab.");
                    return;
                }

                try {
                    extRuntime.sendMessage({ action: "sync_to_synapseip", data: payload }, (response) => {
                    btn.classList.remove('synapseip-syncing-now');
                    if (extRuntime.lastError) {
                        console.error(extRuntime.lastError);
                        btn.style.backgroundColor = originalBg;
                        btn.style.color = originalColor;
                        return;
                    }
                    if (response && response.status === "error") {
                        alert("SynapseIP Sync Error: " + response.error);
                        btn.style.backgroundColor = originalBg;
                        btn.style.color = originalColor;
                        return;
                    }
                    if (response && response.status === "success") {
                        // Turn it green permanently!
                        btn.classList.add('synapseip-synced-btn');
                        
                        // Show a tiny success checkmark or text temporarily
                        const oldHtml = btn.innerHTML;
                        btn.innerHTML = `<span style="font-size: 0.8rem; font-weight: bold; margin: 0 4px; color: #10b981;">Synced! ✓</span>`;
                        setTimeout(() => {
                            btn.innerHTML = oldHtml;
                            btn.classList.add('synapseip-synced-btn'); // Re-apply class in case framework wiped it
                        }, 3000);
                    }
                });
                } catch (sendErr) {
                    console.error("SynapseIP Extension context invalidated during send. Please refresh the page.", sendErr);
                    btn.classList.remove('synapseip-syncing-now');
                    alert("SynapseIP Extension context lost. Please refresh this page to restore the connection!");
                }
            } catch (e) {
                console.error("SynapseIP Clipboard Sync Error. Please allow clipboard permissions if prompted.", e);
                btn.classList.remove('synapseip-syncing-now');
            }
        }, 300); // 300ms wait for native copy to finish
    }
}, true);

// Observer is no longer needed since we only color reactively upon user click.

// --- SYNAPSEIP TOKEN HANDOFF ---
// Listen for authentication tokens broadcasted by the SynapseIP web dashboard
const isSynapseDashboard = window.location.hostname.includes("synapseip-1ncu.onrender.com") || window.location.hostname.includes("localhost") || window.location.hostname.includes("127.0.0.1") || window.location.hostname.includes("192.168.");

if (isSynapseDashboard) {
    window.addEventListener("message", function(event) {
        if (event.source !== window) return;
        if (event.data && event.data.type === "SYNAPSE_AUTH_TOKEN") {
            console.log("SynapseIP Extension: Secure token received from dashboard");
            let extRuntime = null;
            if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) extRuntime = chrome.runtime;
            else if (typeof browser !== 'undefined' && browser.runtime && browser.runtime.sendMessage) extRuntime = browser.runtime;
            
            if (extRuntime) {
                extRuntime.sendMessage({ action: "save_auth_token", token: event.data.token, server: window.location.origin });
            }
        }
    });
}

// --- PROJECT SELECTOR OVERLAY ---
// Only inject on AI chat pages, NOT on the SynapseIP dashboard
if (!isSynapseDashboard) {
    (function initProjectSelector() {
        // Inject overlay CSS
        const overlayStyle = document.createElement('style');
        overlayStyle.textContent = `
            #synapseip-project-pill {
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 2147483647;
                font-family: 'Google Sans', 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
                user-select: none;
                transition: opacity 0.2s ease;
            }
            #synapseip-project-pill.synapseip-dragging {
                opacity: 0.85;
                cursor: grabbing !important;
            }
            #synapseip-pill-btn {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 50px;
                color: #e2e8f0;
                font-size: 13px;
                font-weight: 500;
                cursor: grab;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05) inset;
                transition: all 0.25s ease;
                white-space: nowrap;
                max-width: 280px;
            }
            #synapseip-pill-btn:hover {
                border-color: rgba(59, 130, 246, 0.6);
                box-shadow: 0 4px 24px rgba(59, 130, 246, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
                background: rgba(15, 23, 42, 0.92);
            }
            #synapseip-pill-label {
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 180px;
            }
            #synapseip-pill-chevron {
                transition: transform 0.2s ease;
                flex-shrink: 0;
                opacity: 0.6;
            }
            #synapseip-project-pill.synapseip-open #synapseip-pill-chevron {
                transform: rotate(180deg);
            }
            #synapseip-dropdown {
                display: none;
                position: absolute;
                bottom: calc(100% + 8px);
                right: 0;
                min-width: 240px;
                max-width: 320px;
                max-height: 300px;
                overflow-y: auto;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(59, 130, 246, 0.25);
                border-radius: 14px;
                padding: 6px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                animation: synapseip-slideUp 0.2s ease;
            }
            #synapseip-project-pill.synapseip-open #synapseip-dropdown {
                display: block;
            }
            @keyframes synapseip-slideUp {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .synapseip-dropdown-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 14px;
                border-radius: 10px;
                color: #cbd5e1;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.15s ease;
                border: none;
                background: none;
                width: 100%;
                text-align: left;
                font-family: inherit;
            }
            .synapseip-dropdown-item:hover {
                background: rgba(59, 130, 246, 0.12);
                color: #f1f5f9;
            }
            .synapseip-dropdown-item.synapseip-active {
                background: rgba(59, 130, 246, 0.18);
                color: #93c5fd;
                font-weight: 600;
            }
            .synapseip-dropdown-item .synapseip-radio {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                border: 2px solid rgba(148, 163, 184, 0.4);
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.15s ease;
            }
            .synapseip-dropdown-item.synapseip-active .synapseip-radio {
                border-color: #3b82f6;
            }
            .synapseip-dropdown-item.synapseip-active .synapseip-radio::after {
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #3b82f6;
            }
            .synapseip-dropdown-divider {
                height: 1px;
                background: rgba(255, 255, 255, 0.08);
                margin: 4px 8px;
            }
            .synapseip-dropdown-item.synapseip-new-project {
                color: #60a5fa;
            }
            .synapseip-dropdown-item.synapseip-new-project:hover {
                background: rgba(59, 130, 246, 0.12);
            }
            #synapseip-new-project-input {
                display: none;
                padding: 8px 14px;
                margin: 4px 6px;
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 8px;
                color: #e2e8f0;
                font-size: 13px;
                font-family: inherit;
                outline: none;
                width: calc(100% - 12px);
                box-sizing: border-box;
            }
            #synapseip-new-project-input:focus {
                border-color: rgba(59, 130, 246, 0.6);
            }
            #synapseip-dropdown::-webkit-scrollbar {
                width: 4px;
            }
            #synapseip-dropdown::-webkit-scrollbar-track {
                background: transparent;
            }
            #synapseip-dropdown::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            .synapseip-loading-spinner {
                display: inline-block;
                width: 14px;
                height: 14px;
                border: 2px solid rgba(148, 163, 184, 0.3);
                border-top-color: #60a5fa;
                border-radius: 50%;
                animation: synapseip-spin 0.6s linear infinite;
            }
            @keyframes synapseip-spin {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(overlayStyle);

        // Create the pill
        const pill = document.createElement('div');
        pill.id = 'synapseip-project-pill';
        pill.innerHTML = `
            <div id="synapseip-pill-btn">
                <span style="font-size: 16px; flex-shrink: 0;">🧠</span>
                <span id="synapseip-pill-label">Loading...</span>
                <svg id="synapseip-pill-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div id="synapseip-dropdown">
                <div id="synapseip-project-list"></div>
                <div class="synapseip-dropdown-divider"></div>
                <button class="synapseip-dropdown-item synapseip-new-project" id="synapseip-new-project-btn">
                    <span style="font-size: 15px;">＋</span>
                    <span>New Project...</span>
                </button>
                <input type="text" id="synapseip-new-project-input" placeholder="Project name, then press Enter" autocomplete="off">
            </div>
        `;
        document.body.appendChild(pill);

        const pillBtn = document.getElementById('synapseip-pill-btn');
        const pillLabel = document.getElementById('synapseip-pill-label');
        const dropdown = document.getElementById('synapseip-dropdown');
        const projectList = document.getElementById('synapseip-project-list');
        const newProjectBtn = document.getElementById('synapseip-new-project-btn');
        const newProjectInput = document.getElementById('synapseip-new-project-input');

        let isOpen = false;
        let activeProjectId = null;
        let isDragging = false;
        let dragStartX, dragStartY, pillStartX, pillStartY;
        let hasDragged = false;

        // --- Draggable ---
        pillBtn.addEventListener('mousedown', (e) => {
            isDragging = true;
            hasDragged = false;
            dragStartX = e.clientX;
            dragStartY = e.clientY;
            const rect = pill.getBoundingClientRect();
            pillStartX = rect.left;
            pillStartY = rect.top;
            pill.classList.add('synapseip-dragging');
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - dragStartX;
            const dy = e.clientY - dragStartY;
            if (Math.abs(dx) > 3 || Math.abs(dy) > 3) hasDragged = true;
            pill.style.left = (pillStartX + dx) + 'px';
            pill.style.top = (pillStartY + dy) + 'px';
            pill.style.right = 'auto';
            pill.style.bottom = 'auto';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                pill.classList.remove('synapseip-dragging');
            }
        });

        // --- Toggle Dropdown ---
        pillBtn.addEventListener('click', (e) => {
            if (hasDragged) return; // Don't toggle if we just dragged
            isOpen = !isOpen;
            pill.classList.toggle('synapseip-open', isOpen);
            if (isOpen) {
                fetchAndRenderProjects();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (isOpen && !pill.contains(e.target)) {
                isOpen = false;
                pill.classList.remove('synapseip-open');
                newProjectInput.style.display = 'none';
            }
        });

        // --- Fetch & Render Projects ---
        function fetchAndRenderProjects() {
            projectList.innerHTML = '<div style="padding: 10px 14px; color: #94a3b8;"><span class="synapseip-loading-spinner"></span></div>';
            
            // Check if extension runtime is available
            if (typeof chrome === 'undefined' || !chrome.runtime || !chrome.runtime.sendMessage) {
                projectList.innerHTML = '<div style="padding: 10px 14px; color: #f87171; font-size: 12px;">Extension not loaded. Please reload the extension.</div>';
                console.error("SynapseIP: chrome.runtime not available in content script");
                return;
            }
            
            chrome.runtime.sendMessage({ action: "fetch_projects" }, (response) => {
                if (chrome.runtime.lastError || !response || response.status !== "success") {
                    projectList.innerHTML = '<div style="padding: 10px 14px; color: #f87171; font-size: 12px;">Failed to load projects. Log into SynapseIP first.</div>';
                    return;
                }
                renderProjectList(response.projects);
            });
        }

        function renderProjectList(projects) {
            projectList.innerHTML = '';
            if (!projects || projects.length === 0) {
                projectList.innerHTML = '<div style="padding: 10px 14px; color: #94a3b8; font-size: 12px;">No projects yet.</div>';
                return;
            }
            projects.forEach(p => {
                const item = document.createElement('button');
                item.className = 'synapseip-dropdown-item' + (p.id === activeProjectId ? ' synapseip-active' : '');
                item.innerHTML = `<span class="synapseip-radio"></span><span>${escapeHtml(p.name)}</span>`;
                item.addEventListener('click', () => selectProject(p));
                projectList.appendChild(item);
            });
        }

        function selectProject(project) {
            activeProjectId = project.id;
            pillLabel.textContent = project.name;
            isOpen = false;
            pill.classList.remove('synapseip-open');
            newProjectInput.style.display = 'none';
            if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
                chrome.runtime.sendMessage({ action: "set_active_project", project: { id: project.id, name: project.name } });
            }
            // Re-render to update radio buttons
            fetchAndRenderProjects();
        }

        // --- New Project ---
        newProjectBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            newProjectInput.style.display = 'block';
            newProjectInput.value = '';
            newProjectInput.focus();
        });

        newProjectInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && newProjectInput.value.trim()) {
                const name = newProjectInput.value.trim();
                newProjectInput.style.display = 'none';
                projectList.innerHTML = '<div style="padding: 10px 14px; color: #94a3b8;"><span class="synapseip-loading-spinner"></span> Creating...</div>';
                
                if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
                    chrome.runtime.sendMessage({ action: "create_project", name }, (response) => {
                        if (chrome.runtime.lastError || !response || response.status !== "success") {
                            projectList.innerHTML = '<div style="padding: 10px 14px; color: #f87171; font-size: 12px;">Failed to create project.</div>';
                            return;
                        }
                        selectProject(response.project);
                    });
                } else {
                    projectList.innerHTML = '<div style="padding: 10px 14px; color: #f87171; font-size: 12px;">Extension not loaded.</div>';
                }
            }
            if (e.key === 'Escape') {
                newProjectInput.style.display = 'none';
            }
        });

        // Prevent typing in the input from bubbling to the host page
        newProjectInput.addEventListener('keydown', (e) => e.stopPropagation());
        newProjectInput.addEventListener('keyup', (e) => e.stopPropagation());
        newProjectInput.addEventListener('keypress', (e) => e.stopPropagation());

        // --- Load Initial State ---
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage({ action: "get_active_project" }, (response) => {
                if (chrome.runtime.lastError) {
                    pillLabel.textContent = "No project";
                    return;
                }
                if (response && response.project) {
                    activeProjectId = response.project.id;
                    pillLabel.textContent = response.project.name;
                } else {
                    // No project selected yet — fetch list and auto-select the first one
                    if (chrome.runtime && chrome.runtime.sendMessage) {
                        chrome.runtime.sendMessage({ action: "fetch_projects" }, (res) => {
                            if (res && res.status === "success" && res.projects && res.projects.length > 0) {
                                selectProject(res.projects[0]);
                            } else {
                                pillLabel.textContent = "No project";
                            }
                        });
                    }
                }
            });
        } else {
            pillLabel.textContent = "No project";
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    })();
}
