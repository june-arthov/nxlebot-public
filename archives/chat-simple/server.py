#!/usr/bin/env python3
"""
Nxlebot Simple Chat Server - All in One
Backend + GUI in single server - PASTI BISA!
"""

import http.server
import socketserver
import json
import os
from datetime import datetime
import uuid

PORT = 8080
CHAT_FILE = os.path.join(os.path.dirname(__file__), 'chat.json')

chat_history = []

def load_chat():
    global chat_history
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
            print(f"✅ Loaded {len(chat_history)} messages")
        except:
            chat_history = []
    save_chat()

def save_chat():
    with open(CHAT_FILE, 'w', encoding='utf-8') as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)

def get_response(msg):
    msg = msg.lower()
    if any(w in msg for w in ['halo', 'hai', 'hi']): return "Halo bro! 👋 Ada yang bisa gua bantu?"
    if 'apa kabar' in msg: return "Gua baik bro! Siap bantu lu! 🚀"
    if any(w in msg for w in ['makasih', 'terima kasih']): return "Santai bro! Siempre siap! 🫡"
    if any(w in msg for w in ['bye', 'dadah']): return "See you bro! 👋"
    if 'bug bounty' in msg: return "Bug bounty favorit gua! 🐛💰 Mau hunt apa?"
    if any(w in msg for w in ['coding', 'code']): return "Coding time! 💻 Build apa?"
    if 'telegram' in msg: return "Chat kita sync dengan Telegram! 🎉"
    return ["Menarik! Tell me more.", "Gua ngerti. Ada lagi?", "Oke bro! Lanjut!", "Siap!"][hash(msg) % 4]

HTML = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nxlebot Chat</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;height:100vh;display:flex;flex-direction:column}
.header{background:#1e293b;padding:15px 24px;border-bottom:1px solid #334155;display:flex;align-items:center;gap:12px}
.logo{width:45px;height:45px;border-radius:12px;background:linear-gradient(135deg,#2563eb,#10b981);display:flex;align-items:center;justify-content:center;font-size:1.8rem}
.status{display:flex;align-items:center;gap:6px;font-size:0.85rem;color:#94a3b8}
.dot{width:8px;height:8px;border-radius:50%;background:#10b981;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{display:flex;gap:10px;max-width:70%;animation:slide .3s}
@keyframes slide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.avatar{width:38px;height:38px;border-radius:10px;background:#334155;display:flex;align-items:center;justify-content:center;font-size:1.3rem}
.msg.user .avatar{background:linear-gradient(135deg,#2563eb,#10b981)}
.content{background:#1e293b;padding:12px 16px;border-radius:14px;line-height:1.5;border:1px solid #334155}
.msg.user .content{background:linear-gradient(135deg,#2563eb,#10b981);border:none}
.time{font-size:.7rem;color:#64748b;margin-top:4px;text-align:right}
.typing{display:flex;gap:5px;padding:12px 16px;background:#1e293b;border-radius:14px;width:fit-content;margin-left:48px}
.typing-dot{width:7px;height:7px;border-radius:50%;background:#64748b;animation:typing 1.4s infinite}
.typing-dot:nth-child(2){animation-delay:.2s}.typing-dot:nth-child(3){animation-delay:.4s}
@keyframes typing{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
.input{background:#1e293b;border-top:1px solid #334155;padding:20px}
.input-wrap{max-width:900px;margin:0 auto;display:flex;gap:10px}
.input-box{flex:1;background:#334155;border-radius:12px;border:2px solid transparent;transition:.3s}
.input-box:focus-within{border-color:#2563eb}
#msg{width:100%;background:0 0;border:0;padding:14px 18px;color:#f8fafc;font-size:1rem;outline:0;resize:none;min-height:50px}
#send{background:linear-gradient(135deg,#2563eb,#10b981);color:#fff;border:0;border-radius:12px;width:52px;height:52px;cursor:pointer;font-size:1.3rem;transition:.3s}
#send:hover{transform:translateY(-2px) scale(1.05)}
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center}
.emoji{font-size:4rem;margin-bottom:20px;animation:float 3s infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.badge{background:#10b981;color:#fff;padding:5px 14px;border-radius:20px;font-size:.8rem;font-weight:600;margin-top:12px;display:inline-block}
</style>
</head>
<body>
<div class="header">
<div class="logo">🤖</div>
<div>
<div style="font-weight:600;font-size:1.1rem">Nxlebot</div>
<div class="status"><span class="dot"></span>Online - Sync Telegram</div>
</div>
</div>
<div class="chat" id="chat">
<div class="welcome" id="welcome">
<div class="emoji">👋</div>
<div style="font-size:1.5rem;font-weight:700;margin-bottom:10px">Selamat Datang!</div>
<div style="color:#94a3b8;max-width:400px;line-height:1.6">Chat terintegrasi Telegram. Pindah platform tanpa kehilangan history!</div>
<div class="badge">🔄 Sync Active</div>
</div>
</div>
<div class="typing" id="typing" style="display:none;margin-left:48px">
<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
</div>
<div class="input">
<div class="input-wrap">
<div class="input-box"><textarea id="msg" placeholder="Ketik pesan..." rows="1"></textarea></div>
<button id="send" onclick="send()">➤</button>
</div>
</div>
<script>
const chat=document.getElementById('chat'),msg=document.getElementById('msg'),sendBtn=document.getElementById('send'),typing=document.getElementById('typing'),welcome=document.getElementById('welcome');
let first=true;
msg.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,150)+'px';sendBtn.disabled=!this.value.trim()});
msg.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
async function load(){try{const r=await fetch('/api/history'),d=await r.json();if(d.messages&&d.messages.length>0){welcome.remove();first=false;d.messages.forEach(m=>add(m.text,!m.is_user,m.time))}}catch(e){}}
function add(text,bot=false,time=null){if(welcome.parentNode&&first){welcome.remove();first=false}const div=document.createElement('div');div.className='msg'+(bot?'':' user');div.innerHTML='<div class="avatar">'+(bot?'🤖':'👤')+'</div><div><div class="content">'+text+'</div><div class="time">'+(time||new Date().toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}))+'</div></div>';chat.appendChild(div);chat.scrollTop=chat.scrollHeight}
async function send(){const text=msg.value.trim();if(!text)return;add(text,false);msg.value='';msg.style.height='auto';sendBtn.disabled=true;typing.style.display='flex';chat.appendChild(typing);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})}),d=await r.json();typing.style.display='none';if(d.response)add(d.response,true,d.time)}catch(e){typing.style.display='none';add('⚠️ Error',true)}}
load();msg.focus();sendBtn.disabled=true;
setInterval(load,10000);
</script>
</body>
</html>'''

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path.startswith('/api/history'):
            self.send_json({"success": True, "messages": chat_history[-50:], "count": len(chat_history)})
        elif self.path.startswith('/api/stats'):
            self.send_json({"total": len(chat_history), "user": len([m for m in chat_history if m.get('is_user')]), "bot": len([m for m in chat_history if not m.get('is_user')])})
        else:
            self.send_error(404)
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
        
        if self.path == '/api/chat':
            text = data.get('message', '')
            if text:
                chat_history.append({"id": str(uuid.uuid4()), "text": text, "is_user": True, "platform": "web", "time": datetime.now().isoformat()})
                resp = get_response(text)
                chat_history.append({"id": str(uuid.uuid4()), "text": resp, "is_user": False, "platform": "web", "time": datetime.now().isoformat()})
                save_chat()
                self.send_json({"success": True, "response": resp, "time": datetime.now().isoformat()})
            else:
                self.send_error(400)
        elif self.path == '/api/telegram/message':
            text = data.get('message', '')
            if text:
                chat_history.append({"id": str(uuid.uuid4()), "text": text, "is_user": True, "platform": "telegram", "time": datetime.now().isoformat()})
                resp = get_response(text)
                chat_history.append({"id": str(uuid.uuid4()), "text": resp, "is_user": False, "platform": "telegram", "time": datetime.now().isoformat()})
                save_chat()
                self.send_json({"success": True, "response": resp})
            else:
                self.send_error(400)
        elif self.path == '/api/sync':
            msgs = data.get('messages', [])
            for m in msgs:
                if not any(x.get('id') == m.get('id') for x in chat_history):
                    chat_history.append(m)
            save_chat()
            self.send_json({"success": True, "synced": len(msgs)})
        elif self.path == '/api/clear':
            chat_history.clear()
            save_chat()
            self.send_json({"success": True})
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__ == '__main__':
    print("="*50)
    print("🚀 Nxlebot Simple Chat Server")
    print("="*50)
    print(f"📍 URL: http://localhost:{PORT}")
    print(f"📍 API: http://localhost:{PORT}/api/chat")
    print("="*50)
    load_chat()
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Server RUNNING!")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopped")
