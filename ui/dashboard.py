import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import subprocess
import os
from pathlib import Path
import math
from utils.config import load_config, save_config, preview_temp_files, preview_high_cpu_processes, get_whitelist
from core.cleaner import clean
from core.optimize import optimize
from utils.logger import setup_logger

logger = setup_logger()
CONFIG_PATH = Path('ui/config.json')

class WaterWaveCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.time = 0
        self.animate()
    
    def animate(self):
        self.time += 0.05
        self.delete('wave')
        width = self.winfo_width()
        height = self.winfo_height()
        if width > 1 and height > 1:
            for i in range(2):
                wave_y = height * 0.8 + math.sin(self.time + i * 3) * 8
                self.create_line(0, wave_y, width, wave_y, fill=f'#00d4ff{int(30 - i*15):02x}', width=2, tags='wave', smooth=True)
        self.after(80, self.animate)

class AntiRugDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("antiRug Enterprise - Glassmorphism Dashboard")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#0f1a26")  # Ocean water deep
        
        try:
            self.config = load_config()
        except Exception as e:
            logger.error(f"Config load error: {e}")
            self.config = {}
        self.auto_running = True
        
        self.style = ttk.Style()
        self.setup_glass_theme()
        
        self.create_widgets()
        self.start_updates()
        
    def setup_glass_theme(self):
        self.style.theme_use('clam')
        
        # Glassmorphism & Water colors matching fixed version
        glass_bg = '#1e2a3a'
        glass_hover = '#2d3e50'
        border_water = '#4a90e2'
        accent = '#00d4ff'
        text_primary = '#e2f3ff'
        text_secondary = '#a0c4ff'
        
        self.style.configure('Glass.TFrame', background=glass_bg, relief='flat')
        self.style.configure('Glass.TLabel', background=glass_bg, foreground=text_primary)
        self.style.configure('Header.Glass.TLabel', font=('Segoe UI', 14, 'bold'), 
                           background='#0a1420', foreground=accent)
        self.style.configure('Glass.TButton', background=glass_bg, foreground=text_primary, 
                           relief='flat', borderwidth=1)
        self.style.map('Glass.TButton', background=[('active', glass_hover)])
        
        # Progress water
        self.style.configure('Water.TProgressbar', background=glass_bg, troughcolor='#0f1a26',
                           lightcolor=accent, darkcolor='#00a3cc')
        
        self.style.configure('Glass.TNotebook', tabmargins=0)
        self.style.configure('Glass.TNotebook.Tab', background=glass_bg, foreground=text_secondary,
                           padding=[15,8])
    
    def create_widgets(self):
        # Glass header
        header_frame = ttk.Frame(self.root, style='Glass.TFrame')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(header_frame, text="🌊 antiRug Enterprise", style='Header.Glass.TLabel').pack(side='left')
        self.status_label = ttk.Label(header_frame, text="Status: Running", style='Glass.TLabel')
        self.status_label.pack(side='right')
        
        self.auto_toggle = tk.Checkbutton(header_frame, text="Auto Optimize", bg="#0f1a26", fg="#e2f3ff", 
                                         selectcolor="#1e2a3a", command=self.toggle_auto)
        self.auto_toggle.select()
        self.auto_toggle.pack(side='right', padx=10)
        
        # Subtle wave bg
        self.wave_canvas = WaterWaveCanvas(self.root, height=80, bg="#0f1a26")
        self.wave_canvas.pack(fill='x', before=header_frame)
        
        self.notebook = ttk.Notebook(self.root, style='Glass.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.create_monitoring_tab()
        self.create_controls_tab()
        self.create_logs_tab()
        self.create_config_tab()
        self.create_service_tab()
        
        # Footer
        footer = ttk.Frame(self.root, style='Glass.TFrame')
        footer.pack(fill='x', padx=10, pady=5)
        ttk.Button(footer, text="Exit", command=self.root.quit, style='Glass.TButton').pack(side='right')
    
    def create_monitoring_tab(self):
        self.monitor_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.monitor_tab, text="Monitoring")
        
        stats_frame = ttk.LabelFrame(self.monitor_tab, text="System Stats", style='Glass.TLabel')
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        self.cpu_label = ttk.Label(stats_frame, text="CPU: 0%", font=('Segoe UI', 12, 'bold'))
        self.cpu_label.pack(pady=5)
        self.cpu_prog = ttk.Progressbar(stats_frame, length=350, style='Water.TProgressbar')
        self.cpu_prog.pack(pady=5)
        
        self.ram_label = ttk.Label(stats_frame, text="RAM: 0%", font=('Segoe UI', 12))
        self.ram_label.pack(pady=5)
        self.ram_prog = ttk.Progressbar(stats_frame, length=350, style='Water.TProgressbar')
        self.ram_prog.pack(pady=5)
        
        self.disk_label = ttk.Label(stats_frame, text="Disk: 0%", font=('Segoe UI', 12))
        self.disk_label.pack(pady=5)
        self.disk_prog = ttk.Progressbar(stats_frame, length=350, style='Water.TProgressbar')
        self.disk_prog.pack(pady=5)
        
        proc_frame = ttk.LabelFrame(self.monitor_tab, text="Top CPU Processes")
        proc_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.proc_list = tk.Listbox(proc_frame, bg="#1e2a3a", fg="#e2f3ff", selectbackground="#00d4ff")
        self.proc_list.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_controls_tab(self):
        self.controls_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.controls_tab, text="Controls")
        
        btn_frame = ttk.Frame(self.controls_tab)
        btn_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Button(btn_frame, text="🧹 Clean Temp Files", command=self.clean_temp, style='Glass.TButton').pack(pady=15, ipadx=25)
        ttk.Button(btn_frame, text="🚀 Optimize Processes", command=self.optimize_now, style='Glass.TButton').pack(pady=10, ipadx=25)
    
    def create_logs_tab(self):
        self.logs_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.logs_tab, text="Logs")
        
        self.logs_text = tk.Text(self.logs_tab, bg="#0f1a26", fg="#a0c4ff", wrap='word')
        self.logs_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_config_tab(self):
        self.config_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.config_tab, text="Settings")
        
        ttk.Label(self.config_tab, text="CPU Threshold (%):", style='Glass.TLabel').pack(pady=5)
        self.threshold_var = tk.StringVar(value=str(self.config.get('cpu_threshold', 80)))
        ttk.Entry(self.config_tab, textvariable=self.threshold_var, style='Glass.TEntry').pack(pady=5)
        
        ttk.Label(self.config_tab, text="Whitelist (comma sep):", style='Glass.TLabel').pack(pady=(20,5))
        self.whitelist_text = tk.Text(self.config_tab, height=6, bg="#1e2a3a", fg="#e2f3ff")
        self.whitelist_text.pack(pady=5)
        self.load_whitelist()
        
        ttk.Button(self.config_tab, text="💾 Save Config", command=self.save_ui_config, style='Glass.TButton').pack(pady=20)
    
    def create_service_tab(self):
        self.service_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.service_tab, text="Service")
        
        self.service_status = ttk.Label(self.service_tab, text="Status: Unknown", style='Glass.TLabel')
        self.service_status.pack(pady=20)
        
        btn_frame = ttk.Frame(self.service_tab)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="📥 Install", command=lambda: self.service_action('install'), style='Glass.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="▶️ Start", command=lambda: self.service_action('start'), style='Glass.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="⏹️ Stop", command=lambda: self.service_action('stop'), style='Glass.TButton').pack(side='left', padx=5)
    
    def start_updates(self):
        self.update_stats()
        threading.Thread(target=self.auto_loop, daemon=True).start()
    
    def update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:\\').percent if os.name == 'nt' else psutil.disk_usage('/').percent
            
            self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
            self.cpu_prog['value'] = cpu
            self.ram_label.config(text=f"RAM: {ram:.1f}%")
            self.ram_prog['value'] = ram
            self.disk_label.config(text=f"Disk: {disk:.1f}%")
            self.disk_prog['value'] = disk
            
            self.proc_list.delete(0, 'end')
            for p in sorted(psutil.process_iter(['name','cpu_percent']), key=lambda x: x.info['cpu_percent'] or 0, reverse=True)[:10]:
                try:
                    self.proc_list.insert('end', f"{p.info['cpu_percent']:.1f}% {p.info['name']}")
                except:
                    pass
        except Exception as e:
            logger.error(f"Stats error: {e}")
        self.root.after(2000, self.update_stats)
    
    def toggle_auto(self):
        self.config['auto_optimize'] = self.auto_toggle.instate(['selected'])
        self.status_label.config(text="Status: " + ("Running" if self.config['auto_optimize'] else "Paused"))
    
    def auto_loop(self):
        while self.auto_running:
            if self.config.get('auto_optimize', True):
                self.optimize_now(silent=True)
            time.sleep(self.config.get('clean_interval', 30))
    
    def clean_temp(self):
        files = preview_temp_files()
        if messagebox.askyesno("Clean", f"Clean {len(files)} temp files?"):
            clean()
            messagebox.showinfo("Done", "Cleaned.")
    
    def optimize_now(self, silent=False):
        if not silent:
            whitelist = get_whitelist()
            if messagebox.askyesno("Optimize", "Run optimization?"):
                optimize(whitelist=whitelist)
                messagebox.showinfo("Done", "Optimized.")
    
    def save_ui_config(self):
        try:
            self.config['cpu_threshold'] = float(self.threshold_var.get())
            wl = [l.strip() for l in self.whitelist_text.get('1.0', 'end').strip().split(',') if l.strip()]
            self.config['whitelist'] = wl
            save_config(self.config)
            messagebox.showinfo("Saved", "Config saved.")
        except:
            messagebox.showerror("Error", "Save failed.")
    
    def load_whitelist(self):
        wl = ', '.join(self.config.get('whitelist', []))
        self.whitelist_text.insert('1.0', wl)
    
    def service_action(self, action):
        try:
            if action == 'install':
                subprocess.run(['python', 'service.py', 'install'])
            elif action == 'start':
                subprocess.run(['net', 'start', 'AntiRugService'], shell=True)
            elif action == 'stop':
                subprocess.run(['net', 'stop', 'AntiRugService'], shell=True)
            self.service_status.config(text=f"{action}ed")
        except Exception as e:
            messagebox.showerror("Service", str(e))

def run_ui():
    root = tk.Tk()
    app = AntiRugDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

def app_on_closing():
    pass  # Placeholder

