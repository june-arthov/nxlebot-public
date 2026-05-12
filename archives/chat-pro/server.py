#!/usr/bin/env python3
"""
Nxlebot Pro Chat Server - Telegram Sync + Beautiful UI
All features in one server!
"""

import http.server
import socketserver
import json
import os
from datetime import datetime
import uuid

PORT = 8085
CHAT_FILE = os.path.join(os.path.dirname(__file__), 'chat_history.json')

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
    if any(w in msg for w in ['halo', 'hai', 'hi', 'assalam']): return "Halo bro! 👋 Ada yang bisa gua bantu?"
    if 'apa kabar' in msg: return "Gua baik bro! Siap bantu lu! 🚀"
    if any(w in msg for w in ['makasih', 'terima kasih', 'thanks']): return "Santai bro! Siempre siap! 🫡"
    if any(w in msg for w in ['bye', 'dadah', 'see you']): return "See you bro! Take care! 👋"
    if 'bug bounty' in msg: return "Bug bounty favorit gua! 🐛💰 Mau hunt target apa?"
    if any(w in msg for w in ['coding', 'code', 'program']): return "Coding time! 💻 Build apa hari ini?"
    if 'telegram' in msg: return "Chat kita sync dengan Telegram! Bisa pindah platform tanpa kehilangan history! 🎉"
    if 'sync' in msg: return "Sync aktif bro! Setiap 10 detik auto-refresh! 🔄"
    if 'ui' in msg or 'tampilan' in msg: return "Gimana UI baru-nya? Lebih oke kan? 😎"
    return ["Menarik! Ceritain lebih lanjut.", "Gua ngerti. Ada lagi?", "Oke bro! Lanjut!", "Siap! Tell me more!", "Interesting! Go on..."][hash(msg) % 5]

HTML = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nxlebot Pro - Chat Sync</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--primary:#2563eb;--primary-dark:#1d4ed8;--success:#10b981;--warning:#f59e0b;--danger:#ef4444;--bg:#0f172a;--surface:#1e293b;--surface-light:#334155;--text:#f8fafc;--text-muted:#94a3b8;--border:#334155}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
.header{background:var(--surface);padding:16px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.header-left{display:flex;align-items:center;gap:16px}
.logo{width:50px;height:50px;border-radius:14px;background:linear-gradient(135deg,var(--primary),var(--success));display:flex;align-items:center;justify-content:center;font-size:2rem;box-shadow:0 4px 12px rgba(37,99,235,0.3)}
.bot-info h1{font-size:1.2rem;font-weight:600;margin-bottom:4px;background:linear-gradient(135deg,var(--text),var(--text-muted));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.status{display:flex;align-items:center;gap:8px;font-size:0.85rem;color:var(--text-muted)}
.status-dot{width:8px;height:8px;border-radius:50%;background:var(--success);animation:pulse 2s infinite;box-shadow:0 0 8px var(--success)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.header-actions{display:flex;gap:10px}
.btn{padding:10px 18px;border-radius:10px;border:none;cursor:pointer;font-size:0.9rem;font-weight:500;transition:all .3s;display:flex;align-items:center;gap:8px}
.btn-primary{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(37,99,235,0.4)}
.btn-secondary{background:var(--surface-light);color:var(--text)}
.btn-secondary:hover{background:var(--primary);color:#fff}
.chat{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px}
.msg{display:flex;gap:12px;max-width:75%;animation:slide .3s ease}
@keyframes slide{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.avatar{width:42px;height:42px;border-radius:14px;background:var(--surface-light);display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0;box-shadow:0 2px 8px rgba(0,0,0,0.3)}
.msg.user .avatar{background:linear-gradient(135deg,var(--primary),var(--success))}
.msg-wrapper{display:flex;flex-direction:column;gap:6px;max-width:100%}
.msg.user .msg-wrapper{align-items:flex-end}
.content{background:var(--surface);padding:14px 18px;border-radius:16px;line-height:1.6;font-size:0.95rem;box-shadow:0 2px 8px rgba(0,0,0,0.2);border:1px solid var(--border)}
.msg.user .content{background:linear-gradient(135deg,var(--primary),var(--primary-dark));border:none;color:var(--text)}
.content pre{background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;overflow-x:auto;margin:8px 0;font-family:'JetBrains Mono',monospace;font-size:0.85rem}
.content code{background:rgba(0,0,0,0.2);padding:2px 6px;border-radius:4px;font-family:'JetBrains Mono',monospace}
.content strong{color:var(--success);font-weight:600}
.meta{display:flex;align-items:center;gap:8px;font-size:0.75rem;color:var(--text-muted)}
.typing{display:flex;gap:12px;margin-left:54px;animation:slide .3s}
.typing-bubble{background:var(--surface);padding:16px 20px;border-radius:16px;display:flex;gap:6px;border:1px solid var(--border)}
.typing-dot{width:8px;height:8px;border-radius:50%;background:var(--text-muted);animation:typing 1.4s infinite}
.typing-dot:nth-child(2){animation-delay:.2s}.typing-dot:nth-child(3){animation-delay:.4s}
@keyframes typing{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
.input{background:var(--surface);border-top:1px solid var(--border);padding:20px 24px}
.input-wrap{max-width:1000px;margin:0 auto;display:flex;gap:12px;align-items:flex-end}
.input-box{flex:1;background:var(--surface-light);border-radius:16px;border:2px solid transparent;transition:.3s}
.input-box:focus-within{border-color:var(--primary);box-shadow:0 0 0 4px rgba(37,99,235,0.1)}
#msg{width:100%;background:0 0;border:0;padding:16px 20px;color:var(--text);font-size:1rem;font-family:inherit;outline:0;resize:none;max-height:150px;min-height:56px;line-height:1.5}
#send{background:linear-gradient(135deg,var(--primary),var(--success));color:#fff;border:0;border-radius:14px;width:58px;height:58px;cursor:pointer;font-size:1.5rem;transition:all .3s;flex-shrink:0;box-shadow:0 4px 12px rgba(37,99,235,0.3)}
#send:hover:not(:disabled){transform:translateY(-2px) scale(1.05);box-shadow:0 6px 20px rgba(37,99,235,0.5)}
#send:disabled{opacity:.5;cursor:not-allowed}
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;padding:40px}
.emoji{font-size:5rem;margin-bottom:24px;animation:float 3s infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.welcome h2{font-size:1.8rem;font-weight:700;margin-bottom:12px;background:linear-gradient(135deg,var(--text),var(--primary));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome p{color:var(--text-muted);font-size:1.05rem;max-width:500px;line-height:1.6;margin-bottom:24px}
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;max-width:800px;margin-top:32px}
.feature{background:var(--surface);padding:20px;border-radius:12px;border:1px solid var(--border);text-align:left}
.feature-icon{font-size:2rem;margin-bottom:12px}
.feature-title{font-weight:600;margin-bottom:8px;color:var(--text)}
.feature-desc{font-size:0.85rem;color:var(--text-muted);line-height:1.5}
.badge{background:var(--success);color:#fff;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;display:inline-block;margin-top:16px}
.sync-panel{position:fixed;top:70px;right:-320px;width:320px;height:calc(100vh - 70px);background:var(--surface);border-left:1px solid var(--border);padding:24px;transition:.3s;z-index:100;overflow-y:auto}
.sync-panel.open{right:0}
.panel-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.panel-header h3{font-size:1.1rem;font-weight:600}
.close-btn{background:0 0;border:0;color:var(--text-muted);cursor:pointer;font-size:1.5rem;transition:.2s}
.close-btn:hover{color:var(--text)}
.stat-card{background:var(--surface-light);padding:16px;border-radius:10px;margin-bottom:12px}
.stat-label{font-size:0.85rem;color:var(--text-muted);margin-bottom:6px}
.stat-value{font-size:1.5rem;font-weight:700;color:var(--text)}
.overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);opacity:0;visibility:hidden;transition:.3s;z-index:50}
.overlay.active{opacity:1;visibility:visible}
@media(max-width:768px){.header{padding:12px 16px}.msg{max-width:90%}.chat{padding:16px}.features{grid-template-columns:1fr}}
</style>
</head>
<body>
<header class="header">
<div class="header-left">
<div class="logo">🤖</div>
<div class="bot-info">
<h1>Nxlebot Pro</h1>
<div class="status"><span class="status-dot"></span>Online - Sync Telegram</div>
</div>
</div>
<div class="header-actions">
<button class="btn btn-secondary" onclick="toggleSync()"><span>🔄</span> Sync</button>
<button class="btn btn-secondary" onclick="clearChat()"><span>🗑️</span> Clear</button>
<button class="btn btn-primary" onclick="window.open('https://telegram.org','_blank')"><span>📱</span> Telegram</button>
</div>
</header>
<main class="chat" id="chat">
<div class="welcome" id="welcome">
<div class="emoji">👋</div>
<h2>Selamat Datang di Nxlebot Pro!</h2>
<p>Asisten AI pribadi dengan sync Telegram real-time. Pindah platform tanpa kehilangan history!</p>
<div class="badge">🔄 Auto-Sync Every 10s</div>
<div class="features">
<div class="feature"><div class="feature-icon">🐛</div><div class="feature-title">Bug Bounty</div><div class="feature-desc">Hunting & security research</div></div>
<div class="feature"><div class="feature-icon">💻</div><div class="feature-title">Coding</div><div class="feature-desc">Code review & debugging</div></div>
<div class="feature"><div class="feature-icon">🔍</div><div class="feature-title">Research</div><div class="feature-desc">Info & data analysis</div></div>
<div class="feature"><div class="feature-icon">💰</div><div class="feature-title">Trading</div><div class="feature-desc">AI trading insights</div></div>
</div>
</div>
</main>
<div class="typing" id="typing" style="display:none">
<div class="avatar">🤖</div>
<div class="typing-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
</div>
<footer class="input">
<div class="input-wrap">
<div class="input-box"><textarea id="msg" placeholder="Ketik pesan Anda..." rows="1"></textarea></div>
<button id="send" onclick="send()">➤</button>
</div>
</footer>
<aside class="sync-panel" id="syncPanel">
<div class="panel-header"><h3>🔄 Sync Status</h3><button class="close-btn" onclick="toggleSync()">×</button></div>
<div class="stat-card"><div class="stat-label">Total Messages</div><div class="stat-value" id="statTotal">0</div></div>
<div class="stat-card"><div class="stat-label">Web Messages</div><div class="stat-value" id="statWeb">0</div></div>
<div class="stat-card"><div class="stat-label">Telegram Messages</div><div class="stat-value" id="statTg">0</div></div>
<div class="stat-card"><div class="stat-label">Last Sync</div><div class="stat-value" id="lastSync" style="font-size:1rem">-</div></div>
<button class="btn btn-primary" onclick="manualSync()" style="width:100%;margin-top:16px"><span>🔄</span> Sync Now</button>
<div style="margin-top:24px;padding:16px;background:var(--surface-light);border-radius:10px;font-size:0.85rem;color:var(--text-muted);line-height:1.6">
<strong>Telegram Integration:</strong><br>
Webhook endpoint ready at:<br>
<code style="background:rgba(0,0,0,0.3);padding:2px 6px;border-radius:4px;display:block;margin:8px 0">/api/telegram/message</code>
Configure in OpenClaw to auto-sync!
</div>
</aside>
<div class="overlay" id="overlay" onclick="toggleSync()"></div>
<script>
const chat=document.getElementById('chat'),msg=document.getElementById('msg'),sendBtn=document.getElementById('send'),typing=document.getElementById('typing'),welcome=document.getElementById('welcome'),syncPanel=document.getElementById('syncPanel'),overlay=document.getElementById('overlay');
let first=true,lastCount=0;
msg.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,150)+'px';sendBtn.disabled=!this.value.trim()});
msg.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();return false}});msg.addEventListener('keypress',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();return false}});
async function load(){try{const r=await fetch('/api/history'),d=await r.json();if(d.messages&&d.messages.length>0){if(welcome.parentNode){welcome.remove()}first=false;d.messages.forEach(m=>add(m.text,!m.is_user,m.time));if(d.messages.length!==lastCount){updateStats(d.messages.length)}}}catch(e){console.log('Load error:',e)}}
function add(text,bot=false,time=null){if(welcome.parentNode&&first){welcome.remove();first=false}const div=document.createElement('div');div.className='msg'+(bot?'':' user');const avatar=document.createElement('div');avatar.className='avatar';avatar.textContent=bot?'🤖':'👤';const wrapper=document.createElement('div');wrapper.className='msg-wrapper';const content=document.createElement('div');content.className='content';content.innerHTML=formatText(text);const meta=document.createElement('div');meta.className='meta';meta.textContent=time?new Date(time).toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}):new Date().toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'});content.appendChild(meta);wrapper.appendChild(content);div.appendChild(avatar);div.appendChild(wrapper);chat.appendChild(div);chat.scrollTop=chat.scrollHeight}
function formatText(t){return t.replace(/\\*\\*(.+?)\\*\\*/g,'<strong>$1</strong>').replace(/`(.+?)`/g,'<code>$1</code>').replace(/\\n/g,'<br>')}
async function send(){const text=msg.value.trim();if(!text)return;add(text,false);msg.value='';msg.style.height='auto';sendBtn.disabled=true;typing.style.display='flex';chat.appendChild(typing);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})}),d=await r.json();typing.style.display='none';if(d.response){add(d.response,true,d.time);updateStats()}}catch(e){typing.style.display='none';add('⚠️ Backend error',true)}}
function toggleSync(){syncPanel.classList.toggle('open');overlay.classList.toggle('active');if(syncPanel.classList.contains('open'))loadStats()}
function overlay.onclick(){toggleSync()}
async function loadStats(){try{const r=await fetch('/api/stats'),d=await r.json();document.getElementById('statTotal').textContent=d.total||0;document.getElementById('statWeb').textContent=d.web||0;document.getElementById('statTg').textContent=d.tg||0;document.getElementById('lastSync').textContent=new Date().toLocaleTimeString('id-ID')}}
function updateStats(total){loadStats()}
async function manualSync(){try{const r=await fetch('/api/sync',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:[]})});const d=await r.json();alert('✅ Sync complete! Synced: '+(d.synced||0));load();loadStats()}catch(e){alert('⚠️ Sync failed: '+e.message)}}
async function clearChat(){if(confirm('Clear all chat history?')){try{await fetch('/api/clear',{method:'POST'});chat.innerHTML='';chat.appendChild(welcome);welcome.style.display='flex';first=true;loadStats()}catch(e){alert('Error: '+e.message)}}}
load();msg.focus();sendBtn.disabled=true;setInterval(load,10000);
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
            self.send_json({"success": True, "messages": chat_history[-100:], "count": len(chat_history)})
        elif self.path.startswith('/api/stats'):
            web = len([m for m in chat_history if m.get('platform') == 'web'])
            tg = len([m for m in chat_history if m.get('platform') == 'telegram'])
            self.send_json({"success": True, "total": len(chat_history), "web": web, "tg": tg})
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
            user_id = data.get('user_id', 'unknown')
            if text:
                chat_history.append({"id": str(uuid.uuid4()), "text": text, "is_user": True, "platform": "telegram", "user_id": user_id, "time": datetime.now().isoformat()})
                resp = get_response(text)
                chat_history.append({"id": str(uuid.uuid4()), "text": resp, "is_user": False, "platform": "telegram", "time": datetime.now().isoformat()})
                save_chat()
                print(f"📨 Telegram message from {user_id}: {text[:50]}...")
                self.send_json({"success": True, "response": resp, "saved": True})
            else:
                self.send_error(400)
        elif self.path == '/api/sync':
            msgs = data.get('messages', [])
            synced = 0
            for m in msgs:
                if not any(x.get('id') == m.get('id') for x in chat_history):
                    chat_history.append(m)
                    synced += 1
            save_chat()
            self.send_json({"success": True, "synced": synced, "total": len(chat_history)})
        elif self.path == '/api/clear':
            chat_history.clear()
            save_chat()
            self.send_json({"success": True, "message": "Cleared"})
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
    print("="*60)
    print("🚀 Nxlebot Pro Chat Server")
    print("="*60)
    print(f"🌐 URL: http://localhost:{PORT}")
    print(f"📡 API: http://localhost:{PORT}/api/chat")
    print(f"🔄 Telegram Webhook: POST /api/telegram/message")
    print("="*60)
    print("Features:")
    print("  ✅ Beautiful UI (Professional)")
    print("  ✅ Telegram Sync Ready")
    print("  ✅ Manual Sync Button")
    print("  ✅ Auto-refresh every 10s")
    print("  ✅ Chat Statistics")
    print("="*60)
    load_chat()
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Server RUNNING on port {PORT}!")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopped")
