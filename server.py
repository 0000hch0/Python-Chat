import socket
import threading
import time
import os
from datetime import datetime

class ChatServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        
        self.clients = {}
        self.nicknames = {}
        self.file_transfers = {}
        self.lock = threading.Lock()  # 添加线程锁
        
        print(f"服务器已启动，监听 {self.host}:{self.port}")
    
    def safe_send(self, client, message):
        """安全发送消息，避免异常"""
        try:
            client.send(message.encode('utf-8'))
            return True
        except (ConnectionResetError, BrokenPipeError, OSError):
            return False
        except Exception as e:
            print(f"发送消息时发生意外错误: {e}")
            return False
    
    def broadcast(self, message, sender=None):
        """广播消息给所有客户端"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{current_time}] {message}"
        
        # 在服务器控制台显示消息
        print(formatted_message)
        
        # 使用线程锁确保线程安全
        with self.lock:
            # 创建客户端副本避免迭代时修改
            clients_copy = list(self.clients.keys())
            
            for client in clients_copy:
                if client != sender:  # 不发送给消息来源的客户端
                    if not self.safe_send(client, formatted_message):
                        # 发送失败，移除客户端
                        self.remove_client(client)
    
    def remove_client(self, client):
        """安全移除客户端"""
        if client not in self.clients:
            return
            
        nickname = self.nicknames.get(client, "Unknown")
        print(f"正在移除客户端: {nickname}")
        
        # 先关闭socket避免进一步错误
        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except:
            pass
        
        # 使用线程锁确保线程安全
        with self.lock:
            # 从数据结构中移除
            if client in self.clients:
                del self.clients[client]
            if client in self.nicknames:
                del self.nicknames[client]
            if client in self.file_transfers:
                del self.file_transfers[client]
        
        # 广播离开消息（但不通过该客户端）
        try:
            self.broadcast(f"{nickname} 离开了聊天室")
        except Exception as e:
            print(f"广播离开消息时出错: {e}")
    
    def handle_client(self, client):
        """处理单个客户端连接"""
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    # 客户端正常断开连接
                    print(f"客户端 {self.clients[client]} 断开连接")
                    self.remove_client(client)
                    break
                
                if message.startswith("NICKNAME:"):
                    nickname = message.split(":")[1]
                    with self.lock:
                        self.nicknames[client] = nickname
                    self.broadcast(f"{nickname} 加入了聊天室!")
                
                elif message.startswith("FILE_TRANSFER_REQUEST:"):
                    parts = message.split(":")
                    if len(parts) >= 4:
                        filename = parts[1]
                        filesize = int(parts[2])
                        sender_nickname = parts[3]
                        with self.lock:
                            self.file_transfers[client] = {
                                'filename': filename,
                                'filesize': filesize,
                                'received': 0,
                                'data': b''
                            }
                        self.broadcast(f"{sender_nickname} 正在发送文件: {filename} ({filesize} bytes)")
                        if not self.safe_send(client, "FILE_TRANSFER_READY"):
                            self.remove_client(client)
                
                elif message == "FILE_TRANSFER_START":
                    file_info = None
                    with self.lock:
                        file_info = self.file_transfers.get(client)
                    
                    if file_info:
                        try:
                            while file_info['received'] < file_info['filesize']:
                                data = client.recv(4096)
                                if not data:
                                    break
                                file_info['data'] += data
                                file_info['received'] += len(data)
                            
                            sender_nickname = self.nicknames.get(client, "Unknown")
                            self.broadcast(f"{sender_nickname} 发送了文件: {file_info['filename']}", sender=client)
                            
                            os.makedirs("server_files", exist_ok=True)
                            filepath = os.path.join("server_files", file_info['filename'])
                            with open(filepath, 'wb') as f:
                                f.write(file_info['data'])
                            
                            # 通知其他客户端准备接收文件
                            with self.lock:
                                clients_copy = list(self.clients.keys())
                            
                            for c in clients_copy:
                                if c != client:
                                    if not self.safe_send(c, f"FILE_INCOMING:{file_info['filename']}:{file_info['filesize']}:{sender_nickname}"):
                                        self.remove_client(c)
                        except Exception as e:
                            print(f"文件传输过程中出错: {e}")
                            self.remove_client(client)
                
                else:
                    nickname = self.nicknames.get(client, "Unknown")
                    self.broadcast(f"{nickname}: {message}")
            
            except (ConnectionResetError, ConnectionAbortedError):
                print(f"客户端 {self.clients.get(client, '未知地址')} 异常断开")
                self.remove_client(client)
                break
            except Exception as e:
                print(f"处理客户端消息时出错: {e}")
                self.remove_client(client)
                break
    
    def start(self):
        """启动服务器"""
        try:
            while True:
                client, address = self.server.accept()
                print(f"新的连接来自 {address}")
                
                try:
                    if not self.safe_send(client, "NICK"):
                        client.close()
                        continue
                except Exception as e:
                    print(f"无法发送昵称请求: {e}")
                    client.close()
                    continue
                
                with self.lock:
                    self.clients[client] = address
                
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.daemon = True
                thread.start()
        
        except KeyboardInterrupt:
            print("\n服务器正在关闭...")
            with self.lock:
                clients_copy = list(self.clients.keys())
            
            for client in clients_copy:
                self.remove_client(client)
            
            self.server.close()
            print("服务器已关闭")
        except Exception as e:
            print(f"服务器异常: {e}")

if __name__ == "__main__":
    server = ChatServer()
    server.start()