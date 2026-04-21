import re
import os

ext_dir = "/Users/leiaway/Library/Mobile Documents/com~apple~CloudDocs/AI Learning/SynapseIP/extension"

for filename in ["background.js", "manifest.json"]:
    filepath = os.path.join(ext_dir, filename)
    with open(filepath, "r") as f:
        text = f.read()
    
    text = text.replace("http://localhost:8000", "https://synapseip-1ncu.onrender.com")
    text = text.replace("ws://localhost:8000", "wss://synapseip-1ncu.onrender.com")
    
    with open(filepath, "w") as f:
        f.write(text)
    print(f"Updated {filename}")

