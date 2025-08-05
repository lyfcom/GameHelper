import mss
from PIL import Image
import io
import time

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class UltraFastScreenCapture:
    def __init__(self):
        # 重用mss实例
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
        # 极度激进的性能优化设置
        self.scale_factor = 0.5  # 50%缩放 -> 960x540
        self.target_width = int(self.monitor['width'] * self.scale_factor)
        self.target_height = int(self.monitor['height'] * self.scale_factor)
        
        # 区域采样优化
        self.sample_rate = 2  # 每2个像素采样1个
        
        # 预分配缓冲区
        self.img_buffer = io.BytesIO()
        
        print(f"初始化超高速截图，目标分辨率: {self.target_width}x{self.target_height}")
    
    def capture_and_compress_ultra_fast(self, quality=30):
        """超快速截图+压缩一体化"""
        try:
            # 1. 快速截图
            sct_img = self.sct.grab(self.monitor)
            
            if NUMPY_AVAILABLE:
                # 2. 直接从原始数据创建numpy数组（跳过PIL中间步骤）
                raw_data = np.frombuffer(sct_img.bgra, dtype=np.uint8)
                raw_data = raw_data.reshape((sct_img.height, sct_img.width, 4))
                
                # 3. 快速采样和缩放（跳过部分像素）
                sampled_bgr = raw_data[::self.sample_rate, ::self.sample_rate, :3]  # 取BGR通道
                
                # 4. 修复颜色通道顺序：BGR → RGB
                sampled_rgb = sampled_bgr[:, :, [2, 1, 0]]  # 交换蓝色和红色通道
                
                # 5. 转换为PIL Image进行快速压缩
                img = Image.fromarray(sampled_rgb, 'RGB')
            else:
                # 回退到PIL方法
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                # 采样缩放
                sampled_size = (sct_img.width // self.sample_rate, sct_img.height // self.sample_rate)
                img = img.resize(sampled_size, Image.NEAREST)
            
            # 6. 再次缩放到目标大小
            if img.size != (self.target_width, self.target_height):
                img = img.resize((self.target_width, self.target_height), Image.NEAREST)  # 使用最快的缩放算法
            
            # 7. 重用缓冲区压缩
            self.img_buffer.seek(0)
            self.img_buffer.truncate(0)
            img.save(self.img_buffer, format='JPEG', quality=quality, optimize=False)
            
            return self.img_buffer.getvalue()
            
        except Exception as e:
            print(f"超快速压缩失败: {e}")
            return None

# 全局实例
_ultra_capture = None

def get_ultra_capture():
    global _ultra_capture
    if _ultra_capture is None:
        _ultra_capture = UltraFastScreenCapture()
    return _ultra_capture

def capture_and_compress_ultra_fast(quality=30):
    """超快速一体化接口"""
    return get_ultra_capture().capture_and_compress_ultra_fast(quality)