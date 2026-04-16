// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "sync_to_synapseip") {
    console.log("SynapseIP Messenger: Received sync request", request.data);
    
    // Perform the fetch request in the background script to bypass CORS / Mixed Content issues
    fetch("http://localhost:8000/ingest", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(request.data)
    })
    .then(response => {
      if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log("SynapseIP Messenger: Data successfully ingested", data);
      sendResponse({ status: "success", backendResponse: data });
    })
    .catch(error => {
      console.error("SynapseIP Messenger: Error synching to backend", error);
      sendResponse({ status: "error", error: error.message });
    });

    // Return true to indicate that response will be sent asynchronously
    return true; 
  }
});
