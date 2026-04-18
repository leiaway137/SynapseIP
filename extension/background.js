// Queue State
const syncQueue = [];
let isProcessingQueue = false;

async function processSyncQueue() {
    if (isProcessingQueue || syncQueue.length === 0) return;
    isProcessingQueue = true;

    while (syncQueue.length > 0) {
        const { request, sendResponse } = syncQueue.shift();
        
        try {
            const response = await fetch("http://localhost:8000/ingest", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(request.data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("SynapseIP Messenger: Data successfully ingested", data);
            
            sendResponse({ status: "success", backendResponse: data });
            
            // Global Broadcast to synchronize all isolated tabs 
            chrome.tabs.query({}, function(tabs) {
                for (let tab of tabs) {
                    chrome.tabs.sendMessage(tab.id, {
                        action: "global_sync_update",
                        htmlContent: request.data.content,
                        totalCount: data.total_count
                    }, () => {
                        if (chrome.runtime.lastError) {}
                    });
                }
            });
            
            // Artificial 150ms delay between consecutive queue items to protect SQLite from concurrent write blocks
            await new Promise(resolve => setTimeout(resolve, 150));
            
        } catch (error) {
            console.error("SynapseIP Messenger: Error synching to backend", error);
            sendResponse({ status: "error", error: error.message });
        }
    }
    
    isProcessingQueue = false;
}

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "sync_to_synapseip") {
    console.log("SynapseIP Messenger: Queueing sync request", request.data.title);
    syncQueue.push({ request, sendResponse });
    processSyncQueue();
    return true; // Keep the message channel open for async response
  } else if (request.action === "fetch_synced_sources") {
    fetch("http://localhost:8000/api/sources", {
      method: "GET",
      cache: "no-store"
    })
    .then(response => response.json())
    .then(data => sendResponse({ status: "success", sources: data }))
    .catch(error => {
      console.error("SynapseIP Messenger: Error fetching sources", error);
      sendResponse({ status: "error", error: error.message });
    });
    return true;
  }
});

// Real-Time Desync Listener
function connectWebSocket() {
  const socket = new WebSocket('ws://localhost:8000/ws');
  
  socket.onopen = function() {
      // Always resync when websocket connects/reconnects
      console.log("SynapseIP Messenger: Websocket connected. Forcing global sync.");
      chrome.tabs.query({}, function(tabs) {
          for (let tab of tabs) {
              chrome.tabs.sendMessage(tab.id, { action: "global_desync" }, () => {
                  if (chrome.runtime.lastError) {}
              });
          }
      });
  };

  socket.onmessage = function(event) {
      try {
          const data = JSON.parse(event.data);
          if (data.type === "sources_deleted") {
              console.log("SynapseIP Messenger: Detected backend deletion. Forcing global desync.");
              chrome.tabs.query({}, function(tabs) {
                  for (let tab of tabs) {
                      chrome.tabs.sendMessage(tab.id, { action: "global_desync" }, () => {
                          if (chrome.runtime.lastError) {}
                      });
                  }
              });
          }
      } catch (e) {}
  };

  socket.onclose = function(e) {
    // Reconnect loop if backend goes down or reloads
    setTimeout(connectWebSocket, 3000); 
  };
  
  socket.onerror = function(e) {
    socket.close();
  }
}

// Initialize realtime connection bridging
connectWebSocket();
