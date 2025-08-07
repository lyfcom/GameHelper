import tkinter as tk
from PIL import Image, ImageTk
import io
import time

class ViewerWindow(tk.Toplevel):
    def __init__(self, master, peer_addr, default_size=(480, 270), zoom_scale=1.5, show_fps=True):
        super().__init__(master)
        
        self.peer_addr = peer_addr
        self.default_size = default_size
        self.zoom_scale = zoom_scale
        self.is_zoomed = False
        self.show_fps = show_fps

        # FPS tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0

        # --- Window Configuration ---
        self.title(f"来自 {self.peer_addr} 的屏幕")
        self.geometry(f"{default_size[0]}x{default_size[1]}+0+0") # Default size and top-left position
        self.overrideredirect(True)  # 无边框窗口
        self.attributes("-topmost", True)  # 窗口置顶

        # --- UI Elements ---
        # Main container frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(fill="both", expand=True)
        
        # FPS label (if enabled)
        if self.show_fps:
            self.fps_label = tk.Label(self.main_frame, text="FPS: 0", 
                                    fg="yellow", bg="black", font=("Arial", 8, "bold"))
            self.fps_label.place(x=5, y=5)  # 左上角显示
        
        self.last_image = None # Store the last raw PIL image for resizing

        # --- Drag and Drop ---
        self._offset_x = 0
        self._offset_y = 0
        self.bind("<ButtonPress-1>", self._on_mouse_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<Double-Button-1>", self._on_mouse_double_click)
        # --- Zoom on Hover ---
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_mouse_press(self, event):
        """记录鼠标按下的初始位置，用于计算窗口拖动的偏移量。"""
        self._offset_x = event.x
        self._offset_y = event.y

    def _on_mouse_drag(self, event):
        """根据鼠标的移动来更新窗口的位置。"""
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def _on_mouse_double_click(self, event):
        """双击鼠标时，回到0,0位置。"""
        self.geometry(f"+0+0")

    def _on_enter(self, event):
        """当鼠标进入窗口时，放大窗口和图像。"""
        if not self.is_zoomed:
            self.is_zoomed = True
            self.zoom()

    def _on_leave(self, event):
        """当鼠标离开窗口时，恢复原始大小。"""
        if self.is_zoomed:
            self.is_zoomed = False
            self.unzoom()
            
    def _resize_and_update_image(self, target_size):
        """内部方法：根据目标尺寸缩放并更新显示的图像。"""
        if self.last_image:
            try:
                resized_pil_img = self.last_image.resize(target_size, Image.Resampling.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(resized_pil_img)
                self.image_label.config(image=self.tk_image)
                self.image_label.image = self.tk_image  # Keep reference
            except Exception as e:
                print(f"图像缩放失败: {e}")
            
    def zoom(self):
        """执行放大操作。"""
        if self.last_image is None:
            return  # 尚未收到图像时不执行缩放
        zoomed_w = int(self.default_size[0] * self.zoom_scale)
        zoomed_h = int(self.default_size[1] * self.zoom_scale)
        self.geometry(f"{zoomed_w}x{zoomed_h}")
        self._resize_and_update_image((zoomed_w, zoomed_h))
        
    def unzoom(self):
        """执行缩小（复原）操作。"""
        self.geometry(f"{self.default_size[0]}x{self.default_size[1]}")
        self._resize_and_update_image(self.default_size)

    def update_image(self, image_bytes):
        """
        公共方法：接收原始图像字节流，解码并更新到窗口中。
        这应该是从外部（如网络线程）调用的主要方法。
        """
        try:
            image_stream = io.BytesIO(image_bytes)
            self.last_image = Image.open(image_stream)
            
            # 根据当前是否缩放来决定显示尺寸
            if self.is_zoomed:
                target_size = (int(self.default_size[0] * self.zoom_scale), int(self.default_size[1] * self.zoom_scale))
            else:
                target_size = self.default_size
                
            self._resize_and_update_image(target_size)
            
            # 更新FPS计算
            if self.show_fps:
                self._update_fps()
            
        except Exception as e:
            # 在实际应用中，这里可能需要一个更优雅的处理，比如显示一个"信号丢失"的图像
            print(f"更新图像失败: {e}")
            self.last_image = None
    
    def _update_fps(self):
        """更新FPS显示 - 优化版本减少time.time()调用"""
        self.frame_count += 1
        
        # 每30帧才检查一次时间，减少系统调用开销
        if self.frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - self.fps_start_time
            
            if elapsed >= 1.0:  # 每秒更新一次FPS显示
                self.current_fps = self.frame_count / elapsed
                self.fps_label.config(text=f"FPS: {self.current_fps:.1f}")
                self.frame_count = 0
                self.fps_start_time = current_time
    
    def close_window(self):
        """关闭窗口。"""
        self.destroy()

if __name__ == '__main__':
    # --- 测试代码 ---
    # 直接运行此文件可以测试窗口的拖动、缩放等交互功能。
    
    root = tk.Tk()
    root.title("主控制器 (测试模式)")
    root.geometry("300x200")

    test_addr = ('127.0.0.1', 12345)
    
    # 创建一个假的黑色图像用于测试
    dummy_image_data = None
    try:
        black_img = Image.new('RGB', (1920, 1080), 'black')
        byte_arr = io.BytesIO()
        black_img.save(byte_arr, format='JPEG')
        dummy_image_data = byte_arr.getvalue()
    except Exception as e:
        print(f"创建测试图像失败: {e}")

    viewer = ViewerWindow(root, peer_addr=test_addr)
    
    if dummy_image_data:
        # 模拟接收到网络数据
        viewer.update_image(dummy_image_data)

    def close_all():
        viewer.close_window()
        root.destroy()

    close_button = tk.Button(root, text="关闭所有", command=close_all)
    close_button.pack(pady=20)
    
    root.mainloop()
    