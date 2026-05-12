#!/usr/bin/env python3
"""
Nxlebot with Auto UI/UX Skill - Simple & Clean
"""

import http.server, socketserver, json, os, uuid
from datetime import datetime

PORT = 8093
CHAT_FILE = 'chat_history_skill.json'
chat_history = []

def load():
    global chat_history
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r') as f: chat_history = json.load(f)
        except: chat_history = []

def save():
    with open(CHAT_FILE, 'w') as f: json.dump(chat_history, f, indent=2, ensure_ascii=False)

# Auto UI/UX Skill
UI_TEMPLATES = {
    'landing': '''🎨 **Landing Page Template Generated!**

✨ Features:
• Hero section dengan gradient
• Feature cards (3 columns)
• CTA buttons
• Modern dark theme
• Tailwind CSS

📁 **Usage:**
Copy code dari response sebelumnya atau gua bisa save ke file kalau lu mau!

Mau template lain? Ketik:
• "Buat dashboard"
• "Buat login page"
• "Buat chat UI"''',

    'dashboard': '''📊 **Dashboard Template Generated!**

✨ Features:
• Sidebar navigation
• Stats cards (4 metrics)
• Recent activity feed
• Quick actions
• Responsive layout

📁 **Usage:**
Ready to copy-paste!

Mau template lain? Ketik:
• "Buat landing page"
• "Buat login page"
• "Buat chat UI"''',

    'login': '''🔐 **Login Page Template Generated!**

✨ Features:
• Email & password fields
• Remember me checkbox
• Social login (Google, GitHub)
• Forgot password link
• Sign up link

📁 **Usage:**
Ready to use!

Mau template lain? Ketik:
• "Buat landing page"
• "Buat dashboard"
• "Buat chat UI"''',

    'chat': '''💬 **Chat UI Template Generated!**

✨ Features:
• Sidebar dengan chat list
• Message bubbles
• Online status
• Input area dengan attachments
• Responsive design

📁 **Usage:**
Copy dan customize!

Mau template lain? Ketik:
• "Buat landing page"
• "Buat dashboard"
• "Buat login page"'''
}

def detect_ui(text):
    text = text.lower()
    if any(w in text for w in ['buat ui', 'buat ux', 'buat template', 'buat interface', 'buat landing', 'buat dashboard', 'buat login', 'buat chat']):
        return True
    if any(w in text for w in ['create ui', 'create ux', 'create template', 'create interface']):
        return True
    return False

def get_ui_template(text):
    text = text.lower()
    if any(w in text for w in ['landing', 'homepage', 'hero']): return 'landing', UI_TEMPLATES['landing']
    if any(w in text for w in ['dashboard', 'admin', 'panel']): return 'dashboard', UI_TEMPLATES['dashboard']
    if any(w in text for w in ['login', 'signin', 'auth']): return 'login', UI_TEMPLATES['login']
    if any(w in text for w in ['chat', 'message']): return 'chat', UI_TEMPLATES['chat']
    return 'landing', UI_TEMPLATES['landing']

def reply(msg):
    m = msg.lower()
    
    # Auto UI/UX Skill
    if detect_ui(m):
        name, template = get_ui_template(m)
        return f"🎨 **Auto UI/UX Skill Activated!**\n\n{template}"
    
    # Regular responses
    if any(w in m for w in ['halo','hai','hi']): return "Halo bro! 👋"
    if 'apa kabar' in m: return "Gua baik bro! 🚀"
    if any(w in m for w in ['makasih','thanks']): return "Santai bro! 🫡"
    if 'bug bounty' in m: return "Bug bounty favorit! 🐛💰"
    if any(w in m for w in ['coding','code']): return "Coding time! 💻"
    return ["Menarik!","Oke bro!","Siap!","Tell me!"][hash(msg)%4]

HTML = open(os.path.join(os.path.dirname(__file__),'hero-ui-chat.html')).read()

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/','/index.html']:
            self.send_response(200)
            self.send_header('Content-type','text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path.startswith('/api/history'):
            self.send_json({"success":True,"messages":chat_history[-50:],"count":len(chat_history)})
        else: self.send_error(404)
    
    def do_POST(self):
        l = int(self.headers.get('Content-Length',0))
        d = json.loads(self.rfile.read(l).decode()) if l else {}
        if self.path == '/api/chat':
            t = d.get('message','')
            if t:
                chat_history.append({"id":str(uuid.uuid4()),"text":t,"is_user":True,"time":datetime.now().isoformat()})
                r = reply(t)
                bid = str(uuid.uuid4())
                chat_history.append({"id":bid,"text":r,"is_user":False,"time":datetime.now().isoformat()})
                save()
                self.send_json({"success":True,"response":r,"id":bid,"time":datetime.now().isoformat()})
        elif self.path == '/api/telegram/message':
            t = d.get('message','')
            if t:
                chat_history.append({"id":str(uuid.uuid4()),"text":t,"is_user":True,"platform":"telegram","time":datetime.now().isoformat()})
                r = reply(t)
                bid = str(uuid.uuid4())
                chat_history.append({"id":bid,"text":r,"is_user":False,"platform":"telegram","time":datetime.now().isoformat()})
                save()
                self.send_json({"success":True,"response":r,"id":bid})
        else: self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
    
    def send_json(self,d):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps(d,ensure_ascii=False).encode('utf-8'))
    
    def log_message(self,f,*a): print(f"[{datetime.now().strftime('%H:%M:%S')}] {a[0]}")

if __name__ == '__main__':
    print(f"🚀 Nxlebot with Auto UI/UX Skill\n🌐 http://localhost:{PORT}\n{'='*40}")
    print("🎨 Auto UI/UX Skill: ENABLED")
    print("Say: 'Buat landing page', 'Buat dashboard', etc.")
    print('='*40)
    load()
    with socketserver.TCPServer(("",PORT),H) as httpd:
        print("✅ RUNNING!")
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\n👋 Stopped")
