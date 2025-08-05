import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import socket
import threading
import json
from network_comms import NetworkManager
from viewer_window import ViewerWindow
from settings_dialog import show_settings_dialog
from queue import Queue

class ControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("P2P 屏幕共享控制面板")
        self.geometry("400x600")

        # --- Load Configuration ---
        self.config = self.load_config()

        # --- Data Structures ---
        self.viewer_windows = {}  # K: peer_addr, V: ViewerWindow instance
        self.data_queues = {}     # K: peer_addr, V: Queue for image data
        
        # --- Network Setup ---
        self.network_manager = NetworkManager(port=self.config['network']['default_port'])
        self.network_manager.on_peer_connected = self.on_peer_connected
        self.network_manager.on_peer_disconnected = self.on_peer_disconnected
        self.network_manager.on_data_received = self.on_data_received
        self.network_manager.start_server()

        # --- UI Initialization ---
        self._create_widgets()
        
        # --- Graceful Shutdown ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_config(self):
        """加载配置文件，如果失败则使用默认值。"""
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("配置文件 'config.json' 未找到或格式错误，将使用默认配置。")
            return {
                "network": {
                    "default_port": 17585,
                    "fps": 8,
                    "jpeg_quality": 75
                },
                "viewer": {
                    "default_width": 480,
                    "default_height": 270,
                    "zoom_scale": 2.0
                },
                "ui": {
                    "show_fps": True,
                    "show_connection_status": True
                }
            }

    def _create_widgets(self):
        # Frame for local info
        info_frame = ttk.LabelFrame(self, text="我的信息", padding=(10, 5))
        info_frame.pack(padx=10, pady=5, fill="x")

        # 收集本机所有 IPv4 地址
        def _list_local_ips():
            ips = set()
            try:
                for info in socket.getaddrinfo(socket.gethostname(), None):
                    if info[0] == socket.AF_INET:
                        ip = info[4][0]
                        if not ip.startswith("127."):
                            ips.add(ip)
            except Exception:
                pass
            # 尝试通过 UDP socket 获取默认出口 IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ips.add(s.getsockname()[0])
                s.close()
            except Exception:
                pass
            if not ips:
                ips.add("127.0.0.1")
            return sorted(ips)
        local_ips = _list_local_ips()
        ttk.Label(info_frame, text="本机 IP:").pack(side="left", padx=5)
        self.ip_entry = ttk.Entry(info_frame)
        self.ip_entry.insert(0, ", ".join(local_ips))
        self.ip_entry.config(state="readonly")
        self.ip_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Label(info_frame, text=f"端口: {self.network_manager.port}").pack(side="left", padx=5)

        # Frame for connecting to peers
        connect_frame = ttk.LabelFrame(self, text="连接到同伴", padding=(10, 5))
        connect_frame.pack(padx=10, pady=5, fill="x")
        
        # IP input row
        ip_row = ttk.Frame(connect_frame)
        ip_row.pack(fill="x", pady=2)
        ttk.Label(ip_row, text="IP:").pack(side="left", padx=5)
        self.peer_ip_entry = ttk.Entry(ip_row)
        self.peer_ip_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Port input row
        port_row = ttk.Frame(connect_frame)
        port_row.pack(fill="x", pady=2)
        ttk.Label(port_row, text="端口:").pack(side="left", padx=5)
        self.peer_port_entry = ttk.Entry(port_row, width=10)
        self.peer_port_entry.insert(0, str(self.config['network']['default_port']))
        self.peer_port_entry.pack(side="left", padx=5)
        
        self.connect_button = ttk.Button(port_row, text="连接", command=self.connect_to_peer)
        self.connect_button.pack(side="left", padx=5)
        
        # Frame for connected peers list
        list_frame = ttk.LabelFrame(self, text="当前连接", padding=(10, 5))
        list_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.peer_list = tk.Listbox(list_frame)
        self.peer_list.pack(side="left", fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.peer_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.peer_list.config(yscrollcommand=scrollbar.set)
        
        self.disconnect_button = ttk.Button(self, text="断开选中连接", command=self.disconnect_peer)
        self.disconnect_button.pack(pady=5)
        
        # 性能监控区域
        performance_frame = ttk.LabelFrame(self, text="性能监控", padding=(10, 5))
        performance_frame.pack(padx=10, pady=5, fill="x")
        
        # 性能信息显示
        perf_info_frame = ttk.Frame(performance_frame)
        perf_info_frame.pack(fill="x")
        
        ttk.Label(perf_info_frame, text="实际FPS:").pack(side="left", padx=5)
        self.fps_label = ttk.Label(perf_info_frame, text="0.0", foreground="blue", font=("Arial", 10, "bold"))
        self.fps_label.pack(side="left", padx=5)
        
        ttk.Label(perf_info_frame, text="档案:").pack(side="left", padx=10)
        self.profile_label = ttk.Label(perf_info_frame, text="balanced", foreground="green")
        self.profile_label.pack(side="left", padx=5)
        
        ttk.Label(perf_info_frame, text="效率:").pack(side="left", padx=10)
        self.efficiency_label = ttk.Label(perf_info_frame, text="0%", foreground="orange")
        self.efficiency_label.pack(side="left", padx=5)
        
        # 性能控制按钮
        perf_control_frame = ttk.Frame(performance_frame)
        perf_control_frame.pack(fill="x", pady=5)
        
        ttk.Button(perf_control_frame, text="高质量", command=lambda: self.switch_profile("quality")).pack(side="left", padx=2)
        ttk.Button(perf_control_frame, text="平衡", command=lambda: self.switch_profile("balanced")).pack(side="left", padx=2)
        ttk.Button(perf_control_frame, text="高性能", command=lambda: self.switch_profile("performance")).pack(side="left", padx=2)

        # 底部按钮区域
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(pady=5)
        
        ttk.Button(bottom_frame, text="设置", command=self.show_settings).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="保存配置", command=self.save_config).pack(side="left", padx=5)
        
        # 启动性能监控
        self._start_performance_monitoring()
        
    def connect_to_peer(self):
        peer_ip = self.peer_ip_entry.get().strip()
        peer_port_str = self.peer_port_entry.get().strip()
        
        if not peer_ip:
            messagebox.showerror("错误", "请输入有效的IP地址。")
            return
            
        try:
            peer_port = int(peer_port_str)
            if peer_port < 1 or peer_port > 65535:
                raise ValueError("端口号必须在1-65535之间")
        except ValueError as e:
            messagebox.showerror("错误", f"端口号无效: {e}")
            return
        
        addr = (peer_ip, peer_port)
        if addr in self.viewer_windows:
            messagebox.showinfo("提示", "已经连接到该地址。")
            return
            
        # 显示连接状态
        self.connect_button.config(text="连接中...", state="disabled")
        
        def connect_with_feedback():
            success = self.network_manager.connect_to_peer(peer_ip, peer_port)
            self.after(0, self._on_connect_result, success, addr)
            
        threading.Thread(target=connect_with_feedback, daemon=True).start()
        
    def _on_connect_result(self, success, addr):
        """处理连接结果的回调函数"""
        self.connect_button.config(text="连接", state="normal")
        
        if not success:
            messagebox.showerror("连接失败", f"无法连接到 {addr[0]}:{addr[1]}")
        
    def disconnect_peer(self):
        selected_indices = self.peer_list.curselection()
        if not selected_indices:
            messagebox.showerror("错误", "请先从列表中选择一个连接。")
            return
            
        selected_item = self.peer_list.get(selected_indices[0])
        peer_ip, peer_port_str = selected_item.split(":")
        peer_port = int(peer_port_str)
        
        self.network_manager.disconnect_from_peer(peer_ip, peer_port)
        
    def on_peer_connected(self, peer_addr):
        self.after(0, self._create_viewer_window, peer_addr)
        
    def on_peer_disconnected(self, peer_addr):
        self.after(0, self._destroy_viewer_window, peer_addr)
        
    def on_data_received(self, peer_addr, image_data):
        if peer_addr in self.data_queues:
            self.data_queues[peer_addr].put(image_data)
            
    def _create_viewer_window(self, peer_addr):
        if peer_addr not in self.viewer_windows:
            self.data_queues[peer_addr] = Queue()
            
            viewer_config = self.config['viewer']
            ui_config = self.config.get('ui', {})
            viewer = ViewerWindow(
                self, 
                peer_addr,
                default_size=(viewer_config['default_width'], viewer_config['default_height']),
                zoom_scale=viewer_config['zoom_scale'],
                show_fps=ui_config.get('show_fps', True)
            )
            self.viewer_windows[peer_addr] = viewer
            
            threading.Thread(target=self._update_viewer_loop, args=(viewer, self.data_queues[peer_addr]), daemon=True).start()
            
            self.peer_list.insert(tk.END, f"{peer_addr[0]}:{peer_addr[1]}")
            self.peer_ip_entry.delete(0, tk.END)

    def _destroy_viewer_window(self, peer_addr):
        if peer_addr in self.viewer_windows:
            viewer = self.viewer_windows.pop(peer_addr)
            viewer.close_window()
            
            if peer_addr in self.data_queues:
                del self.data_queues[peer_addr]

            items = list(self.peer_list.get(0, tk.END))
            for i, item in enumerate(items):
                if item == f"{peer_addr[0]}:{peer_addr[1]}":
                    self.peer_list.delete(i)
                    break
                    
    def _update_viewer_loop(self, viewer, queue):
        while viewer.winfo_exists():
            try:
                data = queue.get(timeout=1)
                viewer.update_image(data)
            except Exception:
                pass
        print(f"Update loop for {viewer.peer_addr} has ended.")

    def show_settings(self):
        """显示设置对话框"""
        new_config = show_settings_dialog(self, self.config)
        if new_config:
            # 保存新配置
            self.config = new_config
            
            # 立即保存到文件
            self.save_config(auto=True)
            
            # 通知网络管理器重新加载配置
            if self.network_manager.reload_config():
                print("[UI] 网络管理器配置已同步")
            
            # 更新端口输入框默认值
            self.peer_port_entry.delete(0, tk.END)
            self.peer_port_entry.insert(0, str(self.config['network']['default_port']))
            
            messagebox.showinfo("成功", "设置已保存并应用！性能档案和网络参数已立即生效。")
    
    def save_config(self, auto=False):
        """保存当前配置到文件
        auto=True 时为内部调用，不弹出成功提示，只在错误时提示
        """
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            if not auto:
                messagebox.showinfo("成功", "配置已保存到 config.json")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def _start_performance_monitoring(self):
        """启动性能监控"""
        def update_performance():
            try:
                perf_info = self.network_manager.get_performance_info()
                
                # 更新FPS显示
                self.fps_label.config(text=f"{perf_info['current_fps']:.1f}")
                
                # 更新档案显示
                profile_names = {
                    "quality": "高质量",
                    "balanced": "平衡", 
                    "performance": "高性能"
                }
                profile_display = profile_names.get(perf_info['profile'], perf_info['profile'])
                self.profile_label.config(text=profile_display)
                
                # 更新效率显示（根据效率设置颜色）
                efficiency = perf_info['efficiency']
                efficiency_text = f"{efficiency:.0%}"
                if efficiency >= 0.8:
                    color = "green"
                elif efficiency >= 0.6:
                    color = "orange"
                else:
                    color = "red"
                self.efficiency_label.config(text=efficiency_text, foreground=color)
                
            except Exception as e:
                print(f"性能监控更新失败: {e}")
            
            # 每2秒更新一次
            self.after(2000, update_performance)
        
        # 启动监控
        update_performance()
    
    def switch_profile(self, profile):
        """切换性能档案"""
        if self.network_manager.switch_performance_profile(profile):
            # 重新加载配置到本地
            self.config = self.load_config()
            
            # 显示成功消息
            profile_names = {
                "quality": "高质量模式",
                "balanced": "平衡模式", 
                "performance": "高性能模式"
            }
            messagebox.showinfo("成功", f"已切换到 {profile_names.get(profile, profile)}")
            print(f"[UI] 性能档案切换完成: {profile}")
        else:
            messagebox.showerror("错误", "性能档案切换失败")

    def on_closing(self):
        if messagebox.askokcancel("退出", "确定要关闭所有连接并退出程序吗？"):
            self.network_manager.stop()
            self.destroy()

if __name__ == '__main__':
    app = ControlPanel()
    app.mainloop()
