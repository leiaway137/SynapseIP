console.log("SynapseIP Messenger: Content script loaded on Gemini.");

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

        // Create the button
        const btn = document.createElement('button');
        btn.className = 'synapseip-sync-btn';
        btn.innerText = 'Sync to SynapseIP';
        
        // Add click listener
        btn.addEventListener('click', () => {
            btn.innerText = 'Syncing...';
            btn.disabled = true;

            // Extract the text of THIS specific response only
            // We clone the container and remove the button itself from the text extraction
            const clone = container.cloneNode(true);
            const btnInClone = clone.querySelector('.synapseip-sync-btn');
            if (btnInClone) btnInClone.remove();

            const htmlContent = clone.innerHTML;
            const sourceUrl = window.location.href;
            
            // Grab the user's prompt by finding the closest preceding node
            let userPromptHtml = "";
            try {
                const allUserNodes = Array.from(document.querySelectorAll('[data-message-author="user"], user-query, [class*="user-"]'));
                const previousUserNodes = allUserNodes.filter(n => 
                    n.compareDocumentPosition(container) & Node.DOCUMENT_POSITION_FOLLOWING
                );
                if (previousUserNodes.length > 0) {
                    userPromptHtml = previousUserNodes[previousUserNodes.length - 1].innerHTML;
                }
            } catch (e) { console.error(e); }
            
            let combinedContent = htmlContent;
            if (userPromptHtml) {
                combinedContent = `<div class="gemini-prompt"><strong>User Prompt:</strong><br>${userPromptHtml}</div><hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;"><div class="gemini-response"><strong>AI Response:</strong><br>${htmlContent}</div>`;
            }

            // Send standard payload structure expected by the FastAPI backend
            const payload = {
                title: `Gemini Response - ${new Date().toLocaleString()}`,
                content: combinedContent,
                source_url: sourceUrl
            };

            // Send message to background script
            chrome.runtime.sendMessage({
                action: "sync_to_synapseip",
                data: payload
            }, (response) => {
                // Check for connection severing or other manifest errors
                if (chrome.runtime.lastError) {
                    console.error("SynapseIP Messenger Error:", chrome.runtime.lastError.message);
                    btn.classList.add('error');
                    btn.innerText = 'Failed ✗';
                    setTimeout(() => {
                        btn.classList.remove('error');
                        btn.innerText = 'Sync to SynapseIP';
                        btn.disabled = false;
                    }, 3000);
                    return;
                }

                // Background script returns a callback
                if (response && response.status === "success") {
                    btn.classList.add('synced');
                    btn.innerText = 'Synced ✓';
                } else {
                    btn.classList.add('error');
                    btn.innerText = 'Failed ✗';
                    console.error("SynapseIP Messenger Error:", response?.error);
                    
                    // Reset button after 3 seconds ONLY on error to allow retrying
                    setTimeout(() => {
                        btn.classList.remove('error');
                        btn.innerText = 'Sync to SynapseIP';
                        btn.disabled = false;
                    }, 3000);
                }
            });
        });

        // Append the button to the bottom of the container. 
        // Note: Sometimes `container.appendChild` might break internal React/Lit lifecycle if not careful,
        // but it's typically fine for simple elements at the end of the content.
        container.appendChild(btn);
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
