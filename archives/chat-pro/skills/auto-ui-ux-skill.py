#!/usr/bin/env python3
"""
Auto UI/UX Template Skill
Automatically generates UI templates based on user commands
"""

import re
from datetime import datetime

SKILL_NAME = "Auto UI/UX Template Generator"
SKILL_VERSION = "1.0"
SKILL_TRIGGER = [
    'buat ui', 'buat ux', 'buat template', 'buat interface',
    'create ui', 'create ux', 'create template', 'create interface',
    'design ui', 'design ux', 'ui design', 'ux design',
    'landing page', 'dashboard', 'form', 'login page', 'signup',
    'profile page', 'settings page', 'chat ui', 'message ui'
]

TEMPLATES = {
    'landing': '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Landing Page</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>*{font-family:'Inter',sans-serif}</style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 min-h-screen">
<nav class="flex items-center justify-between px-6 py-4 backdrop-blur-lg bg-white/5 border-b border-white/10">
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-xl">🚀</div>
<span class="text-xl font-bold text-white">YourBrand</span>
</div>
<div class="flex gap-4">
<a href="#" class="text-slate-300 hover:text-white transition">Features</a>
<a href="#" class="text-slate-300 hover:text-white transition">Pricing</a>
<a href="#" class="text-slate-300 hover:text-white transition">Contact</a>
<button class="px-6 py-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-lg font-semibold text-white hover:shadow-lg hover:shadow-blue-500/30 transition">Get Started</button>
</div>
</nav>
<main class="max-w-6xl mx-auto px-6 py-20 text-center">
<h1 class="text-6xl font-bold text-white mb-6">Build Something <span class="bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">Amazing</span></h1>
<p class="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">Create beautiful, modern websites with our powerful tools. Join thousands of developers building the future.</p>
<div class="flex gap-4 justify-center">
<button class="px-8 py-4 bg-gradient-to-r from-blue-500 to-green-500 rounded-xl font-bold text-white text-lg hover:shadow-xl hover:shadow-blue-500/30 hover:scale-105 transition">Start Free Trial</button>
<button class="px-8 py-4 bg-white/10 backdrop-blur border border-white/20 rounded-xl font-bold text-white text-lg hover:bg-white/20 transition">Learn More</button>
</div>
<div class="grid md:grid-cols-3 gap-6 mt-20">
<div class="p-6 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
<div class="text-4xl mb-4">⚡</div>
<h3 class="text-xl font-bold text-white mb-2">Lightning Fast</h3>
<p class="text-slate-400">Optimized for speed and performance</p>
</div>
<div class="p-6 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
<div class="text-4xl mb-4">🔒</div>
<h3 class="text-xl font-bold text-white mb-2">Secure</h3>
<p class="text-slate-400">Enterprise-grade security built-in</p>
</div>
<div class="p-6 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
<div class="text-4xl mb-4">🎨</div>
<h3 class="text-xl font-bold text-white mb-2">Beautiful</h3>
<p class="text-slate-400">Stunning designs out of the box</p>
</div>
</div>
</main>
</body>
</html>''',

    'dashboard': '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>*{font-family:'Inter',sans-serif}</style>
</head>
<body class="bg-slate-900 text-white">
<div class="flex h-screen">
<aside class="w-64 bg-slate-800/50 backdrop-blur border-r border-slate-700 p-6">
<div class="flex items-center gap-3 mb-8">
<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-xl">📊</div>
<span class="font-bold text-lg">Dashboard</span>
</div>
<nav class="space-y-2">
<a href="#" class="flex items-center gap-3 px-4 py-3 bg-blue-500/20 text-blue-400 rounded-xl"><span>🏠</span> Home</a>
<a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700/50 rounded-xl transition"><span>📈</span> Analytics</a>
<a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700/50 rounded-xl transition"><span>👥</span> Users</a>
<a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700/50 rounded-xl transition"><span>⚙️</span> Settings</a>
</nav>
</aside>
<main class="flex-1 p-8 overflow-y-auto">
<header class="flex items-center justify-between mb-8">
<h1 class="text-3xl font-bold">Welcome back, User! 👋</h1>
<div class="flex items-center gap-4">
<button class="px-4 py-2 bg-slate-700/50 rounded-lg hover:bg-slate-600/50 transition">🔔 Notifications</button>
<div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center">👤</div>
</div>
</header>
<div class="grid md:grid-cols-4 gap-6 mb-8">
<div class="p-6 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl">
<div class="text-slate-400 text-sm mb-2">Total Revenue</div>
<div class="text-3xl font-bold text-green-400">$12,450</div>
<div class="text-green-400 text-sm mt-2">↑ 12% from last month</div>
</div>
<div class="p-6 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl">
<div class="text-slate-400 text-sm mb-2">Active Users</div>
<div class="text-3xl font-bold text-blue-400">1,234</div>
<div class="text-blue-400 text-sm mt-2">↑ 8% from last week</div>
</div>
<div class="p-6 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl">
<div class="text-slate-400 text-sm mb-2">Orders</div>
<div class="text-3xl font-bold text-purple-400">456</div>
<div class="text-purple-400 text-sm mt-2">↑ 15% from yesterday</div>
</div>
<div class="p-6 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl">
<div class="text-slate-400 text-sm mb-2">Conversion</div>
<div class="text-3xl font-bold text-orange-400">3.2%</div>
<div class="text-orange-400 text-sm mt-2">↑ 2% from last month</div>
</div>
</div>
<div class="grid md:grid-cols-2 gap-6">
<div class="p-6 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl">
<h3 class="font-bold mb-4">Recent Activity</h3>
<div class="space-y-3">
<div class="flex items-center gap-3 p-3 bg-slate-700/30 rounded-xl"><div class="w-2 h-2 bg-green-500 rounded-full"></div><span class="text-sm">New user registered</span><span class="text-xs text-slate-400 ml-auto">2m ago</span></div>
<div class="flex items-center gap-3 p-3 bg-slate-700/30 rounded-xl"><div class="w-2 h-2 bg-blue-500 rounded-full"></div><span class="text-sm">Order #1234 completed</span><span class="text-xs text-slate-400 ml-auto">5m ago</span></div>
<div class="flex items-center gap-3 p-3 bg-slate-700/30 rounded-xl"><div class="w-2 h-2 bg-purple-500 rounded-full"></div><span class="text-sm">Payment received</span><span class="text-xs text-slate-400 ml-auto">10m ago</span></div>
</div>
</div>
<div class="p-6 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl">
<h3 class="font-bold mb-4">Quick Actions</h3>
<div class="grid grid-cols-2 gap-3">
<button class="p-4 bg-blue-500/20 text-blue-400 rounded-xl hover:bg-blue-500/30 transition">➕ Add User</button>
<button class="p-4 bg-green-500/20 text-green-400 rounded-xl hover:bg-green-500/30 transition">📊 Report</button>
<button class="p-4 bg-purple-500/20 text-purple-400 rounded-xl hover:bg-purple-500/30 transition">⚙️ Settings</button>
<button class="p-4 bg-orange-500/20 text-orange-400 rounded-xl hover:bg-orange-500/30 transition">📧 Export</button>
</div>
</div>
</div>
</main>
</div>
</body>
</html>''',

    'login': '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>*{font-family:'Inter',sans-serif}</style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 min-h-screen flex items-center justify-center p-4">
<div class="w-full max-w-md">
<div class="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-3xl p-8 shadow-2xl">
<div class="text-center mb-8">
<div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-3xl mx-auto mb-4 shadow-lg shadow-blue-500/30">🔐</div>
<h1 class="text-2xl font-bold text-white">Welcome Back</h1>
<p class="text-slate-400 mt-2">Sign in to continue to your account</p>
</div>
<form class="space-y-4">
<div>
<label class="block text-sm font-medium text-slate-300 mb-2">Email</label>
<input type="email" class="w-full bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition" placeholder="you@example.com">
</div>
<div>
<label class="block text-sm font-medium text-slate-300 mb-2">Password</label>
<input type="password" class="w-full bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition" placeholder="••••••••">
</div>
<div class="flex items-center justify-between text-sm">
<label class="flex items-center gap-2 text-slate-400"><input type="checkbox" class="rounded bg-slate-700 border-slate-600 text-blue-500"> Remember me</label>
<a href="#" class="text-blue-400 hover:text-blue-300">Forgot password?</a>
</div>
<button type="submit" class="w-full py-3 bg-gradient-to-r from-blue-500 to-green-500 rounded-xl font-bold text-white hover:shadow-lg hover:shadow-blue-500/30 hover:scale-[1.02] transition">Sign In</button>
</form>
<div class="mt-6 text-center text-sm text-slate-400">
Don't have an account? <a href="#" class="text-blue-400 hover:text-blue-300 font-medium">Sign up</a>
</div>
<div class="mt-6 pt-6 border-t border-slate-700">
<div class="text-center text-sm text-slate-400 mb-4">Or continue with</div>
<div class="grid grid-cols-2 gap-3">
<button class="flex items-center justify-center gap-2 p-3 bg-slate-700/50 rounded-xl hover:bg-slate-600/50 transition"><span class="text-xl">🔵</span> Google</button>
<button class="flex items-center justify-center gap-2 p-3 bg-slate-700/50 rounded-xl hover:bg-slate-600/50 transition"><span class="text-xl">⚫</span> GitHub</button>
</div>
</div>
</div>
</div>
</body>
</html>''',

    'chat': '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chat UI</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>*{font-family:'Inter',sans-serif}</style>
</head>
<body class="bg-slate-900 h-screen flex">
<aside class="w-80 bg-slate-800/50 backdrop-blur border-r border-slate-700 flex flex-col">
<div class="p-4 border-b border-slate-700">
<div class="flex items-center gap-3 mb-4">
<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-xl">💬</div>
<h1 class="font-bold text-lg">Messages</h1>
</div>
<input type="text" placeholder="Search chats..." class="w-full bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-blue-500">
</div>
<div class="flex-1 overflow-y-auto p-2 space-y-2">
<div class="flex items-center gap-3 p-3 bg-blue-500/20 rounded-xl cursor-pointer">
<div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-lg">👤</div>
<div class="flex-1 min-w-0">
<div class="font-medium text-white truncate">John Doe</div>
<div class="text-sm text-slate-400 truncate">Hey! How are you?</div>
</div>
<div class="text-xs text-slate-500">2m</div>
</div>
<div class="flex items-center gap-3 p-3 hover:bg-slate-700/30 rounded-xl cursor-pointer transition">
<div class="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-lg">👤</div>
<div class="flex-1 min-w-0">
<div class="font-medium text-white truncate">Jane Smith</div>
<div class="text-sm text-slate-400 truncate">See you tomorrow!</div>
</div>
<div class="text-xs text-slate-500">1h</div>
</div>
</div>
</aside>
<main class="flex-1 flex flex-col">
<header class="p-4 border-b border-slate-700 flex items-center justify-between">
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-lg">👤</div>
<div>
<div class="font-medium text-white">John Doe</div>
<div class="text-sm text-green-400">● Online</div>
</div>
</div>
<div class="flex gap-2">
<button class="p-2 hover:bg-slate-700/50 rounded-lg transition">📞</button>
<button class="p-2 hover:bg-slate-700/50 rounded-lg transition">📹</button>
<button class="p-2 hover:bg-slate-700/50 rounded-lg transition">⋮</button>
</div>
</header>
<div class="flex-1 overflow-y-auto p-4 space-y-4" id="chat">
<div class="flex gap-3">
<div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center text-sm flex-shrink-0">👤</div>
<div class="max-w-[70%]">
<div class="bg-slate-800 rounded-2xl rounded-tl-none px-4 py-2 text-white inline-block">Hey! How are you?</div>
<div class="text-xs text-slate-500 mt-1 ml-1">10:30 AM</div>
</div>
</div>
<div class="flex gap-3 flex-row-reverse">
<div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-sm flex-shrink-0">👤</div>
<div class="max-w-[70%]">
<div class="bg-gradient-to-r from-blue-500 to-green-500 rounded-2xl rounded-tr-none px-4 py-2 text-white inline-block">I'm good! Working on a new project 🚀</div>
<div class="text-xs text-slate-500 mt-1 mr-1 text-right">10:32 AM</div>
</div>
</div>
</div>
<footer class="p-4 border-t border-slate-700">
<div class="flex gap-3 max-w-4xl mx-auto">
<button class="p-3 hover:bg-slate-700/50 rounded-xl transition">📎</button>
<input type="text" placeholder="Type a message..." class="flex-1 bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500">
<button class="p-3 bg-gradient-to-r from-blue-500 to-green-500 rounded-xl hover:shadow-lg hover:shadow-blue-500/30 transition">➤</button>
</div>
</footer>
</main>
</body>
</html>'''
}

def detect_ui_command(text):
    """Detect if user wants UI/UX template"""
    text_lower = text.lower()
    
    # Check for trigger words
    for trigger in SKILL_TRIGGER:
        if trigger in text_lower:
            return True
    
    # Check for specific template requests
    if any(word in text_lower for word in ['template', 'design', 'interface', 'ui', 'ux', 'page', 'dashboard', 'landing']):
        return True
    
    return False

def generate_template(text):
    """Generate appropriate UI template based on request"""
    text_lower = text.lower()
    
    # Determine template type
    if any(word in text_lower for word in ['landing', 'homepage', 'home', 'hero']):
        return 'landing', TEMPLATES['landing']
    elif any(word in text_lower for word in ['dashboard', 'admin', 'panel', 'stats']):
        return 'dashboard', TEMPLATES['dashboard']
    elif any(word in text_lower for word in ['login', 'signin', 'sign in', 'auth']):
        return 'login', TEMPLATES['login']
    elif any(word in text_lower for word in ['chat', 'message', 'conversation']):
        return 'chat', TEMPLATES['chat']
    else:
        # Default to landing page
        return 'landing', TEMPLATES['landing']

def execute(text):
    """Execute the skill"""
    if not detect_ui_command(text):
        return None
    
    template_name, template_html = generate_template(text)
    
    # Save template to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ui_template_{template_name}_{timestamp}.html"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template_html)
        
        return {
            'success': True,
            'template': template_name,
            'filename': filename,
            'message': f"✅ UI Template generated: **{template_name}**\n\n📁 Saved to: `{filename}`\n\n✨ Features:\n• Modern HeroUI design\n• Tailwind CSS\n• Responsive\n• Dark mode\n• Glassmorphism effects",
            'preview': template_html[:500] + '...'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Skill metadata
SKILL_INFO = {
    'name': SKILL_NAME,
    'version': SKILL_VERSION,
    'description': 'Auto-generates beautiful UI/UX templates based on user commands',
    'triggers': SKILL_TRIGGER,
    'templates': list(TEMPLATES.keys()),
    'author': 'Nxlebot',
    'auto_activate': True
}

if __name__ == '__main__':
    # Test
    print("Testing Auto UI/UX Skill...")
    result = execute("Buat landing page yang keren")
    if result:
        print(f"✅ Success: {result['template']}")
        print(f"📁 File: {result['filename']}")
    else:
        print("❌ No match")
