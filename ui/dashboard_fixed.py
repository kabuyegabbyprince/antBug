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
            colors = ['#00d4ff', '#4a90e2', '#a0c4ff']
            for i, color in enumerate(colors):
                alpha_wave = height * 0.7 + math.sin(self.time + i * 2) * 10
                self.create_line(0, alpha_wave, width, alpha_wave, fill=color, width=4-i, tags='wave', smooth=True)
        self.after(50, self.animate)

class AntiRugDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "antiRug Enterprise - Glassmorphism Dashboard")
        self.root.geometry("1100x850")
        self.root.configure(bg="#0f1a26")
        self.accent = '#00d4ff'
        self.glass_bg = '#1e2a3a'
        self.glass_hover = '#2d3e50'
        self.text_primary = '#e2f3ff'
        self.text_secondary = '#a0c4ff'
        
        try:
            self.config = load_config()
        except:
            self.config = {}
        self.auto_running = True
        self.process_list_data = []  # Store (pid, cpu, name) tuples
        
        self.style = ttk.Style()
        self.setup_glass_theme()
        self.create_widgets()
        self.start_updates()
        
    def setup_glass_theme(self):
        self.style.theme_use('clam')
        self.style.configure('Glass.TFrame', background=self.glass_bg, relief='flat')
        self.style.configure('Glass.TLabel', foreground=self.text_primary, background=self.glass_bg)
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=self.accent, background='#0a1420')
        self.style.configure('Glass.TButton', background=self.glass_bg, foreground=self.text_primary, relief='flat')
        self.style.map('Glass.TButton', background=[('active', self.glass_hover)])
        self.style.configure('Water.TProgressbar', troughcolor='#0f1a26', lightcolor=self.accent)
        
    def create_widgets(self):
        # Header
        header = ttk.Frame(self.root, style='Glass.TFrame')
        header.pack(fill='x', padx=15, pady=10)
        ttk.Label(header, text="🌊 antiRug Enterprise", style='Header.TLabel').pack(side='left')
        self.status_label = ttk.Label(header, text="Status: Running", style='Glass.TLabel')
        self.status_label.pack(side='right')
        self.auto_toggle = tk.Checkbutton(header, text="Auto", bg="#0f1a26", fg=self.text_primary, 
                                         selectcolor=self.glass_bg, activeforeground=self.accent, command=self.toggle_auto)
        self.auto_toggle.select()
        self.auto_toggle.pack(side='right', padx=15)
        
        # Waves
        self.wave_canvas = WaterWaveCanvas(self.root, height=100, bg="#0f1a26")
        self.wave_canvas.pack(fill='x')
        
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.create_monitoring_tab()
        self.create_controls_tab()
        self.create_logs_tab()
        self.create_config_tab()
        
        # Footer
        footer = ttk.Frame(self.root, style='Glass.TFrame')
        footer.pack(fill='x', pady=10)
        ttk.Button(footer, text="Exit", command=self.root.quit, style='Glass.TButton').pack(side='right', padx=15)
    
    def create_monitoring_tab(self):
        self.monitor_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.monitor_tab, text="👁️ Monitoring & Manual Kill")
        
        # Stats
        stats_frame = ttk.LabelFrame(self.monitor_tab, text="Stats", style='Glass.TLabel')
        stats_frame.pack(fill='x', padx=15, pady=15)
        
        self.cpu_label = ttk.Label(stats_frame, text="CPU: 0%", font=('Segoe UI', 14, 'bold'))
        self.cpu_label.pack(pady=5)
        self.cpu_prog = ttk.Progressbar(stats_frame, length=400, style='Water.TProgressbar')
        self.cpu_prog.pack(pady=5)
        
        self.ram_label = ttk.Label(stats_frame, text="RAM: 0%")
        self.ram_label.pack(pady=5)
        self.ram_prog = ttk.Progressbar(stats_frame, length=400, style='Water.TProgressbar')
        self.ram_prog.pack(pady=5)
        
        # Process manager
        proc_frame = ttk.LabelFrame(self.monitor_tab, text="Running Processes - SELECT & KILL", style='Glass.TLabel')
        proc_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        list_frame = ttk.Frame(proc_frame)
        list_frame.pack(fill='both', expand=True)
        
        # Multi-select listbox
        self.proc_list = tk.Listbox(list_frame, bg=self.glass_bg, fg=self.text_primary, selectbackground=self.accent,
                                   selectmode='multiple', font=('Consolas', 9), relief='flat')
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.proc_list.yview)
        self.proc_list.configure(yscrollcommand=scrollbar.set)
        self.proc_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Kill buttons
        btn_frame = ttk.Frame(proc_frame)
        btn_frame.pack(fill='x', pady=10)
        ttk.Button(btn_frame, text="🔴 Kill Selected", command=self.kill_selected, style='Glass.TButton').pack(side='left', padx=10)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_procs, style='Glass.TButton').pack(side='left', padx=10)
        self.kill_count_label = ttk.Label(btn_frame, text="Killed: 0", style='Glass.TLabel')
        self.kill_count_label.pack(side='right')
        
    def create_controls_tab(self):
        self.controls_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.controls_tab, text="⚙️ Controls")
        btn_frame = ttk.Frame(self.controls_tab, style='Glass.TFrame')
        btn_frame.place(relx=0.5, rely=0.5, anchor='center')
        ttk.Button(btn_frame, text="🧹 Clean Temp", command=self.clean_temp, style='Glass.TButton').pack(pady=20, ipadx=30)
        ttk.Button(btn_frame, text="🚀 Auto Optimize", command=self.optimize_now, style='Glass.TButton').pack(pady=10, ipadx=30)
    
    def create_logs_tab(self):
        self.logs_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.logs_tab, text="📋 Logs")
        self.logs_text = tk.Text(self.logs_tab, bg="#0f1a26", fg=self.text_secondary)
        self.logs_text.pack(fill='both', expand=True, padx=15, pady=15)
    
    def create_config_tab(self):
        self.config_tab = ttk.Frame(self.notebook, style='Glass.TFrame')
        self.notebook.add(self.config_tab, text="⚙️ Settings")
        ttk.Label(self.config_tab, text="CPU Threshold (%):").pack(pady=15)
        self.threshold_var = tk.StringVar(value=str(self.config.get('cpu_threshold', 80)))
        ttk.Entry(self.config_tab, textvariable=self.threshold_var).pack(pady=5)
        ttk.Label(self.config_tab, text="Whitelist:").pack(pady=(20,5))
        self.whitelist_text = tk.Text(self.config_tab, height=6, bg=self.glass_bg, fg=self.text_primary)
        self.whitelist_text.pack(pady=5)
        ttk.Button(self.config_tab, text="Save", command=self.save_ui_config, style='Glass.TButton').pack(pady=20)
        self.load_whitelist()
    
    def refresh_procs(self):
        self.update_process_list()
    
    def update_process_list(self):
        self.proc_list.delete(0, 'end')
        self.process_list_data = []
        whitelist = get_whitelist()
        
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                info = p.info
                pid = info['pid']
                name = info['name']
                cpu = info['cpu_percent'] or 0
                
                if name not in whitelist:
                    display = f"PID {pid} | {cpu:.1f}% | {name}"
                    self.proc_list.insert('end', display)
                    self.process_list_data.append((pid, name, cpu))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def kill_selected(self):
        selected_indices = self.proc_list.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Select processes to kill.")
            return
        
        to_kill = [self.process_list_data[i] for i in selected_indices]
        names = [name for _, name, _ in to_kill]
        
        if messagebox.askyesno("Confirm Kill", f"Kill {len(to_kill)} processes?\n\n" + "\n".join(names[:10])):
            killed = 0
            for pid, name, _ in to_kill:
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                    killed += 1
                    logger.info(f"Manual kill: PID {pid} ({name})")
                except:
                    pass
            
            self.kill_count_label['text'] = f"Killed: {killed}"
            self.refresh_procs()
            messagebox.showinfo("Done", f"Killed {killed}/{len(to_kill)} processes.")
    
    def start_updates(self):
        self.update_stats()
        self.update_process_list()
        threading.Thread(target=self.auto_loop, daemon=True).start()
    
    def update_stats(self):
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            self.cpu_label['text'] = f"CPU: {cpu:.1f}%"
            self.cpu_prog['value'] = cpu
            self.ram_label['text'] = f"RAM: {ram:.1f}%"
            self.ram_prog['value'] = ram
        except:
            pass
        self.root.after(1000, self.update_stats)
    
    def toggle_auto(self):
        self.config['auto_optimize'] = self.auto_toggle.instate(['selected'])
    
    def auto_loop(self):
        while self.auto_running:
            if self.config.get('auto_optimize', True):
                self.optimize_now(silent=True)
            time.sleep(self.config.get('clean_interval', 300))
    
    def clean_temp(self):
        files = preview_temp_files()
        if messagebox.askyesno("Clean", f"Delete {len(files)} temp files?"):
            clean()
    
    def optimize_now(self, silent=False):
        if not silent and not messagebox.askyesno("Optimize", "Run auto optimization?"):
            return
        optimize()
    
    def save_ui_config(self):
        try:
            self.config['cpu_threshold'] = float(self.threshold_var.get())
            lines = self.whitelist_text.get('1.0', 'end').split(',')
            self.config['whitelist'] = [l.strip() for l in lines if l.strip()]
            save_config(self.config)
            messagebox.showinfo("Saved", "Config saved.")
        except:
            messagebox.showerror("Error", "Invalid config.")
    
    def load_whitelist(self):
        text = ', '.join(self.config.get('whitelist', []))
        self.whitelist_text.insert('1.0', text)
    
    def on_closing(self):
        self.auto_running = False
        self.root.destroy()

def run_ui():
    root = tk.Tk()
    app = AntiRugDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

