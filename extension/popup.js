document.addEventListener('DOMContentLoaded', () => {
  const captureBtn = document.getElementById('capture-btn');
  const statusDiv = document.getElementById('status');

  captureBtn.addEventListener('click', async () => {
    captureBtn.disabled = true;
    captureBtn.innerText = "Capturing...";
    statusDiv.innerText = "Taking screenshot...";

    try {
      // 1. Get active project and auth details
      const result = await new Promise((resolve) => {
        chrome.storage.local.get(['synapseip_auth_token', 'synapseip_server_url', 'synapseip_active_project'], resolve);
      });

      const token = result.synapseip_auth_token;
      const serverUrl = result.synapseip_server_url || "https://synapseip-1ncu.onrender.com";
      const activeProject = result.synapseip_active_project;

      if (!token || !activeProject) {
        statusDiv.innerText = "Error: Not authenticated or no project selected.";
        captureBtn.innerText = "Error";
        return;
      }

      // 2. Capture the visible tab
      const currentWindow = await chrome.windows.getCurrent();
      const dataUrl = await new Promise((resolve, reject) => {
        chrome.tabs.captureVisibleTab(currentWindow.id, { format: 'jpeg', quality: 80 }, (dataUrl) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else {
            resolve(dataUrl);
          }
        });
      });

      // 3. Send to backend
      statusDiv.innerText = "Analyzing UI with Gemini Vision...";
      captureBtn.innerText = "Processing...";

      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const sourceUrl = activeTab.url || "Captured UI";

      const response = await fetch(`${serverUrl}/api/ext/sources/vision`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          project_id: activeProject.id,
          source_url: sourceUrl,
          image_base64: dataUrl
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      statusDiv.innerText = "✅ Design Tokens Extracted & Saved!";
      statusDiv.style.color = "#10b981";
      captureBtn.innerText = "Done!";

      setTimeout(() => {
        window.close();
      }, 2000);

    } catch (err) {
      console.error(err);
      statusDiv.innerText = `Error: ${err.message}`;
      statusDiv.style.color = "#ef4444";
      captureBtn.innerText = "Failed";
      captureBtn.disabled = false;
    }
  });
});
