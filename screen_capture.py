import mss
import mss.tools
from PIL import Image
import io

def capture_screen():
    """
    捕获整个屏幕的截图。

    使用 mss.mss() 作为上下文管理器，可以确保即使发生错误也能正确清理资源。
    
    Returns:
        mss.screenshot.ScreenShot: 返回一个mss的截图对象，包含了屏幕的原始像素数据和尺寸信息。
    """
    with mss.mss() as sct:
        # 获取第一个监视器的截图
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return sct_img

def compress_image(sct_img, quality=75):
    """
    将mss截图对象压缩为JPEG格式的字节流。

    Args:
        sct_img (mss.screenshot.ScreenShot): mss捕获的截图对象。
        quality (int): JPEG的压缩质量，范围1-100，值越高质量越好，文件越大。

    Returns:
        bytes: 返回JPEG格式的图像字节流。如果发生错误则返回None。
    """
    try:
        # 从原始BGRA像素数据创建Pillow图像对象
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # 创建一个内存中的字节流IO对象
        img_byte_arr = io.BytesIO()
        
        # 将图像以JPEG格式保存到内存IO对象中
        # optimize=True 会尝试优化哈夫曼表，可能会稍微减小文件大小
        img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
        
        # 获取字节流的全部内容
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"图像压缩失败: {e}")
        return None

if __name__ == '__main__':
    # 这是一个简单的测试，当你直接运行这个脚本时会执行
    import time
    
    print("开始屏幕捕获与压缩测试...")
    start_time = time.time()
    
    # 1. 捕获屏幕
    screenshot = capture_screen()
    capture_time = time.time()
    print(f"捕获屏幕完成，耗时: {capture_time - start_time:.4f} 秒")
    print(f"图像尺寸: {screenshot.size}")

    # 2. 压缩图像
    compressed_data = compress_image(screenshot, quality=50)
    compress_time = time.time()
    print(f"压缩图像完成，耗时: {compress_time - capture_time:.4f} 秒")

    if compressed_data:
        original_size = len(screenshot.rgb)
        compressed_size = len(compressed_data)
        print(f"原始数据大小 (RGB): {original_size / 1024:.2f} KB")
        print(f"压缩后数据大小 (JPEG): {compressed_size / 1024:.2f} KB")
        print(f"压缩率: {original_size / compressed_size:.2f} : 1")

        # 3. (可选) 保存压缩后的图片以供验证
        try:
            with open("test_compressed_output.jpg", "wb") as f:
                f.write(compressed_data)
            print("已将压缩后的截图保存为 'test_compressed_output.jpg'")
        except Exception as e:
            print(f"保存测试文件失败: {e}")
    else:
        print("未能获取到压缩后的图像数据。")

    end_time = time.time()
    print(f"测试总耗时: {end_time - start_time:.4f} 秒")
