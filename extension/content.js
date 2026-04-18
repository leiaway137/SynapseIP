console.log("SynapseIP Messenger: Content script loaded on Gemini.");

let syncedSources = [];
chrome.runtime.sendMessage({ action: "fetch_synced_sources" }, (response) => {
    if (response && response.status === "success") {
        syncedSources = response.sources;
        updateSyncState();
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "global_sync_update") {
        syncedSources.push({
            content: request.htmlContent
        });
        updateSyncState();
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
    const containers = document.querySelectorAll('message-content, .message-content, [data-message-author="model"], div[class*="model-response"]');
    containers.forEach((container) => {
        const btn = container.querySelector('.synapseip-sync-btn');
        if (!btn) return;

        const textClone = container.cloneNode(true);
        const wrapperInClone = textClone.querySelector('.synapseip-btn-wrapper');
        if (wrapperInClone) wrapperInClone.remove();
        else {
            const oldBtn = textClone.querySelector('.synapseip-sync-btn');
            if (oldBtn) oldBtn.remove();
        }

        const snippet = textClone.innerText.trim().substring(0, 60).replace(/\s+/g, ' ');
        
        let syncedIndex = -1;
        if (snippet.length > 5 && syncedSources) {
            syncedIndex = syncedSources.findIndex(s => {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = s.content;
                const plainText = (tempDiv.innerText || tempDiv.textContent || "").replace(/\s+/g, ' ');
                return plainText.includes(snippet);
            });
        }

        const allModelRuns = Array.from(document.querySelectorAll('.model-turn, message-content, [data-message-author="model"], div[class*="model-response"]'));
        const uniqueNodes = allModelRuns.filter(n => !allModelRuns.some(other => other !== n && n.contains(other)));
        const myIndex = uniqueNodes.findIndex(n => n.contains(container) || n === container);
        const conversationalIndex = myIndex !== -1 ? myIndex + 1 : "?";

        if (syncedIndex !== -1) {
            btn.classList.add('synced');
            btn.innerText = `Synced Conversation Note #${conversationalIndex} ✓`;
            btn.disabled = true;
        } else {
            btn.classList.remove('synced');
            btn.innerText = "Sync to SynapseIP";
            btn.disabled = false;
        }
    });
}

// Function to inject our Sync button
function injectButtons() {
    // Gemini frequently changes class names. A generic approach:
    // Look for message containers. As of recently, AI responses often use `message-content` components
    // or specific `model-response` classes inside the chat display area.
    
    // Find all potential response containers
    // Note: We use querySelectorAll with common selectors. You might need to adjust this
    // if Gemini's DOM changes. Looking for elements that likely hold a response.
    const messageContainers = document.querySelectorAll('message-content, .message-content, [data-message-author="model"], div[class*="model-response"]');

    messageContainers.forEach((container) => {
        // Prevent adding multiple buttons to the same container
        if (container.querySelector('.synapseip-sync-btn')) return;

        // Clean check for existing sync state
        const textClone = container.cloneNode(true);
        const snippet = textClone.innerText.trim().substring(0, 60).replace(/\s+/g, ' ');
        
        let syncedIndex = -1;
        if (syncedSources.length > 0 && snippet.length > 5) {
            syncedIndex = syncedSources.findIndex(s => {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = s.content;
                const plainText = (tempDiv.innerText || tempDiv.textContent || "").replace(/\s+/g, ' ');
                return plainText.includes(snippet);
            });
        }

        // Derive exact chronological index by checking surrounding tree without double-counting nested wrappers
        const allModelRuns = Array.from(document.querySelectorAll('.model-turn, message-content, [data-message-author="model"], div[class*="model-response"]'));
        const uniqueNodes = allModelRuns.filter(n => !allModelRuns.some(other => other !== n && n.contains(other)));
        const myIndex = uniqueNodes.findIndex(n => n.contains(container) || n === container);
        const conversationalIndex = myIndex !== -1 ? myIndex + 1 : "?";

        // Create the button
        const btn = document.createElement('button');
        btn.className = 'synapseip-sync-btn';
        
        if (syncedIndex !== -1) {
            btn.classList.add('synced');
            btn.innerText = `Synced Conversation Note #${conversationalIndex} ✓`;
            btn.disabled = true;
        } else {
            btn.innerText = 'Sync to SynapseIP';
        }
        
        btn.addEventListener('click', () => {
            btn.classList.add('synapseip-syncing');
            btn.innerText = 'Syncing...';
            btn.disabled = true;

            // Extract the text of THIS specific response only
            // We clone the container and remove the button itself from the text extraction
            const clone = container.cloneNode(true);
            const wrapperInClone = clone.querySelector('.synapseip-btn-wrapper');
            if (wrapperInClone) wrapperInClone.remove();
            else {
                const oldBtn = clone.querySelector('.synapseip-sync-btn');
                if (oldBtn) oldBtn.remove();
            }

            const htmlContent = clone.innerHTML;
            const sourceUrl = window.location.href;
            
            // Grab the user's prompt by finding the closest preceding node
            let userPromptText = "";
            try {
                // Remove generic [class*="user-"] because it catches avatars and labels that just say "You said"
                const allUserNodes = Array.from(document.querySelectorAll('user-query, [data-message-author="user"]'));
                const previousUserNodes = allUserNodes.filter(n => 
                    n.compareDocumentPosition(container) & Node.DOCUMENT_POSITION_FOLLOWING
                );
                if (previousUserNodes.length > 0) {
                    const match = previousUserNodes[previousUserNodes.length - 1];
                    // User prompts don't need raw HTML since they don't have bold/bullet formatting.
                    // Extracting text prevents catching invisible web-components.
                    let text = match.innerText || match.textContent;
                    // Strip the visually-hidden "You said" accessibility label
                    userPromptText = text.replace(/^(You said|You)\s*\n?/i, '').trim();
                }
            } catch (e) { console.error(e); }
            
            let combinedContent = htmlContent;
            if (userPromptText) {
                const escapeUser = userPromptText.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                combinedContent = `<div class="gemini-prompt"><strong>User Prompt:</strong><br><p>${escapeUser}</p></div><hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;"><div class="gemini-response"><strong>AI Response:</strong><br>${htmlContent}</div>`;
            }

            // Send standard payload structure expected by the FastAPI backend
            const payload = {
                title: `Gemini Source Node #${conversationalIndex} - ${new Date().toLocaleString()}`,
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
                    btn.innerText = `Synced Conversation Note #${conversationalIndex} ✓`;
                    if (!syncedSources.some(s => s.content.includes(htmlContent.substring(0, 50)))) {
                        syncedSources.push({
                            content: `<div>${combinedContent}</div>`
                        });
                    }
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
            }, 5000); // 5 seconds wait per user request
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

        container.appendChild(wrapper);
    });
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
