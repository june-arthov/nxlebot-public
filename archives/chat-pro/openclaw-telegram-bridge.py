#!/usr/bin/env python3
"""
OpenClaw Telegram Bridge
Automatically sync Telegram messages to Nxlebot Chat Server
"""

import requests
import time
import json
import os
from datetime import datetime

# Configuration
CHAT_SERVER_URL = "http://localhost:8086"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OPENCLAW_API = "http://localhost:18789"  # OpenClaw Gateway API

# State file
STATE_FILE = os.path.join(os.path.dirname(__file__), "telegram_state.json")
last_message_id = 0

def load_state():
    global last_message_id
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                last_message_id = data.get('last_message_id', 0)
                print(f"✅ Loaded state: last_message_id={last_message_id}")
        except:
            pass
    else:
        save_state()

def save_state():
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_message_id': last_message_id}, f)

def get_telegram_messages():
    """Fetch messages from Telegram via OpenClaw API or Bot API"""
    
    # Option 1: Via OpenClaw Gateway (if available)
    try:
        response = requests.get(f"{OPENCLAW_API}/api/messages/recent", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('messages', [])
    except Exception as e:
        print(f"⚠️ OpenClaw API not available: {e}")
    
    # Option 2: Via Telegram Bot API (if token provided)
    if TELEGRAM_BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {'offset': last_message_id + 1, 'timeout': 10}
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                updates = data.get('result', [])
                messages = []
                for update in updates:
                    if 'message' in update:
                        msg = update['message']
                        messages.append({
                            'message_id': msg['message_id'],
                            'from_user': msg.get('from', {}).get('id', 'unknown'),
                            'text': msg.get('text', ''),
                            'chat_id': msg.get('chat', {}).get('id', '')
                        })
                        last_message_id = msg['message_id']
                save_state()
                return messages
        except Exception as e:
            print(f"⚠️ Telegram Bot API error: {e}")
    
    return []

def sync_to_chat_server(messages):
    """Forward Telegram messages to chat server"""
    for msg in messages:
        text = msg.get('text', '')
        if not text:
            continue
        
        user_id = str(msg.get('from_user', 'unknown'))
        message_id = msg.get('message_id', 0)
        
        try:
            response = requests.post(
                f"{CHAT_SERVER_URL}/api/telegram/message",
                json={
                    'user_id': user_id,
                    'message': text,
                    'message_id': message_id
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Synced: {text[:50]}...")
                
                # Optional: Send bot response back to Telegram
                if data.get('response') and TELEGRAM_BOT_TOKEN:
                    send_telegram_response(user_id, data['response'])
                    
        except Exception as e:
            print(f"❌ Sync error: {e}")

def send_telegram_response(chat_id, text):
    """Send bot response back to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': chat_id, 'text': text}
        requests.post(url, json=data, timeout=5)
    except Exception as e:
        print(f"⚠️ Send response error: {e}")

def main():
    print("="*60)
    print("🌉 OpenClaw Telegram Bridge")
    print("="*60)
    print(f"Chat Server: {CHAT_SERVER_URL}")
    print(f"OpenClaw API: {OPENCLAW_API}")
    print(f"Telegram Bot: {'✅' if TELEGRAM_BOT_TOKEN else '❌ (not configured)'}")
    print("="*60)
    print("🔄 Polling for messages every 5 seconds...")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    load_state()
    
    while True:
        try:
            messages = get_telegram_messages()
            if messages:
                print(f"📨 Found {len(messages)} new message(s)")
                sync_to_chat_server(messages)
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
