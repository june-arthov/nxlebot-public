#!/usr/bin/env python3
"""
Nxlebot Chat Backend - Sync Telegram + Web GUI
Integrates OpenClaw Telegram bot with web chat interface
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__, static_folder='../chat-gui', static_url_path='')
CORS(app)  # Enable CORS for web GUI

# Configuration
CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'chat_history.json')
TELEGRAM_USER_ID = "8621864972"  # Nyxelle's Telegram ID

# In-memory chat history (will be saved to file)
chat_history = {
    "sessions": {},
    "messages": []
}

def load_chat_history():
    """Load chat history from file"""
    global chat_history
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
            print(f"✅ Loaded {len(chat_history.get('messages', []))} messages from history")
        except Exception as e:
            print(f"⚠️ Error loading history: {e}")
            chat_history = {"sessions": {}, "messages": []}
    else:
        print("📝 Creating new chat history file")
        save_chat_history()

def save_chat_history():
    """Save chat history to file"""
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(chat_history.get('messages', []))} messages")
    except Exception as e:
        print(f"❌ Error saving history: {e}")

def add_message(text, is_user=True, platform="web", session_id=None):
    """Add message to chat history"""
    message = {
        "id": str(uuid.uuid4()),
        "text": text,
        "is_user": is_user,
        "platform": platform,  # "web" or "telegram"
        "session_id": session_id or "default",
        "timestamp": datetime.now().isoformat(),
        "user_id": TELEGRAM_USER_ID if is_user else "bot"
    }
    
    chat_history["messages"].append(message)
    
    # Keep only last 1000 messages
    if len(chat_history["messages"]) > 1000:
        chat_history["messages"] = chat_history["messages"][-1000:]
    
    save_chat_history()
    return message

def get_recent_messages(limit=50):
    """Get recent messages"""
    messages = chat_history.get("messages", [])[-limit:]
    return messages

def get_bot_response(user_message):
    """
    Generate bot response
    TODO: Integrate with OpenClaw API or AI model
    For now, use simple rule-based responses
    """
    lower = user_message.lower()
    
    # Custom responses
    if any(word in lower for word in ['halo', 'hai', 'hi', 'assalamualaikum']):
        return "Halo bro! 👋 Ada yang bisa gua bantu?"
    elif 'apa kabar' in lower:
        return "Gua baik bro! Siap bantu lu! 🚀"
    elif any(word in lower for word in ['terima kasih', 'makasih', 'thanks']):
        return "Santai bro! Siempre siap bantu! 🫡"
    elif any(word in lower for word in ['dadah', 'bye', 'see you']):
        return "Sampai jumpa bro! Take care! 👋"
    elif 'bug bounty' in lower:
        return "Bug bounty topik favorit gua! 🐛💰 Mau hunt target apa hari ini?"
    elif any(word in lower for word in ['coding', 'code', 'program']):
        return "Coding time! 💻 Mau build apa hari ini?"
    elif 'telegram' in lower:
        return "Iya bro! Sekarang chat kita sync antara web dan Telegram! Bisa pindah platform tanpa kehilangan history! 🎉"
    elif 'browser' in lower:
        return "Gimana tampilan web-nya? Oke gak? Kalau ada yang perlu diperbaiki kasih tau gua! 😊"
    
    # Default responses
    responses = [
        "Menarik! Ceritain lebih lanjut dong.",
        "Gua mengerti. Ada lagi yang mau dibahas?",
        "Pertanyaan bagus! Biar gua pikir dulu...",
        "Makasih udah share! Ada yang bisa gua bantu?",
        "Gua di sini buat bantu! Butuh apa?",
        "Siap! Ada lagi yang mau didiskusikan?",
        "Oke bro! Gua catat. Ada lagi?",
        "Interesting point! Tell me more!",
    ]
    
    import random
    return random.choice(responses)

# ===== API ENDPOINTS =====

@app.route('/')
def serve_gui():
    """Serve the web GUI"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from web GUI"""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    user_message = data['message']
    session_id = data.get('session_id', 'default')
    
    # Add user message to history
    add_message(user_message, is_user=True, platform="web", session_id=session_id)
    
    # Generate bot response
    bot_response = get_bot_response(user_message)
    
    # Add bot response to history
    add_message(bot_response, is_user=False, platform="web", session_id=session_id)
    
    return jsonify({
        "success": True,
        "response": bot_response,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history"""
    limit = request.args.get('limit', 50, type=int)
    session_id = request.args.get('session_id', 'default')
    
    messages = get_recent_messages(limit)
    
    # Filter by session if specified
    if session_id != 'default':
        messages = [m for m in messages if m.get('session_id') == session_id]
    
    return jsonify({
        "success": True,
        "messages": messages,
        "count": len(messages)
    })

@app.route('/api/telegram/message', methods=['POST'])
def telegram_webhook():
    """
    Webhook for Telegram messages
    Call this from OpenClaw when message received from Telegram
    """
    data = request.json
    
    # Expected format from Telegram/OpenClaw:
    # {
    #     "user_id": "8621864972",
    #     "message": "Hello",
    #     "message_id": 123,
    #     "chat_id": "telegram:8621864972"
    # }
    
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid Telegram message"}), 400
    
    user_message = data['message']
    user_id = data.get('user_id', TELEGRAM_USER_ID)
    message_id = data.get('message_id')
    
    # Add to chat history
    add_message(user_message, is_user=True, platform="telegram", session_id="default")
    
    # Generate bot response
    bot_response = get_bot_response(user_message)
    
    # Add bot response to history
    bot_message = add_message(bot_response, is_user=False, platform="telegram", session_id="default")
    
    # Return response for Telegram to send back
    return jsonify({
        "success": True,
        "response": bot_response,
        "message_id": message_id,
        "chat_history_saved": True
    })

@app.route('/api/sync', methods=['POST'])
def sync_chat():
    """Sync chat history between platforms"""
    data = request.json
    
    if not data or 'messages' not in data:
        return jsonify({"error": "No messages to sync"}), 400
    
    messages_to_sync = data['messages']
    platform = data.get('platform', 'unknown')
    
    synced_count = 0
    for msg in messages_to_sync:
        # Check if message already exists (by ID or timestamp)
        exists = any(
            m.get('id') == msg.get('id') or 
            (m.get('text') == msg.get('text') and m.get('timestamp') == msg.get('timestamp'))
            for m in chat_history["messages"]
        )
        
        if not exists:
            chat_history["messages"].append({
                "id": msg.get('id', str(uuid.uuid4())),
                "text": msg.get('text'),
                "is_user": msg.get('is_user', True),
                "platform": platform,
                "session_id": msg.get('session_id', 'default'),
                "timestamp": msg.get('timestamp', datetime.now().isoformat()),
                "user_id": msg.get('user_id', 'unknown')
            })
            synced_count += 1
    
    save_chat_history()
    
    return jsonify({
        "success": True,
        "synced_count": synced_count,
        "total_messages": len(chat_history["messages"])
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear chat history"""
    chat_history["messages"] = []
    save_chat_history()
    
    return jsonify({
        "success": True,
        "message": "Chat history cleared"
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get chat statistics"""
    messages = chat_history.get("messages", [])
    
    stats = {
        "total_messages": len(messages),
        "user_messages": len([m for m in messages if m.get('is_user')]),
        "bot_messages": len([m for m in messages if not m.get('is_user')]),
        "web_messages": len([m for m in messages if m.get('platform') == 'web']),
        "telegram_messages": len([m for m in messages if m.get('platform') == 'telegram']),
        "last_message": messages[-1].get('timestamp') if messages else None
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    print("🚀 Starting Nxlebot Chat Backend...")
    print("📍 Port: 5000")
    print("🌐 API: http://localhost:5000/api")
    print("💬 GUI: http://localhost:5000")
    print("=" * 50)
    
    load_chat_history()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
