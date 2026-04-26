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
if (window.location.hostname.includes("synapseip-1ncu.onrender.com") || window.location.hostname.includes("localhost") || window.location.hostname.includes("127.0.0.1")) {
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
