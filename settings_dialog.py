import tkinter as tk
from tkinter import ttk, messagebox
import json

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config.copy()  # 复制配置以避免直接修改
        self.result = None
        
        self.title("设置")
        self.geometry("400x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # 居中显示
        self.geometry("+{}+{}".format(
            int(parent.winfo_x() + parent.winfo_width()/2 - 200),
            int(parent.winfo_y() + parent.winfo_height()/2 - 175)
        ))
        
        self._create_widgets()
        
    def _create_widgets(self):
        # 网络设置
        network_frame = ttk.LabelFrame(self, text="网络设置", padding=(10, 5))
        network_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(network_frame, text="默认端口:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.port_var = tk.StringVar(value=str(self.config['network']['default_port']))
        ttk.Entry(network_frame, textvariable=self.port_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(network_frame, text="帧率 (FPS):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.fps_var = tk.StringVar(value=str(self.config['network']['fps']))
        fps_entry = ttk.Entry(network_frame, textvariable=self.fps_var, width=10)
        fps_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(network_frame, text="JPEG质量 (1-100):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.quality_var = tk.StringVar(value=str(self.config['network']['jpeg_quality']))
        ttk.Entry(network_frame, textvariable=self.quality_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # 视图设置
        viewer_frame = ttk.LabelFrame(self, text="视图设置", padding=(10, 5))
        viewer_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(viewer_frame, text="默认宽度:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.width_var = tk.StringVar(value=str(self.config['viewer']['default_width']))
        ttk.Entry(viewer_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(viewer_frame, text="默认高度:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.height_var = tk.StringVar(value=str(self.config['viewer']['default_height']))
        ttk.Entry(viewer_frame, textvariable=self.height_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(viewer_frame, text="缩放比例:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.zoom_var = tk.StringVar(value=str(self.config['viewer']['zoom_scale']))
        ttk.Entry(viewer_frame, textvariable=self.zoom_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # 性能设置
        performance_frame = ttk.LabelFrame(self, text="性能设置", padding=(10, 5))
        performance_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(performance_frame, text="性能档案:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.profile_var = tk.StringVar(value=self.config.get('performance', {}).get('profile', 'balanced'))
        profile_combo = ttk.Combobox(performance_frame, textvariable=self.profile_var, 
                                   values=['quality', 'balanced', 'performance'],
                                   state='readonly', width=15)
        profile_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # 性能档案说明
        profile_descriptions = {
            'quality': '高质量模式 - 最佳画质，适合演示',
            'balanced': '平衡模式 - 画质与性能平衡',
            'performance': '高性能模式 - 最高帧率，适合游戏'
        }
        
        self.profile_desc_var = tk.StringVar(value=profile_descriptions.get(self.profile_var.get(), ''))
        ttk.Label(performance_frame, textvariable=self.profile_desc_var, 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=0, columnspan=2, 
                                                           sticky="w", padx=5, pady=2)
        
        def on_profile_change(*args):
            self.profile_desc_var.set(profile_descriptions.get(self.profile_var.get(), ''))
            # 根据性能档案自动调整参数
            profile = self.profile_var.get()
            if profile == 'quality':
                self.fps_var.set("8")
                self.quality_var.set("75")
            elif profile == 'balanced':
                self.fps_var.set("15") 
                self.quality_var.set("50")
            elif profile == 'performance':
                self.fps_var.set("20")
                self.quality_var.set("30")
        
        self.profile_var.trace('w', on_profile_change)

        # UI设置
        ui_frame = ttk.LabelFrame(self, text="界面设置", padding=(10, 5))
        ui_frame.pack(padx=10, pady=5, fill="x")
        
        self.show_fps_var = tk.BooleanVar(value=self.config.get('ui', {}).get('show_fps', True))
        ttk.Checkbutton(ui_frame, text="显示FPS", variable=self.show_fps_var).pack(anchor="w", padx=5, pady=2)
        
        self.show_status_var = tk.BooleanVar(value=self.config.get('ui', {}).get('show_connection_status', True))
        ttk.Checkbutton(ui_frame, text="显示连接状态", variable=self.show_status_var).pack(anchor="w", padx=5, pady=2)
        
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=self._on_ok).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=self._on_cancel).pack(side="left", padx=5)
        ttk.Button(button_frame, text="恢复默认", command=self._reset_defaults).pack(side="left", padx=5)
        
    def _validate_and_get_config(self):
        """验证输入并返回新配置"""
        try:
            new_config = {
                "network": {
                    "default_port": int(self.port_var.get()),
                    "fps": int(self.fps_var.get()),
                    "jpeg_quality": int(self.quality_var.get())
                },
                "viewer": {
                    "default_width": int(self.width_var.get()),
                    "default_height": int(self.height_var.get()),
                    "zoom_scale": float(self.zoom_var.get())
                },
                "ui": {
                    "show_fps": self.show_fps_var.get(),
                    "show_connection_status": self.show_status_var.get()
                },
                "performance": {
                    "profile": self.profile_var.get()
                }
            }
            
            # 验证范围
            if not (1 <= new_config['network']['default_port'] <= 65535):
                raise ValueError("端口号必须在1-65535之间")
            if not (1 <= new_config['network']['fps'] <= 120):
                raise ValueError("帧率必须在1-120之间")
            if not (1 <= new_config['network']['jpeg_quality'] <= 100):
                raise ValueError("JPEG质量必须在1-100之间")
            if not (100 <= new_config['viewer']['default_width'] <= 2000):
                raise ValueError("默认宽度必须在100-2000之间")
            if not (100 <= new_config['viewer']['default_height'] <= 2000):
                raise ValueError("默认高度必须在100-2000之间")
            if not (1.0 <= new_config['viewer']['zoom_scale'] <= 5.0):
                raise ValueError("缩放比例必须在1.0-5.0之间")
                
            return new_config
            
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return None
    
    def _on_ok(self):
        new_config = self._validate_and_get_config()
        if new_config:
            self.result = new_config
            self.destroy()
    
    def _on_cancel(self):
        self.destroy()
    
    def _reset_defaults(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复所有设置为默认值吗？"):
            self.port_var.set("17585")
            self.fps_var.set("15")  # 使用优化后的默认值
            self.quality_var.set("50")  # 使用优化后的默认值
            self.width_var.set("480")
            self.height_var.set("270")
            self.zoom_var.set("2.0")
            self.show_fps_var.set(True)
            self.show_status_var.set(True)
            self.profile_var.set("balanced")  # 新增性能档案默认值

def show_settings_dialog(parent, config):
    """显示设置对话框并返回新配置，如果用户取消则返回None"""
    dialog = SettingsDialog(parent, config)
    parent.wait_window(dialog)
    return dialog.result