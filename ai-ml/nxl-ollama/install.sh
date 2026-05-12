#!/bin/bash
# Install Nxlebot Ollama CLI

echo "🔧 Installing Nxlebot Ollama Integration..."

# Make executable
chmod +x /home/nxelleai/.openclaw/workspace/nxl-ollama/nxl
chmod +x /home/nxelleai/.openclaw/workspace/nxl-ollama/ollama_client.py

# Add to PATH
echo 'export PATH="$PATH:/home/nxelleai/.openclaw/workspace/nxl-ollama"' >> ~/.bashrc

# Create alias
echo 'alias nxl="/home/nxelleai/.openclaw/workspace/nxl-ollama/nxl"' >> ~/.bashrc

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  nxl              # Interactive mode"
echo "  nxl 'message'    # Single message"
echo ""
echo "Reload shell or run: source ~/.bashrc"
