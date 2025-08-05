import mss
import mss.tools
from PIL import Image
import io

class OptimizedScreenCapture:
    def __init__(self):
        # 重用mss实例以减少初始化开销
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
        # 可选的分辨率缩放以提升性能
        self.scale_factor = 0.75  # 缩放到75%以提升性能
        self.target_width = int(self.monitor['width'] * self.scale_factor)
        self.target_height = int(self.monitor['height'] * self.scale_factor)
        
    def capture_screen(self):
        """优化的屏幕捕获"""
        return self.sct.grab(self.monitor)
    
    def capture_screen_scaled(self):
        """捕获并直接缩放屏幕以减少后续处理负担"""
        sct_img = self.sct.grab(self.monitor)
        
        # 如果需要缩放，直接在截图时处理
        if self.scale_factor != 1.0:
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img_resized = img.resize((self.target_width, self.target_height), Image.LANCZOS)
            return img_resized
        else:
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    
    def compress_image_fast(self, img_or_sct, quality=50):
        """快速图像压缩，移除一些慢速优化"""
        try:
            if hasattr(img_or_sct, 'bgra'):  # 这是mss截图对象
                img = Image.frombytes("RGB", img_or_sct.size, img_or_sct.bgra, "raw", "BGRX")
            else:  # 这是PIL Image对象
                img = img_or_sct
                
            # 创建内存中的字节流IO对象
            img_byte_arr = io.BytesIO()
            
            # 移除optimize=True以提升速度，降低质量以减少数据量
            img.save(img_byte_arr, format='JPEG', quality=quality, optimize=False)
            
            return img_byte_arr.getvalue()
        except Exception as e:
            print(f"快速图像压缩失败: {e}")
            return None
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'sct'):
            self.sct.close()

# 全局实例，避免重复创建
_capture_instance = None

def get_capture_instance():
    """获取全局截图实例"""
    global _capture_instance
    if _capture_instance is None:
        _capture_instance = OptimizedScreenCapture()
    return _capture_instance

def capture_screen_fast():
    """快速截图接口"""
    return get_capture_instance().capture_screen()

def capture_screen_scaled():
    """缩放截图接口"""
    return get_capture_instance().capture_screen_scaled()

def compress_image_fast(img_or_sct, quality=50):
    """快速压缩接口"""
    return get_capture_instance().compress_image_fast(img_or_sct, quality)

# 兼容性接口，用于替换原有函数
def capture_screen():
    """兼容原版的截图函数"""
    return capture_screen_fast()

def compress_image(sct_img, quality=50):
    """兼容原版的压缩函数，但默认使用更低质量"""
    return compress_image_fast(sct_img, quality)