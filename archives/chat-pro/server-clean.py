#!/usr/bin/env python3
"""
Nxlebot Clean Server - Simple & Works + Auto Skills
"""

import http.server, socketserver, json, os, uuid, sys
from datetime import datetime

# Import Auto UI/UX Skill
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills'))
try:
    from auto_ui_ux_skill import execute as ui_skill_execute, detect_ui_command
    UI_SKILL_ENABLED = True
except:
    UI_SKILL_ENABLED = False
    print("⚠️  UI Skill not loaded")

PORT = 8092
CHAT_FILE = 'chat_history.json'
chat_history = []

def load():
    global chat_history
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r') as f: chat_history = json.load(f)
        except: chat_history = []

def save():
    with open(CHAT_FILE, 'w') as f: json.dump(chat_history, f, indent=2, ensure_ascii=False)

def reply(msg):
    m = msg.lower()
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
                
                # Auto-detect UI/UX commands
                if UI_SKILL_ENABLED and detect_ui_command(t):
                    result = ui_skill_execute(t)
                    if result and result.get('success'):
                        r = result['message']
                        bid = str(uuid.uuid4())
                        chat_history.append({"id":bid,"text":r,"is_user":False,"time":datetime.now().isoformat()})
                        save()
                        self.send_json({"success":True,"response":r,"id":bid,"time":datetime.now().isoformat(),"skill":"ui_ux_template"})
                        return
                
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
    print(f"🚀 Nxlebot Clean Server\n🌐 http://localhost:{PORT}\n{'='*40}")
    load()
    with socketserver.TCPServer(("",PORT),H) as httpd:
        print("✅ RUNNING!")
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\n👋 Stopped")
