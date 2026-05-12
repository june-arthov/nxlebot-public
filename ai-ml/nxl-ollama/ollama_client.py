#!/usr/bin/env python3
"""
Nxlebot Ollama Client - FREE AI Integration
Connects to Ollama on Windows from WSL
"""

import requests
import json
import sys

OLLAMA_HOST = "http://172.26.16.1:11434"
MODEL = "qwen2.5-coder:7b"

class OllamaClient:
    def __init__(self, host=OLLAMA_HOST, model=MODEL):
        self.host = host
        self.model = model
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self):
        """Load Nxlebot personality from SOUL.md"""
        try:
            with open('/home/nxelleai/.openclaw/workspace/SOUL.md', 'r') as f:
                return f.read()
        except:
            return "You are Nxlebot, Best King of the King Hacker. Direct, efficient, bro-style."
    
    def chat(self, message, stream=True):
        """Send message to Ollama and get response"""
        url = f"{self.host}/api/generate"
        
        # Build prompt with context
        prompt = f"""{self.system_prompt}

User: {message}

Nxlebot:"""
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "num_predict": 2048
            }
        }
        
        try:
            response = requests.post(url, json=data, stream=stream, timeout=120)
            
            if stream:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            full_response += chunk['response']
                            print(chunk['response'], end='', flush=True)
                        if chunk.get('done'):
                            break
                print()  # New line at end
                return full_response
            else:
                return response.json()['response']
                
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Can't connect to Ollama!")
            print("Make sure Ollama is running on Windows")
            print(f"Check: {self.host}")
            return None
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def check_status(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            models = response.json().get('models', [])
            print(f"✅ Ollama connected!")
            print(f"Available models: {[m['name'] for m in models]}")
            return True
        except:
            print(f"❌ Ollama not reachable at {self.host}")
            return False

if __name__ == "__main__":
    client = OllamaClient()
    
    if len(sys.argv) > 1:
        # Single message mode
        message = " ".join(sys.argv[1:])
        client.chat(message)
    else:
        # Interactive mode
        print("🔥 Nxlebot Ollama Mode - Type 'exit' to quit\n")
        
        if not client.check_status():
            sys.exit(1)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👑 Nxlebot out!")
                    break
                if not user_input:
                    continue
                
                print("Nxlebot: ", end='', flush=True)
                client.chat(user_input)
                
            except KeyboardInterrupt:
                print("\n👑 Nxlebot out!")
                break
            except EOFError:
                break
