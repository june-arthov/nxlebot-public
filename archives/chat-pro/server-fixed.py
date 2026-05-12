#!/usr/bin/env python3
"""
Nxlebot Pro Chat Server v2 - FIXED JavaScript
"""

import http.server
import socketserver
import json
import os
from datetime import datetime
import uuid

PORT = 8086
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
    try:
        with open(CHAT_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Save error: {e}")

def get_response(msg):
    import re
    msg_lower = msg.lower()
    
    # Greetings
    if any(w in msg_lower for w in ['halo', 'hai', 'hi', 'assalamualaikum', 'selamat pagi', 'selamat siang', 'selamat malam']):
        return "Halo bro! 👋 Ada yang bisa gua bantu hari ini?"
    
    # How are you
    if 'apa kabar' in msg_lower or 'gimana kabar' in msg_lower:
        return "Gua baik bro! 💪 Siap bantu lu 24/7! Lu gimana?"
    
    # Thanks
    if any(w in msg_lower for w in ['makasih', 'terima kasih', 'thanks', 'thank you', 'trims']):
        return "Santai bro! 🫡 Siempre siap bantu lu kapan aja!"
    
    # Goodbye
    if any(w in msg_lower for w in ['bye', 'dadah', 'see you', 'sampai jumpa', 'goodbye']):
        return "See you bro! 👋 Take care and happy hunting! 🎯"
    
    # Bug Bounty
    if 'bug bounty' in msg_lower:
        return "Bug bounty topik favorit gua! 🐛💰 Mau hunt target apa hari ini? Gua bisa bantu reconnaissance, vulnerability analysis, atau report writing!"
    
    # Coding/Programming
    if any(w in msg_lower for w in ['coding', 'code', 'program', 'programming', 'develop']):
        return "Coding time! 💻 Mau build apa hari ini? Web app, mobile app, atau automation tool?"
    
    # Telegram/Sync
    if 'telegram' in msg_lower or 'sync' in msg_lower:
        return "Chat kita sync dengan Telegram! 🔄 Bisa pindah platform tanpa kehilangan history. Keren kan? 😎"
    
    # UI/Design
    if any(w in msg_lower for w in ['ui', 'tampilan', 'design', 'interface']):
        return "Gimana UI baru-nya? Lebih oke kan? 😎 Gua bikin professional dan user-friendly!"
    
    # Trading
    if any(w in msg_lower for w in ['trading', 'crypto', 'bitcoin', 'forex', 'saham']):
        return "Trading topic! 📊 Gua bisa bantu analisis market, tapi ingat: DYOR (Do Your Own Research)! Never invest more than you can lose! 💰"
    
    # Security/Hacking
    if any(w in msg_lower for w in ['hack', 'security', 'vulnerability', 'exploit', 'pentest']):
        return "Security first! 🔒 Remember: Always hack ethically and legally. Bug bounty is the way! 💰"
    
    # AI/Tech
    if any(w in msg_lower for w in ['ai', 'artificial intelligence', 'machine learning', 'tech']):
        return "AI is the future! 🤖 Gua sendiri AI assistant yang terus belajar. Ada yang mau lu tanyain tentang AI?"
    
    # Help
    if any(w in msg_lower for w in ['help', 'bantu', 'help me']):
        return "Gua di sini buat bantu! 🫡 Bisa bantu bug bounty hunting, coding, research, trading analysis, atau sekadar ngobrol. Mau apa?"
    
    # Joke/Fun
    if any(w in msg_lower for w in ['joke', 'lucu', 'ketawa', 'funny']):
        return "Kenapa programmer suka gelap? Karena kalau terang, mereka harus nge-debug! 😂💻"
    
    # Default contextual responses
    default_responses = [
        "Menarik! Ceritain lebih lanjut dong. 🤔",
        "Gua ngerti. Ada lagi yang mau dibahas? 💭",
        "Oke bro! Lanjut! 🚀",
        "Siap! Tell me more! 👂",
        "Interesting point! Gua sependapat. 👍",
        "Hmm, let me think about that... 🤔",
        "That's a good point! 💡",
        "Gua catat! Ada lagi? 📝"
    ]
    
    return default_responses[hash(msg) % len(default_responses)]

HTML = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nxlebot Pro</title>
<style>
:root{--primary:#2563eb;--success:#10b981;--bg:#0f172a;--surface:#1e293b;--surface-light:#334155;--text:#f8fafc;--text-muted:#94a3b8;--border:#334155}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
.header{background:var(--surface);padding:16px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.header-left{display:flex;align-items:center;gap:16px}
.logo{width:50px;height:50px;border-radius:14px;background:linear-gradient(135deg,var(--primary),var(--success));display:flex;align-items:center;justify-content:center;font-size:2rem}
.status{display:flex;align-items:center;gap:8px;font-size:0.85rem;color:var(--text-muted)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--success);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.btn{padding:10px 18px;border-radius:10px;border:none;cursor:pointer;font-size:0.9rem;font-weight:500;transition:.3s;display:flex;align-items:center;gap:8px}
.btn-primary{background:linear-gradient(135deg,var(--primary),#1d4ed8);color:#fff}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(37,99,235,0.4)}
.btn-secondary{background:var(--surface-light);color:var(--text)}
.chat{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px}
.msg{display:flex;gap:12px;max-width:75%;animation:slide .3s}
@keyframes slide{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.avatar{width:42px;height:42px;border-radius:14px;background:var(--surface-light);display:flex;align-items:center;justify-content:center;font-size:1.5rem}
.msg.user .avatar{background:linear-gradient(135deg,var(--primary),var(--success))}
.content{background:var(--surface);padding:14px 18px;border-radius:16px;line-height:1.6;border:1px solid var(--border)}
.msg.user .content{background:linear-gradient(135deg,var(--primary),#1d4ed8);border:none}
.meta{font-size:.75rem;color:var(--text-muted);margin-top:5px;text-align:right}
.typing{display:flex;gap:6px;padding:16px 20px;background:var(--surface);border-radius:16px;width:fit-content;margin-left:54px}
.td{width:8px;height:8px;border-radius:50%;background:var(--text-muted);animation:typing 1.4s infinite}
.td:nth-child(2){animation-delay:.2s}.td:nth-child(3){animation-delay:.4s}
@keyframes typing{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
.input{background:var(--surface);border-top:1px solid var(--border);padding:20px 24px}
.input-wrap{max-width:1000px;margin:0 auto;display:flex;gap:12px}
.ibox{flex:1;background:var(--surface-light);border-radius:16px;border:2px solid transparent;transition:.3s}
.ibox:focus-within{border-color:var(--primary)}
#msg{width:100%;background:0 0;border:0;padding:16px 20px;color:var(--text);font-size:1rem;outline:0;resize:none;min-height:56px}
#send{background:linear-gradient(135deg,var(--primary),var(--success));color:#fff;border:0;border-radius:14px;width:58px;height:58px;cursor:pointer;font-size:1.5rem;transition:.3s}
#send:hover{transform:translateY(-2px) scale(1.05)}
.welcome{text-align:center;padding:60px 20px}
.emoji{font-size:5rem;margin-bottom:24px;animation:float 3s infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.welcome h2{font-size:1.8rem;margin-bottom:12px}
.welcome p{color:var(--text-muted);max-width:500px;line-height:1.6;margin:0 auto 24px}
.badge{background:var(--success);color:#fff;padding:6px 14px;border-radius:20px;font-size:.8rem;font-weight:600}
.panel{position:fixed;top:70px;right:-320px;width:320px;height:calc(100vh - 70px);background:var(--surface);border-left:1px solid var(--border);padding:24px;transition:.3s;z-index:100}
.panel.open{right:0}
.ph{display:flex;justify-content:space-between;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.ph h3{font-size:1.1rem}
.cls{background:0 0;border:0;color:var(--text-muted);cursor:pointer;font-size:1.5rem}
.stat{background:var(--surface-light);padding:16px;border-radius:10px;margin-bottom:12px}
.stat-l{font-size:.85rem;color:var(--text-muted);margin-bottom:6px}
.stat-v{font-size:1.5rem;font-weight:700}
.overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);opacity:0;visibility:hidden;transition:.3s;z-index:50}
.overlay.active{opacity:1;visibility:visible}
</style>
</head>
<body>
<header class="header">
<div class="header-left">
<div class="logo">🤖</div>
<div><div style="font-weight:600">Nxlebot Pro</div><div class="status"><span class="dot"></span>Online</div></div>
</div>
<div style="display:flex;gap:10px">
<button class="btn btn-secondary" onclick="togglePanel()">🔄 Sync</button>
<button class="btn btn-secondary" onclick="doClear()">🗑️</button>
</div>
</header>
<main class="chat" id="chat"><div class="welcome" id="welcome"><div class="emoji">👋</div><h2>Selamat Datang!</h2><p>Chat terintegrasi Telegram</p><div class="badge">🔄 Auto-Sync</div></div></main>
<div class="typing" id="typing" style="display:none"><div class="td"></div><div class="td"></div><div class="td"></div></div>
<footer class="input"><div class="input-wrap"><div class="ibox"><textarea id="msg" placeholder="Ketik pesan..." rows="1"></textarea></div><button id="send" onclick="doSend()">➤</button></div></footer>
<aside class="panel" id="panel"><div class="ph"><h3>🔄 Status</h3><button class="cls" onclick="togglePanel()">×</button></div><div class="stat"><div class="stat-l">Total</div><div class="stat-v" id="st0">0</div></div><div class="stat"><div class="stat-l">Web</div><div class="stat-v" id="st1">0</div></div><div class="stat"><div class="stat-l">Telegram</div><div class="stat-v" id="st2">0</div></div><button class="btn btn-primary" onclick="doSync()" style="width:100%;margin-top:16px">Sync Now</button></aside>
<div class="overlay" id="ov" onclick="togglePanel()"></div>
<script>
const $=id=>document.getElementById(id);
const chat=$('chat'),msg=$('msg'),send=$('send'),typing=$('typing'),welcome=$('welcome'),panel=$('panel'),ov=$('ov');
let first=true;

msg.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,150)+'px';send.disabled=!this.value.trim()});

msg.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();doSend()}});

async function load(){try{const r=await fetch('/api/history'),d=await r.json();if(d.messages&&d.messages.length>0){if(welcome.parentNode)welcome.remove();first=false;d.messages.forEach(m=>add(m.text,!m.is_user,m.time));upd()}}catch(e){}}

function add(text,bot=false,time=null){
if(welcome.parentNode&&first){welcome.remove();first=false}
const div=document.createElement('div');
div.className='msg'+(bot?'':' user');
div.innerHTML='<div class="avatar">'+(bot?'🤖':'👤')+'</div><div><div class="content">'+text.replace(/\\n/g,'<br>')+'</div><div class="meta">'+(time?new Date(time).toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}):new Date().toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}))+'</div></div>';
chat.appendChild(div);
chat.scrollTop=chat.scrollHeight;
}

async function doSend(){
const text=msg.value.trim();
if(!text)return;
add(text,false);
msg.value='';
msg.style.height='auto';
send.disabled=true;
typing.style.display='flex';
chat.appendChild(typing);
chat.scrollTop=chat.scrollHeight;
try{
const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
const d=await r.json();
typing.style.display='none';
if(d.response)add(d.response,true,d.time);
upd();
}catch(e){typing.style.display='none';add('⚠️ Error',true);}
}

function togglePanel(){panel.classList.toggle('open');ov.classList.toggle('active');if(panel.classList.contains('open'))loadStats();}

async function loadStats(){try{const r=await fetch('/api/stats'),d=await r.json();$('st0').textContent=d.total||0;$('st1').textContent=d.web||0;$('st2').textContent=d.tg||0;}catch(e){}}

function upd(){loadStats();}

async function doSync(){try{const r=await fetch('/api/sync',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:[]})});const d=await r.json();alert('✅ Synced: '+(d.synced||0));load();}catch(e){alert('Error: '+e.message);}}

async function doClear(){if(confirm('Clear all?')){try{await fetch('/api/clear',{method:'POST'});chat.innerHTML='';chat.appendChild(welcome);welcome.style.display='block';first=true;loadStats();}catch(e){alert('Error');}}}

load();
msg.focus();
send.disabled=true;
setInterval(load,10000);
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
            web=len([m for m in chat_history if m.get('platform')=='web'])
            tg=len([m for m in chat_history if m.get('platform')=='telegram'])
            self.send_json({"success": True, "total": len(chat_history), "web": web, "tg": tg})
        else:
            self.send_error(404)
    
    def do_POST(self):
        length=int(self.headers.get('Content-Length',0))
        data=json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
        if self.path=='/api/chat':
            text=data.get('message','')
            if text:
                chat_history.append({"id":str(uuid.uuid4()),"text":text,"is_user":True,"platform":"web","time":datetime.now().isoformat()})
                resp=get_response(text)
                chat_history.append({"id":str(uuid.uuid4()),"text":resp,"is_user":False,"platform":"web","time":datetime.now().isoformat()})
                save_chat()
                self.send_json({"success":True,"response":resp,"time":datetime.now().isoformat()})
            else:self.send_error(400)
        elif self.path=='/api/telegram/message':
            text=data.get('message','')
            if text:
                chat_history.append({"id":str(uuid.uuid4()),"text":text,"is_user":True,"platform":"telegram","time":datetime.now().isoformat()})
                resp=get_response(text)
                chat_history.append({"id":str(uuid.uuid4()),"text":resp,"is_user":False,"platform":"telegram","time":datetime.now().isoformat()})
                save_chat()
                print(f"📨 Telegram: {text[:50]}")
                self.send_json({"success":True,"response":resp,"saved":True})
            else:self.send_error(400)
        elif self.path=='/api/sync':
            msgs=data.get('messages',[])
            synced=sum(1 for m in msgs if not any(x.get('id')==m.get('id') for x in chat_history))
            chat_history.extend([m for m in msgs if not any(x.get('id')==m.get('id') for x in chat_history)])
            save_chat()
            self.send_json({"success":True,"synced":synced})
        elif self.path=='/api/clear':
            chat_history.clear()
            save_chat()
            self.send_json({"success":True})
        else:self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
    
    def send_json(self,data):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps(data,ensure_ascii=False).encode('utf-8'))
    
    def log_message(self,fmt,*args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__=='__main__':
    print("="*50)
    print("🚀 Nxlebot Pro v2 - FIXED")
    print(f"🌐 http://localhost:{PORT}")
    print("="*50)
    load_chat()
    with socketserver.TCPServer(("",PORT),Handler) as httpd:
        print("✅ Server RUNNING!")
        try:httpd.serve_forever()
        except KeyboardInterrupt:print("\n👋 Stopped")
