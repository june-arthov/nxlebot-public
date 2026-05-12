#!/usr/bin/env python3
"""
Nxlebot Pro v4 - FIXED Layout & UI
"""

import http.server
import socketserver
import json
import os
from datetime import datetime
import uuid

PORT = 8088
CHAT_FILE = os.path.join(os.path.dirname(__file__), 'chat_history_final.json')
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
    try:
        with open(CHAT_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Save error: {e}")

def get_response(msg):
    msg_lower = msg.lower()
    if any(w in msg_lower for w in ['halo', 'hai', 'hi']): return "Halo bro! 👋"
    if 'apa kabar' in msg_lower: return "Gua baik bro! 🚀"
    if any(w in msg_lower for w in ['makasih', 'thanks']): return "Santai bro! 🫡"
    if 'bug bounty' in msg_lower: return "Bug bounty topik favorit! 🐛💰"
    if any(w in msg_lower for w in ['coding', 'code']): return "Coding time! 💻"
    return ["Menarik!", "Oke bro!", "Siap!", "Tell me more!"][hash(msg) % 4]

HTML = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nxlebot Chat</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#f8fafc;height:100vh;display:flex;flex-direction:column}
.header{background:#1e293b;padding:16px 24px;border-bottom:1px solid #334155;display:flex;align-items:center;gap:16px}
.logo{width:45px;height:45px;border-radius:12px;background:linear-gradient(135deg,#2563eb,#10b981);display:flex;align-items:center;justify-content:center;font-size:1.8rem}
.status{display:flex;align-items:center;gap:8px;font-size:0.85rem;color:#94a3b8}
.dot{width:8px;height:8px;border-radius:50%;background:#10b981;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.message{display:flex;gap:12px;max-width:70%;animation:slide .3s ease}
@keyframes slide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.message.user{align-self:flex-end;flex-direction:row-reverse}
.avatar{width:40px;height:40px;border-radius:12px;background:#334155;display:flex;align-items:center;justify-content:center;font-size:1.4rem;flex-shrink:0}
.message.user .avatar{background:linear-gradient(135deg,#2563eb,#10b981)}
.content{background:#1e293b;padding:12px 16px;border-radius:16px;line-height:1.5;border:1px solid #334155}
.message.user .content{background:linear-gradient(135deg,#2563eb,#1d4ed8);border:none}
.time{font-size:.75rem;color:#94a3b8;margin-top:6px;text-align:right}
.typing{display:flex;gap:6px;padding:12px 16px;background:#1e293b;border-radius:16px;width:fit-content;margin-left:52px}
.td{width:8px;height:8px;border-radius:50%;background:#94a3b8;animation:typing 1.4s infinite}
.td:nth-child(2){animation-delay:.2s}.td:nth-child(3){animation-delay:.4s}
@keyframes typing{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
.input-area{background:#1e293b;border-top:1px solid #334155;padding:20px}
.input-wrapper{max-width:900px;margin:0 auto;display:flex;gap:12px}
.input-box{flex:1;background:#334155;border-radius:14px;border:2px solid transparent;transition:.3s}
.input-box:focus-within{border-color:#2563eb}
#msg{width:100%;background:0 0;border:0;padding:14px 18px;color:#f8fafc;font-size:1rem;outline:0;resize:none;min-height:52px;max-height:150px}
#send{background:linear-gradient(135deg,#2563eb,#10b981);color:#fff;border:0;border-radius:14px;width:54px;height:54px;cursor:pointer;font-size:1.4rem;transition:.3s;flex-shrink:0}
#send:hover{transform:translateY(-2px) scale(1.05)}
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;padding:40px}
.emoji{font-size:5rem;margin-bottom:24px;animation:float 3s infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.welcome h2{font-size:1.8rem;margin-bottom:12px}
.welcome p{color:#94a3b8;max-width:500px;line-height:1.6}
.badge{background:#10b981;color:#fff;padding:6px 14px;border-radius:20px;font-size:.8rem;font-weight:600;margin-top:16px;display:inline-block}
</style>
</head>
<body>
<div class="header">
<div class="logo">🤖</div>
<div><div style="font-weight:600">Nxlebot</div><div class="status"><span class="dot"></span>Online</div></div>
</div>
<div class="chat" id="chat">
<div class="welcome" id="welcome">
<div class="emoji">👋</div>
<h2>Selamat Datang!</h2>
<p>Chat dengan Nxlebot - AI Assistant lu</p>
<div class="badge">✨ Ready</div>
</div>
</div>
<div class="typing" id="typing" style="display:none"><div class="td"></div><div class="td"></div><div class="td"></div></div>
<div class="input-area">
<div class="input-wrapper">
<div class="input-box"><textarea id="msg" placeholder="Ketik pesan..." rows="1"></textarea></div>
<button id="send" onclick="send()">➤</button>
</div>
</div>
<script>
const chat=document.getElementById('chat');
const msg=document.getElementById('msg');
const sendBtn=document.getElementById('send');
const typing=document.getElementById('typing');
const welcome=document.getElementById('welcome');
let first=true;

msg.addEventListener('input',function(){
this.style.height='auto';
this.style.height=Math.min(this.scrollHeight,150)+'px';
sendBtn.disabled=!this.value.trim();
});

msg.addEventListener('keydown',function(e){
if(e.key==='Enter'&&!e.shiftKey){
e.preventDefault();
send();
}
});

async function loadHistory(){
try{
const r=await fetch('/api/history');
const d=await r.json();
if(d.messages&&d.messages.length>0){
if(welcome.parentNode){
welcome.remove();
}
first=false;
d.messages.forEach(function(m){
addMessage(m.text,!m.is_user,m.time);
});
}
}catch(e){
console.log('Load error:',e);
}
}

function addMessage(text,isBot,time){
if(welcome.parentNode&&first){
welcome.remove();
first=false;
}
const msgDiv=document.createElement('div');
msgDiv.className='message'+(isBot?'':' user');
const avatar=document.createElement('div');
avatar.className='avatar';
avatar.textContent=isBot?'🤖':'👤';
const contentDiv=document.createElement('div');
contentDiv.className='content';
contentDiv.textContent=text;
const timeDiv=document.createElement('div');
timeDiv.className='time';
timeDiv.textContent=time?new Date(time).toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}):new Date().toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'});
contentDiv.appendChild(timeDiv);
msgDiv.appendChild(avatar);
msgDiv.appendChild(contentDiv);
chat.appendChild(msgDiv);
chat.scrollTop=chat.scrollHeight;
}

async function send(){
const text=msg.value.trim();
if(!text)return;
addMessage(text,false,null);
msg.value='';
msg.style.height='auto';
sendBtn.disabled=true;
typing.style.display='flex';
chat.appendChild(typing);
chat.scrollTop=chat.scrollHeight;
try{
const r=await fetch('/api/chat',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({message:text})
});
const d=await r.json();
typing.style.display='none';
if(d.response){
addMessage(d.response,true,d.time);
}
}catch(e){
typing.style.display='none';
addMessage('⚠️ Error',true);
}
}

loadHistory();
msg.focus();
sendBtn.disabled=true;
setInterval(loadHistory,10000);
</script>
</body>
</html>'''

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path.startswith('/api/history'):
            self.send_json({"success": True, "messages": chat_history[-100:], "count": len(chat_history)})
        elif self.path.startswith('/api/stats'):
            self.send_json({"success": True, "total": len(chat_history)})
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
                print(f"📨 Telegram: {text[:50]}")
                self.send_json({"success": True, "response": resp, "saved": True})
            else:
                self.send_error(400)
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
    print("🚀 Nxlebot Pro v4 - FIXED Layout")
    print(f"🌐 http://localhost:{PORT}")
    print("="*50)
    load_chat()
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("✅ Server RUNNING!")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopped")
