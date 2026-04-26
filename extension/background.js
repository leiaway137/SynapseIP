// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "save_auth_token") {
      chrome.storage.local.set({ 
          synapseip_auth_token: request.token,
          synapseip_server_url: request.server || "https://synapseip-1ncu.onrender.com"
      }, () => {
          console.log("SynapseIP Messenger: Auth token securely saved to extension storage.");
      });
      return false; // synchronous response not needed
  }

  if (request.action === "sync_to_synapseip") {
    console.log("SynapseIP Messenger: Initiating sync request", request.data.title);
    
    chrome.storage.local.get(['synapseip_auth_token', 'synapseip_server_url'], (result) => {
        const token = result.synapseip_auth_token;
        const serverUrl = result.synapseip_server_url || "https://synapseip-1ncu.onrender.com";
        
        console.log("SynapseIP Messenger: Using server URL:", serverUrl, "| Token present:", !!token);

        if (!token) {
            console.error("SynapseIP Messenger: Missing Auth Token. Please log into the SynapseIP dashboard first.");
            sendResponse({ status: "error", error: "Missing Auth Token. Please log into the SynapseIP dashboard first." });
            return;
        }

        // Retry wrapper to handle Render cold-start "Failed to fetch" errors
        async function attemptFetch(retries = 2, delay = 2000) {
            for (let attempt = 0; attempt <= retries; attempt++) {
                try {
                    const response = await fetch(`${serverUrl}/ingest`, {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify(request.data)
                    });
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return await response.json();
                } catch (error) {
                    console.warn(`SynapseIP Messenger: Fetch attempt ${attempt + 1}/${retries + 1} failed:`, error.message);
                    if (attempt < retries) {
                        // Wait before retrying (exponential backoff)
                        await new Promise(r => setTimeout(r, delay * (attempt + 1)));
                    } else {
                        throw error; // Final attempt failed, propagate
                    }
                }
            }
        }

        attemptFetch()
            .then((data) => {
                console.log("SynapseIP Messenger: Data successfully ingested", data);
                sendResponse({ status: "success", backendResponse: data });
            })
            .catch((error) => {
                console.error("SynapseIP Messenger: Error synching to backend", error);
                let errorMessage = error.message;
                if (errorMessage === 'Failed to fetch' || errorMessage.includes('NetworkError')) {
                    errorMessage = "Network error: The SynapseIP server might be sleeping or unreachable. Please try again in 30 seconds.";
                }
                sendResponse({ status: "error", error: errorMessage });
            });
    });
    
    return true; // Keep the message channel open for async response
  }
});
