// State
let syncActive = false;

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "sync_to_synapseip") {
    console.log("SynapseIP Messenger: Initiating sync request", request.data.title);
    
    fetch("http://127.0.0.1:8000/ingest", {
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
        
        chrome.tabs.query({}, function(tabs) {
            for (let tab of tabs) {
                chrome.tabs.sendMessage(tab.id, {
                    action: "global_sync_update",
                    htmlContent: request.data.content,
                    totalCount: data.total_count
                }, () => { if (chrome.runtime.lastError) {} });
            }
        });
    })
    .catch((error) => {
        console.error("SynapseIP Messenger: Error synching to backend", error);
        sendResponse({ status: "error", error: error.message });
    });
    
    return true; // Keep the message channel open for async response
  } else if (request.action === "fetch_synced_sources") {
    fetch("http://127.0.0.1:8000/api/sources", {
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
  } else if (request.action === "desync_from_synapseip") {
    fetch("http://127.0.0.1:8000/api/sources/bulk-delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_ids: [request.data.id] })
    })
    .then(response => response.json())
    .then(data => sendResponse({ status: "success" }))
    .catch(error => {
      console.error("SynapseIP Messenger: Error desyncing source", error);
      sendResponse({ status: "error", error: error.message });
    });
    return true;
  } else if (request.action === "report_structural_change") {
    fetch("http://127.0.0.1:8000/api/report-change", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ html_payload: request.html_payload, hostname: request.hostname })
    })
    .then(response => response.json())
    .then(data => {
        if (data.new_selector) {
            chrome.storage.local.get("extensionSelectors", (storage) => {
                const currentData = storage.extensionSelectors || {};
                currentData[request.hostname] = data.new_selector;
                chrome.storage.local.set({ "extensionSelectors": currentData });
            });
            sendResponse({ status: "success", new_selector: data.new_selector });
        }
    })
    .catch(error => {
      console.error("SynapseIP Messenger: Sentinel fix failed", error);
      sendResponse({ status: "error", error: error.message });
    });
    return true;
  }
});

// Real-Time Desync Listener
function connectWebSocket() {
  const socket = new WebSocket('ws://127.0.0.1:8000/ws');
  
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

// Sentinel Auto-Updater
function fetchSystemConfig() {
    fetch("http://127.0.0.1:8000/api/config/selectors", { cache: "no-store" })
    .then(res => res.json())
    .then(data => {
        if (Object.keys(data).length > 0) {
            console.log("SynapseIP Sentinel: Downloaded dynamic selector config map.");
            chrome.storage.local.set({ "extensionSelectors": data });
        }
    }).catch(e => console.error("SynapseIP Sentinel: Could not reach backend for config.", e));
}

chrome.runtime.onStartup.addListener(fetchSystemConfig);
chrome.runtime.onInstalled.addListener(fetchSystemConfig);
fetchSystemConfig();
