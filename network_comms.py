import socket
import threading
import time
import struct
import json
from queue import Queue, Empty
from screen_capture import capture_screen, compress_image

# 优化版截图和压缩功能
try:
    from screen_capture_optimized import capture_screen_scaled, compress_image_fast
    OPTIMIZED_AVAILABLE = True
except ImportError:
    OPTIMIZED_AVAILABLE = False

try:
    from screen_capture_ultra import capture_and_compress_ultra_fast
    ULTRA_AVAILABLE = True
except ImportError:
    ULTRA_AVAILABLE = False

class NetworkManager:
    def __init__(self, host='0.0.0.0', port=55555):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.clients = {}  # K: (ip, port), V: socket
        self.peers = {} # K: peer_addr, V: (socket, thread)
        self.on_peer_connected = None
        self.on_peer_disconnected = None
        self.on_data_received = None
        
        # 优化：图像数据队列，分离截图和发送
        self.image_queue = Queue(maxsize=3)
        self.capture_thread = None
        self.send_thread = None
        
        # 性能统计
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        # Load configuration
        self.config = self._load_config()
        
        # 性能档案设置
        self.performance_profile = self.config.get("performance", {}).get("profile", "balanced")
        print(f"网络管理器初始化，性能档案: {self.performance_profile}")

    def _load_config(self):
        """加载配置文件"""
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 智能性能提示
                if config['network']['fps'] > 20:
                    print("⚠️  检测到高FPS设置，建议使用高性能模式以获得最佳体验")
                if config['network']['jpeg_quality'] > 60:
                    print("⚠️  检测到高质量设置，建议降低到60以下以提升性能")
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "network": {"default_port": 55555, "fps": 15, "jpeg_quality": 50},
                "viewer": {"default_width": 480, "default_height": 270, "zoom_scale": 1.5},
                "performance": {"profile": "balanced"}
            }

    def start_server(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 优化：允许端口重用
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # 启动各个优化线程
        server_thread = threading.Thread(target=self._server_loop, daemon=True)
        server_thread.start()
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.send_thread.start()
        
        print(f"[*] 优化服务已启动，监听于 {self.host}:{self.port}")
        print(f"[*] 性能档案: {self.performance_profile}, 目标FPS: {self.config['network']['fps']}")

    def _server_loop(self):
        """接受客户端连接的循环"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                # 优化：设置TCP_NODELAY减少延迟
                client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                print(f"[+] 新的连接来自: {addr}")
                self.clients[addr] = client_socket
            except OSError:
                break # Socket was closed
        print("服务器循环已停止.")
        
    def _capture_loop(self):
        """专门负责截图和压缩的线程"""
        
        while self.running:
            frame_start = time.time()
            
            # 实时读取当前配置（支持动态切换）
            fps = self.config['network']['fps']
            jpeg_quality = self.config['network']['jpeg_quality']
            target_frame_time = 1.0 / max(1, fps)
            
            try:
                # 根据性能档案选择截图和压缩方法
                img_bytes = self._capture_and_compress_by_profile(jpeg_quality)
                
                if img_bytes:
                    try:
                        self.image_queue.put_nowait(img_bytes)
                    except:
                        # 队列满了，跳过这一帧以防止堆积
                        pass
                        
            except Exception as e:
                print(f"截图时发生错误: {e}")
            
            # 精确的帧率控制
            frame_time = time.time() - frame_start
            sleep_time = max(0, target_frame_time - frame_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _send_loop(self):
        """专门负责发送数据的线程"""
        while self.running:
            try:
                # 从队列获取图像数据，超时0.1秒
                img_bytes = self.image_queue.get(timeout=0.1)
                
                # 更新FPS统计
                self._update_fps_stats()
                
                # 构造消息
                message = struct.pack('>Q', len(img_bytes)) + img_bytes
                
                # 并发发送给所有客户端
                disconnected_clients = []
                send_threads = []
                
                for addr, client in list(self.clients.items()):
                    # 创建单独的发送线程，避免单个客户端阻塞整体
                    thread = threading.Thread(
                        target=self._send_to_client, 
                        args=(client, message, addr, disconnected_clients),
                        daemon=True
                    )
                    send_threads.append(thread)
                    thread.start()
                
                # 等待所有发送完成（设置超时）
                for thread in send_threads:
                    thread.join(timeout=0.05)  # 50ms超时
                
                # 清理断开的客户端
                for addr in disconnected_clients:
                    if addr in self.clients:
                        self.clients[addr].close()
                        del self.clients[addr]
                        
            except Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                print(f"发送时发生错误: {e}")

    def _capture_and_compress_by_profile(self, quality):
        """根据性能档案选择截图和压缩方法"""
        profile = self.performance_profile
        
        try:
            if profile == "performance" and ULTRA_AVAILABLE:
                # 高性能模式：使用超高速一体化方法
                return capture_and_compress_ultra_fast(quality=quality)
            elif profile == "balanced" and OPTIMIZED_AVAILABLE:
                # 平衡模式：使用优化版本
                img = capture_screen_scaled()
                return compress_image_fast(img, quality=quality)
            else:
                # 高质量模式或回退：使用原始方法
                sct_img = capture_screen()
                return compress_image(sct_img, quality=quality)
        except Exception as e:
            print(f"[ERROR] 截图失败，回退到原始模式: {e}")
            # 发生错误时回退到原始方法
            sct_img = capture_screen()
            return compress_image(sct_img, quality=quality)

    def _send_to_client(self, client, message, addr, disconnected_list):
        """向单个客户端发送数据"""
        try:
            client.sendall(message)
        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"[-] 客户端 {addr} 断开连接")
            disconnected_list.append(addr)

    def _update_fps_stats(self):
        """更新FPS统计"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:  # 每秒更新一次
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time

    def connect_to_peer(self, peer_host, peer_port):
        if (peer_host, peer_port) in self.peers:
            print(f"已经连接到 {peer_host}:{peer_port}")
            return True

        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 优化：设置连接超时和TCP_NODELAY
            peer_socket.settimeout(10)
            peer_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            peer_socket.connect((peer_host, peer_port))
            peer_socket.settimeout(None)
            
            thread = threading.Thread(target=self._peer_receive_loop, args=(peer_socket, (peer_host, peer_port)), daemon=True)
            thread.start()
            
            self.peers[(peer_host, peer_port)] = (peer_socket, thread)
            print(f"[*] 成功连接到 {peer_host}:{peer_port}")
            if self.on_peer_connected:
                self.on_peer_connected((peer_host, peer_port))
            return True
        except Exception as e:
            print(f"[!] 连接到 {peer_host}:{peer_port} 失败: {e}")
            return False

    def _peer_receive_loop(self, peer_socket, addr):
        """优化的数据接收循环"""
        payload_size = struct.calcsize(">Q")
        data_buffer = b""
        
        # 优化：设置接收缓冲区大小
        peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

        while self.running:
            try:
                # 接收长度头
                while len(data_buffer) < payload_size:
                    packet = peer_socket.recv(8192)  # 增大接收缓冲区
                    if not packet:
                        raise ConnectionResetError("远程主机关闭连接")
                    data_buffer += packet
                
                packed_msg_size = data_buffer[:payload_size]
                data_buffer = data_buffer[payload_size:]
                msg_size = struct.unpack(">Q", packed_msg_size)[0]

                # 接收图像数据
                while len(data_buffer) < msg_size:
                    remaining = msg_size - len(data_buffer)
                    chunk_size = min(8192, remaining)  # 分块接收
                    packet = peer_socket.recv(chunk_size)
                    if not packet:
                        raise ConnectionResetError("远程主机关闭连接")
                    data_buffer += packet

                frame_data = data_buffer[:msg_size]
                data_buffer = data_buffer[msg_size:]
                
                if self.on_data_received:
                    self.on_data_received(addr, frame_data)

            except (ConnectionResetError, OSError):
                print(f"[-] 来自 {addr} 的连接已断开.")
                self.disconnect_from_peer(addr[0], addr[1])
                break
        print(f"接收循环停止 for {addr}.")

    def disconnect_from_peer(self, peer_host, peer_port):
        addr = (peer_host, peer_port)
        if addr in self.peers:
            peer_socket, _ = self.peers[addr]
            peer_socket.close()
            del self.peers[addr]
            print(f"[*] 已从 {addr} 断开连接.")
            if self.on_peer_disconnected:
                self.on_peer_disconnected(addr)

    def stop(self):
        print("正在停止网络服务...")
        self.running = False
        
        # Close server socket to unblock accept()
        if self.server_socket:
            self.server_socket.close()
            
        # Close all client connections
        for client in self.clients.values():
            client.close()
        self.clients.clear()
        
        # Close all peer connections
        for peer_socket, _ in self.peers.values():
            peer_socket.close()
        self.peers.clear()

        print("网络服务已停止。")

    # 新增的性能管理方法
    def get_current_fps(self):
        """获取当前实际FPS"""
        return self.current_fps
    
    def get_performance_info(self):
        """获取性能信息"""
        target_fps = self.config['network']['fps']
        return {
            "current_fps": self.current_fps,
            "target_fps": target_fps,
            "profile": self.performance_profile,
            "efficiency": (self.current_fps / target_fps) if target_fps > 0 else 0,
            "queue_size": self.image_queue.qsize()
        }
    
    def switch_performance_profile(self, profile):
        """切换性能档案"""
        valid_profiles = ["quality", "balanced", "performance"]
        if profile in valid_profiles:
            old_profile = self.performance_profile
            self.performance_profile = profile
            
            # 更新配置文件中的性能档案
            self.config["performance"] = self.config.get("performance", {})
            self.config["performance"]["profile"] = profile
            
            # 根据性能档案更新网络参数
            if profile == "performance":
                self.config["network"]["fps"] = 20
                self.config["network"]["jpeg_quality"] = 30
            elif profile == "balanced":
                self.config["network"]["fps"] = 15
                self.config["network"]["jpeg_quality"] = 50
            elif profile == "quality":
                self.config["network"]["fps"] = 8
                self.config["network"]["jpeg_quality"] = 75
            
            try:
                import os
                config_path = os.path.join(os.path.dirname(__file__), 'config.json')
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                print(f"✅ 性能档案已从 {old_profile} 切换为: {profile}")
                print(f"✅ 已更新FPS: {self.config['network']['fps']}, 质量: {self.config['network']['jpeg_quality']}")
                return True
            except Exception as e:
                print(f"❌ 保存配置失败: {e}")
                return False
        else:
            print(f"❌ 无效的性能档案: {profile}")
            return False
    
    def reload_config(self):
        """重新加载配置文件"""
        try:
            self.config = self._load_config()
            old_profile = self.performance_profile
            self.performance_profile = self.config.get("performance", {}).get("profile", "balanced")
            print(f"✅ 配置已重新加载，性能档案: {old_profile} → {self.performance_profile}")
            return True
        except Exception as e:
            print(f"❌ 重新加载配置失败: {e}")
            return False

if __name__ == '__main__':
    # This is a test case.
    # To test this, you need to run two instances of this script.
    # One will act as a server, and you can connect to it from the other.
    
    manager1 = NetworkManager(port=55555)
    manager1.start_server()

    # In a real app, you would get this from user input.
    connect_to = input("输入要连接的IP地址 (留空则仅作为服务端): ")
    if connect_to:
        manager2 = NetworkManager(port=55556) # Use a different port for the second instance's server
        manager2.start_server()
        
        def display_data(addr, data):
            print(f"从 {addr} 接收到 {len(data)} 字节的数据")
        
        manager2.on_data_received = display_data
        manager2.connect_to_peer(connect_to, 55555)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n检测到用户中断，正在关闭...")
        manager1.stop()
        if 'manager2' in locals():
            manager2.stop()
        print("已关闭。")
