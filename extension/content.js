console.log("SynapseIP Messenger: Content script loaded on", window.location.hostname);

let syncedSources = [];
chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
    if (response && response.status === "success") {
        syncedSources = response.sources;
        updateSyncState();
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "global_sync_update") {
        chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
            if (response && response.status === "success") {
                syncedSources = response.sources;
                updateSyncState();
            }
        });
    } else if (request.action === "global_desync") {
        chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
            if (response && response.status === "success") {
                syncedSources = response.sources;
                updateSyncState();
            }
        });
    }
});

function updateSyncState() {
    const wrappers = document.querySelectorAll('.synapseip-btn-wrapper');
    wrappers.forEach(w => w.remove());
    injectButtons();
}

// Function to inject our Sync button
function injectButtons() {
    // Synchronous check to see if the Extension was hot-reloaded by the user. 
    // If the ID is gone, the context is dead. Kill the DOM Observer instantly.
    if (!chrome.runtime || !chrome.runtime.id) {
        console.warn("SynapseIP: Extension updated. Disconnecting DOM listener. Please refresh the page.");
        if (typeof observer !== "undefined") observer.disconnect();
        return;
    }

    try {
        chrome.storage.local.get("extensionSelectors", (data) => {
            if (chrome.runtime.lastError) return; // Silent fail if async context dies
            
            const activeHost = window.location.hostname.replace('www.', '');
            let selectorString = 'message-content, .message-content, [data-message-author="model"], div[class*="model-response"], article, .prose, .ds-markdown, .markdown-body, .font-claude-message, .markdown, [data-testid="chat-message-text"], div[class*="conversation-msg"]';
            if (data.extensionSelectors && data.extensionSelectors[activeHost]) {
                selectorString = data.extensionSelectors[activeHost];
            }

            let rawContainers = Array.from(document.querySelectorAll(selectorString));
            // De-duplicate nested matches! If a site wraps its markdown in an <article> and both match, only target the innermost payload!
            const messageContainers = rawContainers.filter(n => !rawContainers.some(other => other !== n && n.contains(other)));
        
        if (messageContainers.length === 0) {
            if (!window.sentinelTriggered) {
                setTimeout(() => {
                    if (document.querySelectorAll(selectorString).length === 0) {
                        triggerSentinelMode();
                    }
                }, 4000);
            }
            return;
        }

        messageContainers.forEach((container) => {
            // Prevent adding multiple buttons to the same container
            if (container.querySelector('.synapseip-sync-btn')) return;
            
            // Explicitly ignore bubbles authored by the User natively to prevent dual injection on right-aligned text
            if (container.closest('[data-message-author="user"], user-query, [class*="user-message"]')) return;

        // Clean check for existing sync state
        const textClone = container.cloneNode(true);
        const snippet = textClone.innerText.trim().substring(0, 150).replace(/\s+/g, ' ');
        const geminiId = container.closest('[data-message-id]')?.getAttribute('data-message-id') || container.getAttribute('data-message-id') || container.id || 'unknown';
        
        let syncedIndex = -1;
        if (syncedSources.length > 0) {
            syncedIndex = syncedSources.findIndex(s => {
                if (geminiId !== 'unknown' && s.content.includes(`data-synth-id="${geminiId}"`)) return true;
                
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = s.content;
                const plainText = (tempDiv.innerText || tempDiv.textContent || "").replace(/\s+/g, ' ');
                return snippet.length > 25 && plainText.includes(snippet);
            });
        }

        // Derive exact chronological index natively from the pre-processed array
        const myIndex = messageContainers.indexOf(container);
        const conversationalIndex = myIndex !== -1 ? myIndex + 1 : "?";

        // Create the button
        const btn = document.createElement('button');
        btn.className = 'synapseip-sync-btn';
        
        if (syncedIndex !== -1) {
            btn.classList.add('synced');
            const displayIdx = syncedSources[syncedIndex].id && syncedSources[syncedIndex].id > 0 ? syncedSources[syncedIndex].id : conversationalIndex;
            btn.innerText = `Synced Note #${displayIdx} ✓ (Click to Desync)`;
            btn.disabled = false;
            
            btn.addEventListener('click', () => {
                btn.classList.add('synapseip-syncing');
                btn.innerText = 'Desyncing...';
                btn.disabled = true;
                
                chrome.runtime.sendMessage({ 
                    action: "desync_from_synapseip", 
                    data: { id: syncedSources[syncedIndex].id } 
                }, (response) => {
                    if (chrome.runtime.lastError) {
                        btn.classList.remove('synapseip-syncing');
                        btn.innerText = 'Desync Failed ✗';
                        setTimeout(() => { btn.disabled = false; btn.innerText = `Synced Note #${conversationalIndex} ✓ (Click to Desync)`; }, 2000);
                    }
                });
            });
            
        } else {
            btn.innerText = 'Sync to SynapseIP';
            
            btn.addEventListener('click', () => {
            btn.classList.add('synapseip-syncing');
            btn.innerText = 'Syncing...';
            btn.disabled = true;

            // Extract the text!
            let cloneTarget = container;
            if (window.location.hostname.includes("notebooklm")) {
                const bubble = container.closest('article, div[class*="message"], .chat-bubble') || container.parentElement.parentElement.parentElement;
                if (bubble) cloneTarget = bubble;
            }
            const clone = cloneTarget.cloneNode(true);
            
            const wrapperInClone = clone.querySelector('.synapseip-btn-wrapper');
            if (wrapperInClone) wrapperInClone.remove();
            else {
                const oldBtn = clone.querySelector('.synapseip-sync-btn');
                if (oldBtn) oldBtn.remove();
            }
            
            if (window.location.hostname.includes("notebooklm")) {
                // Scrub Google's native SVGs and action icons so they don't pollute your synced document text
                Array.from(clone.querySelectorAll('button, mat-icon, [role="button"]')).forEach(b => b.remove());
            }

            const htmlContent = clone.innerHTML;
            const sourceUrl = window.location.href;
            
            // Grab the user's prompt by finding the closest preceding node
            let userPromptText = "";
            try {
                // Generic catch for conversational user node prefixes matching industry defaults
                const allUserNodes = Array.from(document.querySelectorAll('user-query, [data-message-author="user"], div[data-message-author="user"], [class*="user-message"]'));
                const previousUserNodes = allUserNodes.filter(n => 
                    n.compareDocumentPosition(container) & Node.DOCUMENT_POSITION_FOLLOWING
                );
                if (previousUserNodes.length > 0) {
                    const match = previousUserNodes[previousUserNodes.length - 1];
                    let text = match.innerText || match.textContent;
                    userPromptText = text.replace(/^(You said|You)\s*\n?/i, '').trim();
                }
            } catch (e) { console.error(e); }
            
            let combinedContent = htmlContent;
            if (userPromptText) {
                const escapeUser = userPromptText.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                combinedContent = `<div class="ai-prompt"><strong>User Prompt:</strong><br><p>${escapeUser}</p></div><hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;"><div class="ai-response"><strong>AI Response:</strong><br>${htmlContent}</div>`;
            }
            
            const nodeId = container.closest('[data-message-id]')?.getAttribute('data-message-id') || container.getAttribute('data-message-id') || container.id || "hash-" + Math.random().toString(36).substr(2, 9);
            combinedContent += `<div style="display:none;" data-synth-id="${nodeId}"></div>`;

            // Send standard payload structure expected by the FastAPI backend
            const payload = {
                title: `AI Source Node #${conversationalIndex} - ${new Date().toLocaleString()}`,
                content: combinedContent,
                source_url: sourceUrl
            };

            // Send message to background script
            chrome.runtime.sendMessage({ action: "sync_to_synapseip", data: payload }, (response) => {
                // Check for connection severing or other manifest errors
                if (chrome.runtime.lastError) {
                    console.error("SynapseIP Messenger Error:", chrome.runtime.lastError.message);
                    btn.classList.add('error');
                    btn.innerText = 'Manifest Sync Failed ✗';
                    setTimeout(() => {
                        btn.classList.remove('error');
                        btn.classList.remove('synapseip-syncing');
                        btn.innerText = 'Sync to SynapseIP';
                        btn.disabled = false;
                    }, 4000);
                    return;
                }

                if (response && response.status === "success") {
                    btn.classList.add('synced');
                    const displayIdx = (response.backendResponse && response.backendResponse.total_count) ? response.backendResponse.total_count : conversationalIndex;
                    btn.innerText = `Synced Conversation Note #${displayIdx} ✓`;
                    if (!syncedSources.some(s => s.content.includes(htmlContent.substring(0, 50)))) {
                        syncedSources.push({
                            id: (response.backendResponse && response.backendResponse.id) ? response.backendResponse.id : -1,
                            content: `<div>${combinedContent}</div>`
                        });
                    }
                    updateSyncState();
                } else if (response && response.status === "error") {
                    console.error("SynapseIP Messenger Backend Error:", response.error);
                    btn.classList.add('error');
                    btn.innerText = 'Server Error ✗';
                    setTimeout(() => {
                        btn.classList.remove('error');
                        btn.classList.remove('synapseip-syncing');
                        btn.innerText = 'Sync to SynapseIP';
                        btn.disabled = false;
                    }, 3000);
                }
            });
        });
        } // Close the 'else' block

        // Wrap the button in a context container
        const wrapper = document.createElement('div');
        wrapper.className = 'synapseip-btn-wrapper';
        wrapper.style.display = 'inline-flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.gap = '8px';
        wrapper.style.marginTop = '12px';

        wrapper.appendChild(btn);

        // Build the hidden Sync All button
        const syncAllBtn = document.createElement('button');
        syncAllBtn.className = 'synapseip-sync-all-btn';
        syncAllBtn.innerText = 'Sync All Responses';
        syncAllBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        syncAllBtn.style.color = 'white';
        syncAllBtn.style.border = 'none';
        syncAllBtn.style.borderRadius = '20px';
        syncAllBtn.style.fontFamily = 'Inter, sans-serif';
        syncAllBtn.style.fontSize = '12px';
        syncAllBtn.style.fontWeight = '600';
        syncAllBtn.style.cursor = 'pointer';
        syncAllBtn.style.maxWidth = '0px';
        syncAllBtn.style.opacity = '0';
        syncAllBtn.style.overflow = 'hidden';
        syncAllBtn.style.whiteSpace = 'nowrap';
        syncAllBtn.style.padding = '0';
        syncAllBtn.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        syncAllBtn.style.pointerEvents = 'none';

        wrapper.appendChild(syncAllBtn);

        let hoverTimer;
        wrapper.addEventListener('mouseenter', () => {
            hoverTimer = setTimeout(() => {
                syncAllBtn.style.maxWidth = '200px';
                syncAllBtn.style.opacity = '1';
                syncAllBtn.style.padding = '8px 16px';
                syncAllBtn.style.pointerEvents = 'auto';
            }, 3000); // 3 seconds wait per user request
        });
        
        wrapper.addEventListener('mouseleave', () => {
            clearTimeout(hoverTimer);
            syncAllBtn.style.maxWidth = '0px';
            syncAllBtn.style.opacity = '0';
            syncAllBtn.style.padding = '0';
            syncAllBtn.style.pointerEvents = 'none';
        });

        function getScrollParent(node) {
            if (node == null) return null;
            if (node.scrollHeight > node.clientHeight && window.getComputedStyle(node).overflowY !== 'visible') {
                return node;
            }
            return getScrollParent(node.parentNode) || document.scrollingElement || document.body;
        }

        syncAllBtn.addEventListener('click', async () => {
            syncAllBtn.innerText = `Auto-Scrolling DOM Engine Active...`;
            syncAllBtn.disabled = true;
            syncAllBtn.style.background = '#eab308';
            
            const blocker = document.createElement('div');
            blocker.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: rgba(0,0,0,0.85); z-index: 999999;
                display: flex; align-items: center; justify-content: center;
                flex-direction: column; cursor: wait; backdrop-filter: blur(8px);
            `;
            const blockerText = document.createElement('h1');
            blockerText.innerText = "🤖 SynapseIP Virtual DOM Hijack Active";
            blockerText.style.cssText = "color: white; font-family: sans-serif; font-weight: 800; font-size: 2.5rem; margin-bottom: 10px;";
            const blockerSubtext = document.createElement('p');
            blockerSubtext.innerText = "Forcing Gemini to render offscreen nodes. Do not click. Please wait.";
            blockerSubtext.style.cssText = "color: #e5e7eb; font-family: sans-serif; font-size: 1.2rem;";
            blocker.appendChild(blockerText);
            blocker.appendChild(blockerSubtext);
            document.body.appendChild(blocker);

            // --- PHASE 1: ASCENDANT CRAWLER ---
            blockerText.innerText = "🤖 Ascending to conversation sequence start...";
            
            let prevTopText = "";
            let topFails = 0;
            
            // Initial blast to top
            window.scrollTo(0, 0);
            await new Promise(r => setTimeout(r, 1500));
            
            while (true) {
                const modelNodes = Array.from(document.querySelectorAll('.model-turn, message-content, [data-message-author="model"], div[class*="model-response"]'));
                const leafNodes = modelNodes.filter(n => !modelNodes.some(other => other !== n && n.contains(other)));
                
                if (leafNodes.length > 0) {
                    const firstNode = leafNodes[0];
                    // Fling the highest visible node to the very bottom of the screen to trigger the UPWARD infinite scroll interceptors!
                    firstNode.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    window.scrollTo(0, 0);
                    
                    await new Promise(r => setTimeout(r, 1600));
                    
                    const topText = firstNode.innerText.trim().substring(0, 100);
                    if (topText === prevTopText) {
                        topFails++;
                        if (topFails >= 2) break; // We hit the absolute roof, no new older messages loaded!
                    } else {
                        prevTopText = topText;
                        topFails = 0;
                    }
                } else {
                    break;
                }
            }
            
            // Setup for Phase 2
            blockerText.innerText = "🤖 Initiating downward synchronous extraction...";
            await new Promise(r => setTimeout(r, 1000));

            let totalScraped = 0;
            let scrollFails = 0;
            
            while (true) {
                // Find the very first unsynced button on the screen
                const targetBtn = document.querySelector('.synapseip-sync-btn:not(.synced):not(.synapseip-syncing)');
                
                if (!targetBtn) {
                    // Try to scroll down to force Gemini to load the next chunk
                    const allNodes = Array.from(document.querySelectorAll('.model-turn, message-content, [data-message-author="model"], div[class*="model-response"]'));
                    if (allNodes.length > 0) {
                        const lastNode = allNodes[allNodes.length - 1];
                        lastNode.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } else {
                        window.scrollBy(0, window.innerHeight);
                    }
                    
                    // LONG DELAY: Allow Gemini Intersection Observer to execute UI repaint
                    await new Promise(r => setTimeout(r, 1600)); 
                    
                    const postScrollCheck = document.querySelector('.synapseip-sync-btn:not(.synced):not(.synapseip-syncing)');
                    if (!postScrollCheck) {
                        scrollFails++;
                        if (scrollFails >= 3) break; // Finished gracefully if we scroll 3 times absolutely blank!
                        continue;
                    } else {
                        scrollFails = 0;
                        continue;
                    }
                }
                
                scrollFails = 0;
                
                // Pull the target button beautifully into the center of the viewport
                targetBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                await new Promise(r => setTimeout(r, 300));
                
                targetBtn.click();
                totalScraped++;
                blockerText.innerText = `🤖 Sequential Engine... Extracted: ${totalScraped}`;
                
                // Small breather before hunting next one
                await new Promise(r => setTimeout(r, 150));
            }
            
            document.body.removeChild(blocker);
            
            syncAllBtn.innerText = `Virtual DOM Scraped & Queued (${totalScraped}) ✓`;
            syncAllBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            setTimeout(() => {
                syncAllBtn.style.maxWidth = '0px';
                syncAllBtn.style.opacity = '0';
                syncAllBtn.style.padding = '0';
                syncAllBtn.style.pointerEvents = 'none';
                syncAllBtn.disabled = false;
                syncAllBtn.innerText = 'Sync All Responses';
            }, 3000);
        });

        let targetAppendNode = container;
        
        try {
            if (window.location.hostname.includes("notebooklm")) {
                // Look upwards to the overarching message block
                const globalMessageLevel = container.closest('article, div[class*="message"], .chat-bubble') || container.parentElement.parentElement.parentElement;
                if (globalMessageLevel) {
                    const buttons = Array.from(globalMessageLevel.querySelectorAll('button, [role="button"]'));
                    const anchorBtn = buttons.find(b => {
                        const t = (b.innerText || "").toLowerCase();
                        const a = (b.getAttribute('aria-label') || "").toLowerCase();
                        const title = (b.getAttribute('title') || "").toLowerCase();
                        const tooltip = (b.getAttribute('mattooltip') || "").toLowerCase();
                        return t.includes('save to note') || t.includes('export') || a.includes('bad') || title.includes('bad') || tooltip.includes('bad');
                    });
                    
                    const finalAnchor = anchorBtn || buttons[buttons.length - 1];
                    
                    if (finalAnchor && finalAnchor.parentElement) {
                        targetAppendNode = finalAnchor.parentElement;
                        // Restyle wrapper to sit inline with the action bar cleanly
                        wrapper.style.marginTop = '0';
                        wrapper.style.marginLeft = '16px';
                        wrapper.style.transform = 'scale(0.9)';
                    } else {
                        // If no action bar exists in this message block, this is the user's prompt. Do not attach a sync button.
                        return;
                    }
                }
            }
        } catch(e) { console.warn("SynapseIP: Failed to parse native action bar", e); }
        
        // Hard-enforcement: Only ever inject ONE button per visual action row natively!
        if (!targetAppendNode.querySelector('.synapseip-btn-wrapper')) {
            targetAppendNode.appendChild(wrapper);
        }
        });
        });
    } catch (e) {
        if (e.message && e.message.includes("Extension context invalidated")) {
            console.warn("SynapseIP: Extension updated. Disconnecting DOM listener. Please refresh the page.");
            if (typeof observer !== "undefined") observer.disconnect();
        } else {
            console.error("SynapseIP Extension Error:", e);
        }
    }
}

// Observe DOM for new messages as Gemini is a Single Page Application
const observer = new MutationObserver(() => {
    // Debounce or directly call logic to find new response bubbles
    injectButtons();
});

// Start observing the chat container or body
observer.observe(document.body, { childList: true, subtree: true });

// Initial run
injectButtons();

function triggerSentinelMode() {
    window.sentinelTriggered = true;
    if (document.getElementById("synapseip-sentinel")) return;

    const toast = document.createElement("div");
    toast.id = "synapseip-sentinel";
    toast.innerHTML = `
        <div style="background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); color: white; padding: 16px 24px; border-radius: 12px; box-shadow: 0 10px 25px rgba(239, 68, 68, 0.4); font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: space-between; position: fixed; top: 20px; right: 20px; z-index: 999999; width: 350px; cursor: pointer; border: 1px solid rgba(255,255,255,0.2);">
            <div>
                <h4 style="margin: 0 0 4px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Layout Shift Detected</h4>
                <p style="margin: 0; font-size: 13px; opacity: 0.9;">SynapseIP nodes disconnected. Click to auto-heal via AI.</p>
            </div>
            <div id="sentinel-loader" style="display: none; padding-left: 10px; font-weight: bold; font-size: 14px;">Wait...</div>
        </div>
    `;

    toast.addEventListener('click', () => {
        toast.querySelector('p').innerText = "Scanning Layout. AI Processing...";
        toast.querySelector('#sentinel-loader').style.display = 'block';
        toast.style.pointerEvents = 'none';

        // Rip HTML payload safely
        const payload = document.querySelector('main')?.innerHTML || document.body.innerHTML; 

        const activeHost = window.location.hostname.replace('www.', '');

        chrome.runtime.sendMessage({ 
            action: "report_structural_change", 
            html_payload: payload,
            hostname: activeHost
        }, (response) => {
            if (response && response.status === "success") {
                toast.innerHTML = `<div style="background: #10b981; color: white; padding: 16px; border-radius: 12px; text-align: center; width: 350px; position: fixed; top: 20px; right: 20px; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4); z-index: 999999; font-family: system-ui, sans-serif; font-weight: bold;">Healing Complete! Resyncing...</div>`;
                setTimeout(() => { toast.remove(); window.sentinelTriggered = false; injectButtons(); }, 2000);
            } else {
                toast.innerHTML = `<div style="background: #6b7280; color: white; padding: 16px; border-radius: 12px; text-align: center; width: 350px; position: fixed; top: 20px; right: 20px; box-shadow: 0 10px 25px rgba(107, 114, 128, 0.4); z-index: 999999; font-family: system-ui, sans-serif;">Heal Failed. Check Logs.</div>`;
                setTimeout(() => toast.remove(), 4000);
            }
        });
    });

    document.body.appendChild(toast);
}
