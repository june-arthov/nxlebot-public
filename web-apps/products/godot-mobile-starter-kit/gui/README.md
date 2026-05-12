# 🎨 Godot Mobile Starter Kit - GUI Mockup

_Quick UI prototyping using HeroUI_

---

## 🚀 Quick Start

### Option 1: HeroUI Storybook (Recommended)
```bash
cd /home/nxelleai/.openclaw/workspace/heroui
pnpm dev
# Opens at http://localhost:3000
```

### Option 2: Simple HTML/JS Mockup
```bash
cd /home/nxelleai/.openclaw/workspace/products/godot-mobile-starter-kit/gui
python3 -m http.server 8080
# Opens at http://localhost:8080
```

---

## 📐 UI Components to Design

### 1. Main Menu
- Game Title
- Start Button
- Settings Button
- Shop Button
- Exit Button

### 2. Shop/Store UI
- Product cards (IAP items)
- Coin/Gem display
- Purchase buttons
- Restore purchases button

### 3. Settings Screen
- Audio sliders (BGM, SFX)
- Graphics quality dropdown
- Language selector
- Reset button

### 4. HUD Template
- Health bar
- Score counter
- Currency display (coins/gems)
- Pause button

### 5. Virtual Controls
- Left joystick
- Right joystick (optional)
- Action buttons (A, B, X, Y)
- D-Pad (optional)

---

## 🎨 Design System

### Colors (Godot Theme)
```
Primary: #3498db (Blue)
Secondary: #2ecc71 (Green)
Accent: #e74c3c (Red)
Background: #2c3e50 (Dark)
Text: #ecf0f1 (Light)
```

### Fonts
```
Headings: Montserrat / Poppins
Body: Open Sans / Roboto
Monospace: Fira Code (for code examples)
```

### Spacing
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
```

---

## 📁 File Structure

```
gui/
├── index.html (main showcase page)
├── styles/
│   └── godot-theme.css
├── components/
│   ├── main-menu.html
│   ├── shop-ui.html
│   ├── settings.html
│   ├── hud.html
│   └── controls.html
├── scripts/
│   └── interactions.js
└── assets/
    ├── icons/
    └── images/
```

---

## ✅ Checklist

- [ ] Setup dev server
- [ ] Create main showcase page
- [ ] Design Main Menu component
- [ ] Design Shop UI component
- [ ] Design Settings component
- [ ] Design HUD component
- [ ] Design Virtual Controls
- [ ] Add interactivity (JS)
- [ ] Export to Godot-compatible format

---

**READY TO CODE!** 💻
