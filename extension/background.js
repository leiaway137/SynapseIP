// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "save_auth_token") {
      chrome.storage.local.set({ 
          synapseip_auth_token: request.token,
          synapseip_server_url: request.server || "https://synapseip-1ncu.onrender.com"
      }, () => {
          console.log("SynapseIP Messenger: Auth token securely saved to extension storage.");
      });
      return false;
  }

  // ---- Project Management Actions ----

  if (request.action === "fetch_projects") {
    chrome.storage.local.get(['synapseip_auth_token', 'synapseip_server_url'], async (result) => {
        const token = result.synapseip_auth_token;
        const serverUrl = result.synapseip_server_url || "https://synapseip-1ncu.onrender.com";
        if (!token) {
            sendResponse({ status: "error", error: "Not authenticated" });
            return;
        }
        try {
            const response = await fetch(`${serverUrl}/api/ext/projects`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const projects = await response.json();
            sendResponse({ status: "success", projects });
        } catch (error) {
            console.error("SynapseIP: Failed to fetch projects", error);
            sendResponse({ status: "error", error: error.message });
        }
    });
    return true;
  }

  if (request.action === "create_project") {
    chrome.storage.local.get(['synapseip_auth_token', 'synapseip_server_url'], async (result) => {
        const token = result.synapseip_auth_token;
        const serverUrl = result.synapseip_server_url || "https://synapseip-1ncu.onrender.com";
        if (!token) {
            sendResponse({ status: "error", error: "Not authenticated" });
            return;
        }
        try {
            const response = await fetch(`${serverUrl}/api/ext/projects`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ name: request.name })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const project = await response.json();
            // Auto-select the newly created project
            chrome.storage.local.set({ synapseip_active_project: project });
            sendResponse({ status: "success", project });
        } catch (error) {
            console.error("SynapseIP: Failed to create project", error);
            sendResponse({ status: "error", error: error.message });
        }
    });
    return true;
  }

  if (request.action === "set_active_project") {
    chrome.storage.local.set({ synapseip_active_project: request.project }, () => {
        console.log("SynapseIP Messenger: Active project set to:", request.project.name);
        sendResponse({ status: "success" });
    });
    return true;
  }

  if (request.action === "get_active_project") {
    chrome.storage.local.get(['synapseip_active_project'], (result) => {
        sendResponse({ status: "success", project: result.synapseip_active_project || null });
    });
    return true;
  }

  // ---- Sync Action ----

  if (request.action === "sync_to_synapseip") {
    console.log("SynapseIP Messenger: Initiating sync request", request.data.title);
    
    chrome.storage.local.get(['synapseip_auth_token', 'synapseip_server_url', 'synapseip_active_project'], (result) => {
        const token = result.synapseip_auth_token;
        const serverUrl = result.synapseip_server_url || "https://synapseip-1ncu.onrender.com";
        const activeProject = result.synapseip_active_project;
        
        console.log("SynapseIP Messenger: Using server URL:", serverUrl, 
                     "| Token present:", !!token,
                     "| Target project:", activeProject ? activeProject.name : "auto (most recent)");

        if (!token) {
            console.error("SynapseIP Messenger: Missing Auth Token.");
            sendResponse({ status: "error", error: "Missing Auth Token. Please log into the SynapseIP dashboard first." });
            return;
        }

        // Include project_id in payload if user has selected a project
        const payload = { ...request.data };
        if (activeProject && activeProject.id) {
            payload.project_id = activeProject.id;
        }

        async function attemptFetch(retries = 2, delay = 2000) {
            for (let attempt = 0; attempt <= retries; attempt++) {
                try {
                    const response = await fetch(`${serverUrl}/ingest`, {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify(payload)
                    });
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return await response.json();
                } catch (error) {
                    console.warn(`SynapseIP Messenger: Fetch attempt ${attempt + 1}/${retries + 1} failed:`, error.message);
                    if (attempt < retries) {
                        await new Promise(r => setTimeout(r, delay * (attempt + 1)));
                    } else {
                        throw error;
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
    
    return true;
  }
});
