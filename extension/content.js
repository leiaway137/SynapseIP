console.log("SynapseIP Messenger: Stealth Content Script loaded on", window.location.hostname);

let syncedSources = [];
chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
    if (response && response.status === "success") {
        syncedSources = response.sources;
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "global_sync_update" || request.action === "global_desync") {
        chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
            if (response && response.status === "success") {
                syncedSources = response.sources;
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
    let claimedIndices = new Set();
    
    messageContainers.forEach((container, index) => {
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
                tempDiv.innerHTML = s.content.replace(/<\/(p|div|h[1-6]|li|ul|ol|br|strong|b)>/gi, ' </$1> ');
                const plainText = (tempDiv.innerText || tempDiv.textContent || "").replace(/\s+/g, ' ');
                return snippet.length > 25 && plainText.includes(snippet);
            });
            if (syncedIndex !== -1) claimedIndices.add(syncedIndex);
        }

        if (syncedIndex !== -1) {
            const displayIdx = syncedSources[syncedIndex].id && syncedSources[syncedIndex].id > 0 ? syncedSources[syncedIndex].id : (index + 1);
            
            // Apply sleek green styling to the copy button instead of appending a badge!
            const copyBtns = Array.from(container.querySelectorAll('button, [role="button"], [aria-label], [title], [mattooltip], .copy-button'))
                .filter(b => {
                    const t = (b.innerText || "").toLowerCase();
                    const a = (b.getAttribute('aria-label') || "").toLowerCase();
                    const title = (b.getAttribute('title') || "").toLowerCase();
                    const tooltip = (b.getAttribute('mattooltip') || "").toLowerCase();
                    return t.includes('copy') || a.includes('copy') || title.includes('copy') || tooltip.includes('copy');
                });
            
            if (copyBtns.length > 0) {
                const btn = copyBtns[copyBtns.length - 1]; // Usually the last one
                if (!btn.classList.contains('synapseip-synced-btn')) {
                    btn.classList.add('synapseip-synced-btn');
                    btn.style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
                    btn.style.color = '#10b981';
                    btn.style.borderRadius = '6px';
                    // Optional: add a tiny tooltip or text if possible, but color is enough!
                }
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
            container = messageContainers.find(c => c.contains(btn));
        }
        if (!container) return; // Not inside a message
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

                chrome.runtime.sendMessage({ action: "sync_to_synapseip", data: payload }, (response) => {
                    btn.classList.remove('synapseip-syncing-now');
                    if (chrome.runtime.lastError) {
                        console.error(chrome.runtime.lastError);
                        btn.style.backgroundColor = originalBg;
                        btn.style.color = originalColor;
                        return;
                    }
                    if (response && response.status === "success") {
                        if (!syncedSources.some(s => s.content.includes(clipboardText.substring(0, 50)))) {
                            syncedSources.push({
                                id: (response.backendResponse && response.backendResponse.id) ? response.backendResponse.id : -1,
                                content: `<div>${combinedContent}</div>`
                            });
                        }
                        // Turn it green permanently!
                        btn.classList.add('synapseip-synced-btn');
                        btn.style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
                        btn.style.color = '#10b981';
                        btn.style.borderRadius = '6px';
                    } else {
                        btn.style.backgroundColor = originalBg;
                        btn.style.color = originalColor;
                    }
                });
            } catch (e) {
                console.error("SynapseIP Clipboard Sync Error. Please allow clipboard permissions if prompted.", e);
                btn.classList.remove('synapseip-syncing-now');
                btn.style.backgroundColor = originalBg;
                btn.style.color = originalColor;
            }
        }, 300); // 300ms wait for native copy to finish
    }
}, true);

// Observer is no longer needed since we only color reactively upon user click.
