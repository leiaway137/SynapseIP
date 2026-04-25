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
        
        if (!token) {
            console.error("SynapseIP Messenger: Missing Auth Token. Please log into the SynapseIP dashboard first.");
            sendResponse({ status: "error", error: "Missing Auth Token. Please log into the SynapseIP dashboard first." });
            return;
        }

        fetch(`${serverUrl}/ingest`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(request.data)
        })
        .then(async (response) => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then((data) => {
            console.log("SynapseIP Messenger: Data successfully ingested", data);
            sendResponse({ status: "success", backendResponse: data });
        })
        .catch((error) => {
            console.error("SynapseIP Messenger: Error synching to backend", error);
            sendResponse({ status: "error", error: error.message });
        });
    });
    
    return true; // Keep the message channel open for async response
  }
});
