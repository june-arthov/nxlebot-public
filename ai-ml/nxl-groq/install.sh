#!/bin/bash
# Install Nxlebot Groq Client

echo "🔧 Installing Nxlebot Groq Client..."

# Install groq package
pip install groq -q

# Make executable
chmod +x /home/nxelleai/.openclaw/workspace/nxl-groq/nxl-groq
chmod +x /home/nxelleai/.openclaw/workspace/nxl-groq/groq_client.py

# Add to PATH
echo 'export PATH="$PATH:/home/nxelleai/.openclaw/workspace/nxl-groq"' >> ~/.bashrc
echo 'alias nxl-groq="/home/nxelleai/.openclaw/workspace/nxl-groq/nxl-groq"' >> ~/.bashrc

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  nxl-groq              # Interactive mode"
echo "  nxl-groq 'message'    # Single message"
echo ""
echo "Models available:"
echo "  - llama-3.3-70b-versatile (default)"
echo "  - llama-3.1-8b-instant"
echo "  - mixtral-8x7b-32768"
echo "  - gemma2-9b-it"
echo ""
echo "Run: source ~/.bashrc"
