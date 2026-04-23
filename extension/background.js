// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "sync_to_synapseip") {
    console.log("SynapseIP Messenger: Initiating sync request", request.data.title);
    
    fetch("https://synapseip-1ncu.onrender.com/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
    
    return true; // Keep the message channel open for async response
  }
});
