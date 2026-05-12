#!/usr/bin/env python3
"""
Nxlebot Groq Client - FREE 1M tokens/day
Lightning fast inference with Mixtral & Llama 3
"""

import os
import sys
import json

try:
    from groq import Groq
except ImportError:
    print("Installing groq package...")
    os.system("pip install groq -q")
    from groq import Groq

# API Key from user
GROQ_API_KEY = "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"

class GroqClient:
    def __init__(self, api_key=GROQ_API_KEY):
        self.client = Groq(api_key=api_key)
        self.system_prompt = self._load_personality()
        
    def _load_personality(self):
        """Load Nxlebot personality"""
        try:
            with open('/home/nxelleai/.openclaw/workspace/SOUL.md', 'r') as f:
                return f.read()
        except:
            return "You are Nxlebot - Best King of the King Hacker. Direct, efficient, bro-style Bahasa Indonesia."
    
    def chat(self, message, model="llama-3.3-70b-versatile", stream=True):
        """Chat with Groq"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                temperature=0.7,
                max_tokens=4096
            )
            
            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        print(content, end='', flush=True)
                print()
                return full_response
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def list_models(self):
        """List available models"""
        models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        return models

if __name__ == "__main__":
    print("🔥 Nxlebot Groq Mode - FREE 1M tokens/day\n")
    
    client = GroqClient()
    
    print("Available models:")
    for i, model in enumerate(client.list_models(), 1):
        print(f"  {i}. {model}")
    print()
    
    # Default model
    model = "llama-3.3-70b-versatile"
    
    if len(sys.argv) > 1:
        # Single message mode
        message = " ".join(sys.argv[1:])
        print(f"Model: {model}\n")
        print("Nxlebot: ", end='', flush=True)
        client.chat(message, model=model)
    else:
        # Interactive mode
        print(f"Using model: {model}")
        print("Commands: /model <name>, /exit, /models\n")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input == "/exit":
                    print("👑 Nxlebot out!")
                    break
                    
                if user_input == "/models":
                    print("\nAvailable models:")
                    for i, m in enumerate(client.list_models(), 1):
                        marker = " ✓" if m == model else ""
                        print(f"  {i}. {m}{marker}")
                    continue
                    
                if user_input.startswith("/model "):
                    new_model = user_input.split("/model ")[1].strip()
                    if new_model in client.list_models():
                        model = new_model
                        print(f"✓ Switched to: {model}")
                    else:
                        print(f"❌ Unknown model: {new_model}")
                    continue
                
                print("Nxlebot: ", end='', flush=True)
                client.chat(user_input, model=model)
                
            except KeyboardInterrupt:
                print("\n👑 Nxlebot out!")
                break
            except EOFError:
                break
