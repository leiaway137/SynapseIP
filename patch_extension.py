import re

file_path = "/Users/leiaway/Library/Mobile Documents/com~apple~CloudDocs/AI Learning/SynapseIP/extension/content.js"

with open(file_path, "r") as f:
    text = f.read()

old_block = """        if (syncedIndex !== -1) {
            btn.classList.add('synced');
            btn.innerText = `Synced Conversation Note #${conversationalIndex} ✓`;
            btn.disabled = true;
        } else {
            btn.innerText = 'Sync to SynapseIP';
        }
        
        btn.addEventListener('click', () => {"""

new_block = """        if (syncedIndex !== -1) {
            btn.classList.add('synced');
            btn.innerText = `Synced Note #${conversationalIndex} ✓ (Click to Desync)`;
            btn.disabled = false;
            
            btn.addEventListener('click', () => {
                btn.classList.add('synapseip-syncing');
                btn.innerText = 'Desyncing...';
                btn.disabled = true;
                
                chrome.runtime.sendMessage({ 
                    action: "desync_from_synapseip", 
                    data: { id: syncedSources[syncedIndex].id } 
                }, (response) => {
                    if (chrome.runtime.lastError) {
                        btn.classList.remove('synapseip-syncing');
                        btn.innerText = 'Desync Failed ✗';
                        setTimeout(() => { btn.disabled = false; btn.innerText = `Synced Note #${conversationalIndex} ✓ (Click to Desync)`; }, 2000);
                    }
                });
            });
            
        } else {
            btn.innerText = 'Sync to SynapseIP';
            
            btn.addEventListener('click', () => {"""

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    with open(file_path, "w") as f:
        f.write(text)
    print("content.js patched successfully.")
else:
    print("Could not find old_block in content.js")
