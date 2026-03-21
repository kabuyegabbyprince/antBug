# antiRug - System Optimizer & Cleaner

## 🚀 New: Glassmorphism & Water Design Theme
**Implemented modern glassmorphism UI** with water/ocean theme:
- **Glass Elements**: Semi-transparent frosted cards (#1e2a3a bg, subtle cyan borders #4a90e2), hover glows.
- **Water Effects**: Deep ocean gradient bg (#0f1a26), animated sine waves (Canvas), fluid cyan accents (#00d4ff).
- **Enhanced UX**: Emojis, Segoe UI fonts, smooth progressbars, live stats/logs.
- **Two UIs**: `ui/dashboard_fixed.py` (full-featured: tray/service preview), `ui/dashboard.py` (lightweight).
- **main.py** integrates seamlessly with tray/background.

**Screenshot Preview**: Modern, performant, Windows-native look.

## Current State Analysis

### Overview
antiRug Enterprise is a Windows desktop application designed as an aggressive system optimizer and cleaner. It operates in three main layers:
1. **Background Service**: Continuously monitors and optimizes system resources every 30 seconds.
2. **System Tray Icon**: Provides quick access to dashboard and exit functionality.
3. **Dashboard UI**: Advanced glassmorphism interface with real-time monitoring, safe controls, config, service management.

### Architecture
```
antiRug/
├── main.py               # Entry point: launches all components
├── service.py            # Windows service wrapper
├── requirements.txt      # Dependencies
├── installer.iss         # Inno Setup installer
├── core/                 # Optimization logic
│   ├── cleaner.py        # Deletes temp files (⚠️ Aggressive)
│   └── optimize.py       # Terminates high-CPU processes (⚠️ Risky)
├── services/
│   └── background.py     # Main optimization loop
├── tray/
│   └── tray.py           # System tray menu
├── ui/
│   ├── dashboard.py      # Lightweight glass UI
│   └── dashboard_fixed.py # Full-featured glass UI
└── utils/
    └── logger.py         # Logging to logs/app.log
```

### Key Features
- **Auto-Optimization**: Every 30s, kills processes using >70% CPU (excludes whitelist).
- **Temp Cleaning**: Deletes **all** files/folders in Windows temp.
- **Glassmorphism Dashboard**: Tabs for Monitoring (live CPU/RAM/disk/processes), Controls (safe preview ops), Logs (auto-tail), Settings (threshold/whitelist), Service (install/start/stop).
- **System Tray**: Right-click for Dashboard/Exit.
- **Configurable**: UI edits threshold/whitelist, auto-save to ui/config.json.
- **Logging**: `logs/app.log`.
- **Windows Service**: Persistent background mode.

### Dependencies (requirements.txt)
```
psutil          # System monitoring
pystray         # System tray
pillow          # Tray images
pywin32         # Windows service
```

**Status**: ✅ All satisfied.

### Risks & Improvements
⚠️ **Aggressive defaults**: Temp deletion/process kill - use with caution.
✅ **Safety**: UI previews confirmations.

**Todo**: Safer cleaning (user confirm), tests, PyInstaller.

## User Manual

### 1. Run / Test
```bash
cd c:/Users/princ/Desktop/ALL/antiRug
pip install -r requirements.txt
python main.py
```
- Tray icon appears.
- Dashboard opens with glass/water design.
- Background optimizes.
- **Test UI**: `python ui/dashboard_fixed.py`

### 2. Service Install (Admin)
```bash
python service.py install
net start AntiRugService
```

**Manage via Dashboard > Service tab**.

### 3. Build EXE/Installer
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data \"tray;tray\" main.py
# Edit installer.iss, compile with Inno Setup
```

### Troubleshooting
| Issue | Fix |
|-------|-----|
| UI not glass | Tkinter theme cached? Restart. |
| Waves not animating | Canvas init delay. |
| Service | Run Admin, check logs. |

## Build Status: 🎉 Feature-Complete with Modern UI
**Test with `python main.py` to see glassmorphism/water design in action!**






