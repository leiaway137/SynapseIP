console.log("SynapseIP Messenger: Stealth Content Script loaded on", window.location.hostname);

let syncedSources = [];
chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
    if (response && response.status === "success") {
        syncedSources = response.sources;
        decorateSyncedNodes();
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "global_sync_update" || request.action === "global_desync") {
        chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
            if (response && response.status === "success") {
                syncedSources = response.sources;
                decorateSyncedNodes();
            }
        });
    }
});

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

function decorateSyncedNodes() {
    if (!chrome.runtime || !chrome.runtime.id) return;

    const messageContainers = getMessageContainers();
    
    // Clear old decorations
    document.querySelectorAll('.synapseip-persistent-badge').forEach(b => b.remove());
    document.querySelectorAll('.synapseip-synced-container').forEach(c => c.classList.remove('synapseip-synced-container'));

    let claimedIndices = new Set();
    messageContainers.forEach((container, index) => {
        if (container.classList.contains('synapseip-synced-container')) return;
        if (container.closest('[data-message-author="user"], user-query, [class*="user-message"]')) return;

        const textClone = container.cloneNode(true);
        const snippet = textClone.innerText.trim().substring(0, 150).replace(/\s+/g, ' ');
        const geminiId = container.getAttribute('data-message-id') || container.id || container.getAttribute('data-synapseip-id') || 'unknown';
        
        let syncedIndex = -1;
        if (syncedSources.length > 0) {
            syncedIndex = syncedSources.findIndex((s, idx) => {
                if (claimedIndices.has(idx)) return false;
                if (geminiId !== 'unknown' && s.content.includes(`data-synth-id="${geminiId}"`)) return true;
                
                const tempDiv = document.createElement('div');
                // Force spacing between block elements so textContent doesn't crush words together
                tempDiv.innerHTML = s.content.replace(/<\/(p|div|h[1-6]|li|ul|ol|br|strong|b)>/gi, ' </$1> ');
                const plainText = (tempDiv.innerText || tempDiv.textContent || "").replace(/\s+/g, ' ');
                return snippet.length > 25 && plainText.includes(snippet);
            });
            if (syncedIndex !== -1) claimedIndices.add(syncedIndex);
        }

        if (syncedIndex !== -1) {
            // It IS synced!
            container.classList.add('synapseip-synced-container');
            const badge = document.createElement('div');
            badge.className = 'synapseip-persistent-badge';
            
            const displayIdx = syncedSources[syncedIndex].id && syncedSources[syncedIndex].id > 0 ? syncedSources[syncedIndex].id : (index + 1);
            
            badge.innerHTML = `<span style="font-size: 11px; font-weight: 600;">✓ SynapseIP Synced #${displayIdx}</span>`;
            badge.style.cssText = "display: inline-flex; align-items: center; justify-content: center; background: rgba(16, 185, 129, 0.15); color: #059669; padding: 4px 8px; border-radius: 12px; margin-top: 8px; margin-bottom: 8px; font-family: system-ui, sans-serif; border: 1px solid rgba(16, 185, 129, 0.3); pointer-events: none;";
            
            // Try to put it near the action bar, or at the bottom of the container
            let appendTarget = container;
            const actionBars = Array.from(container.querySelectorAll('button, [role="button"]'));
            if (actionBars.length > 0) {
                 appendTarget = actionBars[actionBars.length - 1].parentElement;
                 if (appendTarget && (appendTarget.tagName === 'ARTICLE' || appendTarget === container)) {
                    container.appendChild(badge);
                 } else if (appendTarget) {
                    appendTarget.appendChild(badge);
                 } else {
                    container.appendChild(badge);
                 }
            } else {
                 container.appendChild(badge);
            }
        }
    });
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
            // Find which message container this button belongs to
            container = messageContainers.find(c => c.contains(btn));
        }
        
        if (!container) return; // Not inside a message
        
        if (container.closest('[data-message-author="user"], user-query, [class*="user-message"]')) return;
        
        // Prevent accidental duplicate copies if already syncing/synced
        if (container.classList.contains('synapseip-syncing-now')) return;
        container.classList.add('synapseip-syncing-now');
        
        // Show immediate visual feedback on the button
        const tempBadge = document.createElement('span');
        tempBadge.innerText = ' ✓ Synced';
        tempBadge.style.cssText = "color: #10b981; font-weight: bold; font-size: 12px; margin-left: 6px; animation: fadein 0.3s forwards;";
        btn.appendChild(tempBadge);
        setTimeout(() => {
            tempBadge.remove();
            container.classList.remove('synapseip-syncing-now');
        }, 3500);

        // Proceed to extract and sync
        const myIndex = messageContainers.indexOf(container);
        const conversationalIndex = myIndex !== -1 ? myIndex + 1 : "?";

        let cloneTarget = container;
        const clone = cloneTarget.cloneNode(true);
        Array.from(clone.querySelectorAll('button, mat-icon, [role="button"], .synapseip-persistent-badge')).forEach(b => b.remove());

        const htmlContent = clone.innerHTML;
        const sourceUrl = window.location.href;
        
        let userPromptText = "";
        try {
            const userSelectors = 'user-query, [data-message-author="user"], div[data-message-author="user"], [class*="user-message"], [class*="UserMessage"], .query-text, [class*="query"], [class*="user-bubble"]';
            let match = container.querySelector(userSelectors);
            
            if (match) {
                let text = match.innerText || match.textContent;
                userPromptText = text.replace(/^(You said|You)\s*\n?/i, '').trim();
                // Remove from clone to avoid duplication in AI Response
                const promptInClone = clone.querySelector(userSelectors);
                if (promptInClone) promptInClone.remove();
            } else {
                const allUserNodes = Array.from(document.querySelectorAll(userSelectors));
                const previousUserNodes = allUserNodes.filter(n => n.compareDocumentPosition(container) & Node.DOCUMENT_POSITION_FOLLOWING);
                if (previousUserNodes.length > 0) {
                    match = previousUserNodes[previousUserNodes.length - 1];
                    let text = match.innerText || match.textContent;
                    userPromptText = text.replace(/^(You said|You)\s*\n?/i, '').trim();
                }
            }
        } catch (e) { console.error(e); }
        
        let combinedContent = htmlContent;
        if (userPromptText) {
            const escapeUser = userPromptText.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            combinedContent = `<div class="ai-prompt"><strong>User Prompt:</strong><br><p>${escapeUser}</p></div><hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;"><div class="ai-response"><strong>AI Response:</strong><br>${htmlContent}</div>`;
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

        try {
            chrome.runtime.sendMessage({ action: "sync_to_synapseip", data: payload }, (response) => {
                if (chrome.runtime.lastError) return;
                if (response && response.status === "success") {
                    if (!syncedSources.some(s => s.content.includes(htmlContent.substring(0, 50)))) {
                        syncedSources.push({
                            id: (response.backendResponse && response.backendResponse.id) ? response.backendResponse.id : -1,
                            content: `<div>${combinedContent}</div>`
                        });
                    }
                    decorateSyncedNodes();
                }
            });
        } catch (e) {
            console.error("SynapseIP Extension Error: Please refresh this page. The extension was reloaded.", e);
        }
    }
}, true); // Use capture phase to ensure we catch it before React stops propagation!

// Observe DOM for new messages as Gemini/NotebookLM is a Single Page Application
let debounceTimer;
const observer = new MutationObserver(() => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        decorateSyncedNodes();
    }, 1500); // Wait for chat generation to settle
});

observer.observe(document.body, { childList: true, subtree: true });
