#!/usr/bin/env python3
"""
Nxlebot Chat Backend - Sync Telegram + Web GUI
Simple HTTP server without Flask dependency
"""

import http.server
import socketserver
import json
import os
from datetime import datetime
import uuid
from urllib.parse import urlparse, parse_qs

PORT = 5000
CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'chat_history.json')
GUI_FOLDER = os.path.join(os.path.dirname(__file__), '../chat-gui')
TELEGRAM_USER_ID = "8621864972"

# In-memory chat history
chat_history = {"sessions": {}, "messages": []}

def load_chat_history():
    global chat_history
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
            print(f"✅ Loaded {len(chat_history.get('messages', []))} messages")
        except:
            chat_history = {"sessions": {}, "messages": []}
    save_chat_history()

def save_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Error saving: {e}")

def add_message(text, is_user=True, platform="web"):
    message = {
        "id": str(uuid.uuid4()),
        "text": text,
        "is_user": is_user,
        "platform": platform,
        "session_id": "default",
        "timestamp": datetime.now().isoformat(),
        "user_id": TELEGRAM_USER_ID if is_user else "bot"
    }
    chat_history["messages"].append(message)
    if len(chat_history["messages"]) > 1000:
        chat_history["messages"] = chat_history["messages"][-1000:]
    save_chat_history()
    return message

def get_bot_response(user_message):
    lower = user_message.lower()
    
    if any(word in lower for word in ['halo', 'hai', 'hi']):
        return "Halo bro! 👋 Ada yang bisa gua bantu?"
    elif 'apa kabar' in lower:
        return "Gua baik bro! Siap bantu lu! 🚀"
    elif any(word in lower for word in ['terima kasih', 'makasih']):
        return "Santai bro! Siempre siap bantu! 🫡"
    elif any(word in lower for word in ['dadah', 'bye']):
        return "Sampai jumpa bro! Take care! 👋"
    elif 'bug bounty' in lower:
        return "Bug bounty topik favorit gua! 🐛💰 Mau hunt target apa hari ini?"
    elif any(word in lower for word in ['coding', 'code']):
        return "Coding time! 💻 Mau build apa hari ini?"
    elif 'telegram' in lower:
        return "Iya bro! Sekarang chat kita sync antara web dan Telegram! 🎉"
    
    responses = [
        "Menarik! Ceritain lebih lanjut dong.",
        "Gua mengerti. Ada lagi yang mau dibahas?",
        "Pertanyaan bagus! Biar gua pikir dulu...",
        "Makasih udah share! Ada yang bisa gua bantu?",
        "Siap! Ada lagi yang mau didiskusikan?",
    ]
    
    import random
    return random.choice(responses)

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/history':
            self.send_json({
                "success": True,
                "messages": chat_history.get("messages", [])[-50:],
                "count": len(chat_history.get("messages", []))
            })
        elif parsed.path == '/api/stats':
            messages = chat_history.get("messages", [])
            self.send_json({
                "total_messages": len(messages),
                "user_messages": len([m for m in messages if m.get('is_user')]),
                "bot_messages": len([m for m in messages if not m.get('is_user')]),
            })
        elif parsed.path == '/':
            self.path = '/index.html'
            return super().do_GET()
        else:
            return super().do_GET()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data) if post_data else {}
        except:
            data = {}
        
        if parsed.path == '/api/chat':
            user_message = data.get('message', '')
            if user_message:
                add_message(user_message, is_user=True, platform="web")
                bot_response = get_bot_response(user_message)
                add_message(bot_response, is_user=False, platform="web")
                self.send_json({
                    "success": True,
                    "response": bot_response,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self.send_error(400, "No message")
        
        elif parsed.path == '/api/telegram/message':
            user_message = data.get('message', '')
            if user_message:
                add_message(user_message, is_user=True, platform="telegram")
                bot_response = get_bot_response(user_message)
                add_message(bot_response, is_user=False, platform="telegram")
                self.send_json({
                    "success": True,
                    "response": bot_response,
                    "chat_history_saved": True
                })
            else:
                self.send_error(400, "No message")
        
        elif parsed.path == '/api/sync':
            messages = data.get('messages', [])
            synced = 0
            for msg in messages:
                exists = any(m.get('id') == msg.get('id') for m in chat_history["messages"])
                if not exists:
                    chat_history["messages"].append(msg)
                    synced += 1
            save_chat_history()
            self.send_json({"success": True, "synced_count": synced})
        
        elif parsed.path == '/api/clear':
            chat_history["messages"] = []
            save_chat_history()
            self.send_json({"success": True, "message": "Cleared"})
        
        else:
            self.send_error(404, "Not found")
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__ == '__main__':
    print("🚀 Starting Nxlebot Chat Backend...")
    print(f"📍 Port: {PORT}")
    print(f"🌐 API: http://localhost:{PORT}/api")
    print(f"💬 GUI: http://localhost:{PORT}")
    print("=" * 50)
    
    load_chat_history()
    
    with socketserver.TCPServer(("", PORT), ChatHandler) as httpd:
        print(f"✅ Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
