import socket
import threading
import time
import struct
import json
from screen_capture import capture_screen, compress_image

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
        
        # Load configuration
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "network": {"default_port": 55555, "fps": 30, "jpeg_quality": 75},
                "viewer": {"default_width": 480, "default_height": 270, "zoom_scale": 1.5}
            }

    def start_server(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        server_thread = threading.Thread(target=self._server_loop, daemon=True)
        server_thread.start()
        
        broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        broadcast_thread.start()
        print(f"[*] 服务已启动，监听于 {self.host}:{self.port}")

    def _server_loop(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"[+] 新的连接来自: {addr}")
                self.clients[addr] = client_socket
            except OSError:
                break # Socket was closed
        print("服务器循环已停止.")
        
    def _broadcast_loop(self):
        while self.running:
            fps = self.config['network']['fps']
            jpeg_quality = self.config['network']['jpeg_quality']
            frame_delay = 1.0 / max(1, fps)
            try:
                sct_img = capture_screen()
                img_bytes = compress_image(sct_img, quality=jpeg_quality)
                
                if not img_bytes:
                    continue

                message = struct.pack('>Q', len(img_bytes)) + img_bytes
                
                disconnected_clients = []
                for addr, client in list(self.clients.items()):
                    try:
                        client.sendall(message)
                    except (ConnectionResetError, BrokenPipeError):
                        print(f"[-] 客户端 {addr} 断开连接 (发送时发现).")
                        disconnected_clients.append(addr)

                for addr in disconnected_clients:
                    self.clients[addr].close()
                    del self.clients[addr]
                    
            except Exception as e:
                print(f"广播时发生错误: {e}")
                
            time.sleep(frame_delay)

    def connect_to_peer(self, peer_host, peer_port):
        if (peer_host, peer_port) in self.peers:
            print(f"已经连接到 {peer_host}:{peer_port}")
            return True

        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(10)  # 10秒连接超时
            peer_socket.connect((peer_host, peer_port))
            peer_socket.settimeout(None)  # 连接后移除超时
            
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
        payload_size = struct.calcsize(">Q")
        data_buffer = b""

        while self.running:
            try:
                while len(data_buffer) < payload_size:
                    packet = peer_socket.recv(4096)
                    if not packet:
                        raise ConnectionResetError("远程主机关闭连接")
                    data_buffer += packet
                
                packed_msg_size = data_buffer[:payload_size]
                data_buffer = data_buffer[payload_size:]
                msg_size = struct.unpack(">Q", packed_msg_size)[0]

                while len(data_buffer) < msg_size:
                    packet = peer_socket.recv(4096)
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
