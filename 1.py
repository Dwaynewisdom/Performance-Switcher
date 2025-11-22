import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import threading

class AdvancedPowerManager:
    def __init__(self):
        self.power_plans = {
            "High Performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "Balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "Power Saver": "a1841308-3541-4fab-bc81-f71556f20b4a"
        }
        
    def get_current_plan(self):
        """Get the currently active power plan"""
        try:
            result = subprocess.run(
                "powercfg /getactivescheme", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            for name, guid in self.power_plans.items():
                if guid in result.stdout:
                    return name
            return "Unknown"
        except:
            return "Error"
    
    def set_power_plan(self, plan_name, update_callback=None):
        """Set power plan with optional callback for status updates"""
        def apply_settings():
            try:
                if update_callback:
                    update_callback(f"Applying {plan_name}...")
                
                guid = self.power_plans[plan_name]
                subprocess.run(f"powercfg /setactive {guid}", shell=True, check=True)
                
                self.apply_additional_settings(plan_name)
                
                if update_callback:
                    update_callback(f"✓ {plan_name} applied successfully!")
                return True
                
            except Exception as e:
                if update_callback:
                    update_callback(f"✗ Error: {str(e)}")
                return False
        

        thread = threading.Thread(target=apply_settings)
        thread.daemon = True
        thread.start()
    
    def apply_additional_settings(self, plan_name):
        """Apply custom settings for each power plan"""
        settings = {
            "High Performance": {
                "monitor_ac": 15, "monitor_dc": 10,
                "standby_ac": 45, "standby_dc": 30,
                "hibernate_ac": 0, "hibernate_dc": 120
            },
            "Balanced": {
                "monitor_ac": 10, "monitor_dc": 5,
                "standby_ac": 30, "standby_dc": 15,
                "hibernate_ac": 0, "hibernate_dc": 60
            },
            "Power Saver": {
                "monitor_ac": 5, "monitor_dc": 3,
                "standby_ac": 15, "standby_dc": 10,
                "hibernate_ac": 0, "hibernate_dc": 30
            }
        }
        
        if plan_name in settings:
            s = settings[plan_name]
            commands = [
                f"powercfg /change monitor-timeout-ac {s['monitor_ac']}",
                f"powercfg /change monitor-timeout-dc {s['monitor_dc']}",
                f"powercfg /change standby-timeout-ac {s['standby_ac']}",
                f"powercfg /change standby-timeout-dc {s['standby_dc']}",
                f"powercfg /change hibernate-timeout-ac {s['hibernate_ac']}",
                f"powercfg /change hibernate-timeout-dc {s['hibernate_dc']}"
            ]
            
            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True)

class AdvancedPowerManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Power Settings Manager")
        self.root.geometry("700x400")
        
        self.manager = AdvancedPowerManager()
        self.setup_ui()
        self.update_current_plan()
    
    def setup_ui(self):
        """Create advanced user interface"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        

        ttk.Label(main_frame, text="Current Power Plan:", font=('Arial', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        self.current_plan_label = ttk.Label(
            main_frame, 
            text="Checking...", 
            font=('Arial', 10, 'bold'),
            foreground="blue"
        )
        self.current_plan_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 20))
        

        ttk.Label(main_frame, text="Select New Power Mode:", font=('Arial', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        self.mode_var = tk.StringVar(value="Balanced")
        
        modes = [
            ("🚀 High Performance", "High Performance"),
            ("⚖️ Balanced", "Balanced"), 
            ("🔋 Power Saver", "Power Saver")
        ]
        
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(
                main_frame, 
                text=text,
                variable=self.mode_var, 
                value=value
            ).grid(row=i+2, column=0, columnspan=2, sticky=tk.W, pady=5)
        

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame,
            text="🚀 Performance",
            command=lambda: self.apply_quick_mode("High Performance")
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="⚖️ Balanced", 
            command=lambda: self.apply_quick_mode("Balanced")
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔋 Power Saver",
            command=lambda: self.apply_quick_mode("Power Saver")  
        ).pack(side=tk.LEFT, padx=5)
        
  
        self.status_label = ttk.Label(
            main_frame, 
            text="Ready to change power settings",
            font=('Arial', 9)
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=10)
        

        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=300
        )
        self.progress.grid(row=7, column=0, columnspan=2, pady=5)
        

        ttk.Button(
            main_frame,
            text="🔄 Refresh Current Status",
            command=self.update_current_plan
        ).grid(row=8, column=0, columnspan=2, pady=10)
    
    def update_current_plan(self):
        """Update the display with current power plan"""
        def get_plan():
            current = self.manager.get_current_plan()
            self.root.after(0, lambda: self.current_plan_label.config(
                text=current, 
                foreground="green" if current != "Error" else "red"
            ))
        
        threading.Thread(target=get_plan, daemon=True).start()
    
    def apply_quick_mode(self, mode):
        """Apply power mode from quick buttons"""
        self.mode_var.set(mode)
        self.apply_settings()
    
    def apply_settings(self):
        """Apply the selected power settings"""
        selected_mode = self.mode_var.get()
        

        self.progress.start()
        self.status_label.config(text=f"Applying {selected_mode} mode...", foreground="blue")
        
        def update_status(message):
            self.root.after(0, lambda: self.status_label.config(
                text=message,
                foreground="green" if "✓" in message else "red"
            ))
            if "✓" in message or "✗" in message:
                self.root.after(0, self.progress.stop)
                self.root.after(1000, self.update_current_plan)
        
        self.manager.set_power_plan(selected_mode, update_callback=update_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedPowerManagerApp(root)
    root.mainloop()