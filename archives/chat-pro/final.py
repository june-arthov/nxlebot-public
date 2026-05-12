#!/usr/bin/env python3
"""
Nxlebot FINAL - Clean, Simple, Works!
"""

import http.server, socketserver, json, os, uuid
from datetime import datetime

PORT = 8100
CHAT_FILE = 'chat_final.json'
chat_history = []

def load():
    global chat_history
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r') as f: chat_history = json.load(f)
        except: pass

def save():
    with open(CHAT_FILE, 'w') as f: json.dump(chat_history, f, indent=2, ensure_ascii=False)

def reply(msg):
    m = msg.lower()
    # Auto UI/UX Skill
    if any(w in m for w in ['buat ui', 'buat ux', 'buat template', 'buat landing', 'buat dashboard', 'buat login', 'buat chat']):
        return "🎨 **UI Template Ready!**\n\nGua bisa generate:\n• Landing Page\n• Dashboard\n• Login Page\n• Chat UI\n\nMau yang mana? Ketik lengkap aja!"
    # Regular
    if any(w in m for w in ['halo','hai','hi']): return "Halo bro! 👋"
    if 'apa kabar' in m: return "Gua baik bro! 🚀"
    if any(w in m for w in ['makasih','thanks']): return "Santai bro! 🫡"
    return ["Menarik!","Oke bro!","Siap!","Tell me!"][hash(msg)%4]

HTML = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nxlebot</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
*{font-family:system-ui,sans-serif}
body{background:linear-gradient(135deg,#0f172a,#1e293b)}
.msg{animation:slide .3s}
@keyframes slide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.typing-dot{animation:typing 1.4s infinite}
@keyframes typing{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
</style>
</head>
<body class="h-screen flex flex-col">
<header class="bg-slate-800/80 backdrop-blur border-b border-slate-700 px-6 py-4 flex items-center gap-4">
<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-xl">🤖</div>
<div><div class="font-semibold text-white">Nxlebot</div><div class="text-xs text-slate-400">Online</div></div>
</header>
<main class="flex-1 overflow-y-auto p-4" id="chat"></main>
<footer class="bg-slate-800/80 backdrop-blur border-t border-slate-700 p-4">
<div class="max-w-3xl mx-auto flex gap-3">
<textarea id="msg" rows="1" placeholder="Ketik pesan..." class="flex-1 bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 resize-none" style="min-height:50px"></textarea>
<button id="send" onclick="send()" class="w-12 h-12 bg-gradient-to-br from-blue-500 to-green-500 rounded-xl flex items-center justify-center text-xl text-white hover:shadow-lg hover:shadow-blue-500/30 transition">➤</button>
</div>
</footer>
<script>
const chat=document.getElementById('chat'),msg=document.getElementById('msg'),sendBtn=document.getElementById('send');
let ids=new Set();

msg.addEventListener('input',()=>{msg.style.height='auto';msg.style.height=Math.min(msg.scrollHeight,120)+'px';sendBtn.disabled=!msg.value.trim()});
msg.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});

async function load(){
try{
const r=await fetch('/api/history'),d=await r.json();
if(d.messages&&d.messages.length>0){
chat.innerHTML='';
d.messages.forEach(x=>{if(!ids.has(x.id)){add(x.id,x.text,!x.is_user,x.time);ids.add(x.id)}});
chat.scrollTop=chat.scrollHeight;
}
}catch(e){}
}

function add(id,txt,bot,time){
if(ids.has(id))return;
const d=document.createElement('div');
d.className='msg flex gap-3 max-w-[75%]'+(bot?'':' ml-auto flex-row-reverse');
d.innerHTML='<div class="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-lg flex-shrink-0">'+(bot?'🤖':'👤')+'</div><div class="flex flex-col gap-1 '+(!bot?'items-end':'')+'"><div class="bg-slate-800 border border-slate-700 rounded-2xl px-4 py-3 text-white leading-relaxed">'+txt.replace(/\\n/g,'<br>')+'</div><div class="text-xs text-slate-500">'+(time?new Date(time).toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}):new Date().toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}))+'</div></div>';
chat.appendChild(d);
ids.add(id);
}

async function send(){
const t=msg.value.trim();if(!t)return;
const tid='u'+Date.now();
add(tid,t,false);msg.value='';msg.style.height='auto';sendBtn.disabled=true;
try{
const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
const d=await r.json();
if(d.response)add(d.id||('b'+Date.now()),d.response,true,d.time);
}catch(e){add('e'+Date.now(),'Error',true);}
}

load();msg.focus();sendBtn.disabled=true;
setInterval(load,10000);
</script>
</body>
</html>'''

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/','/index.html']:
            self.send_response(200)
            self.send_header('Content-type','text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path.startswith('/api/history'):
            self.send_json({"success":True,"messages":chat_history[-50:]})
        else: self.send_error(404)
    
    def do_POST(self):
        l=int(self.headers.get('Content-Length',0))
        d=json.loads(self.rfile.read(l).decode()) if l else {}
        if self.path=='/api/chat':
            t=d.get('message','')
            if t:
                chat_history.append({"id":str(uuid.uuid4()),"text":t,"is_user":True,"time":datetime.now().isoformat()})
                r=reply(t)
                bid=str(uuid.uuid4())
                chat_history.append({"id":bid,"text":r,"is_user":False,"time":datetime.now().isoformat()})
                save()
                self.send_json({"success":True,"response":r,"id":bid,"time":datetime.now().isoformat()})
        else: self.send_error(404)
    
    def send_json(self,d):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps(d,ensure_ascii=False).encode('utf-8'))
    
    def log_message(self,f,*a):print(f"[{datetime.now().strftime('%H:%M:%S')}] {a[0]}")

if __name__=='__main__':
    print(f"🚀 Nxlebot FINAL\\n🌐 http://localhost:{PORT}\\n{'='*30}")
    load()
    with socketserver.TCPServer(("",PORT),H) as httpd:
        print("✅ RUNNING!")
        try:httpd.serve_forever()
        except KeyboardInterrupt:print("\\n👋")
