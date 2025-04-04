import socket
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from datetime import datetime
import os

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("局域网聊天工具")
        
        # 连接设置
        self.host = 'localhost'
        self.port = 12345
        self.nickname = "匿名用户"
        
        # 创建GUI
        self.create_connection_frame()
        self.create_chat_frame()
        self.create_input_frame()
        
        # 默认隐藏聊天界面
        self.chat_frame.pack_forget()
        self.input_frame.pack_forget()
        
        # 初始化socket
        self.client = None
        self.running = False
        
        # 文件传输相关
        self.current_file_transfer = None
        
        # 窗口关闭时处理
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """窗口关闭时的处理"""
        if self.client:
            try:
                self.client.close()
            except:
                pass
        self.running = False
        self.master.destroy()
    
    def create_connection_frame(self):
        """创建连接服务器的界面"""
        self.conn_frame = tk.Frame(self.master)
        self.conn_frame.pack(padx=20, pady=20)
        
        tk.Label(self.conn_frame, text="服务器地址:").grid(row=0, column=0, sticky='e')
        self.host_entry = tk.Entry(self.conn_frame)
        self.host_entry.insert(0, self.host)
        self.host_entry.grid(row=0, column=1)
        
        tk.Label(self.conn_frame, text="端口:").grid(row=1, column=0, sticky='e')
        self.port_entry = tk.Entry(self.conn_frame)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=1, column=1)
        
        tk.Label(self.conn_frame, text="昵称:").grid(row=2, column=0, sticky='e')
        self.nickname_entry = tk.Entry(self.conn_frame)
        self.nickname_entry.insert(0, self.nickname)
        self.nickname_entry.grid(row=2, column=1)
        
        self.connect_btn = tk.Button(self.conn_frame, text="连接", command=self.connect_to_server)
        self.connect_btn.grid(row=3, columnspan=2, pady=10)
    
    def create_chat_frame(self):
        """创建聊天显示区域"""
        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(fill=tk.BOTH, expand=True)
    
    def create_input_frame(self):
        """创建消息输入区域"""
        self.input_frame = tk.Frame(self.master)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.msg_entry = tk.Text(self.input_frame, height=3)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        button_frame = tk.Frame(self.input_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_btn = tk.Button(button_frame, text="发送", command=self.send_message)
        self.send_btn.pack(fill=tk.X)
        
        self.file_btn = tk.Button(button_frame, text="发送文件", command=self.send_file)
        self.file_btn.pack(fill=tk.X)
    
    def connect_to_server(self):
        """连接服务器"""
        self.host = self.host_entry.get()
        self.port = int(self.port_entry.get())
        self.nickname = self.nickname_entry.get()
        
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            
            # 发送昵称给服务器
            self.client.send(f"NICKNAME:{self.nickname}".encode('utf-8'))
            
            # 隐藏连接界面，显示聊天界面
            self.conn_frame.pack_forget()
            self.chat_frame.pack(fill=tk.BOTH, expand=True)
            self.input_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 启动接收消息的线程
            self.running = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
            if self.client:
                self.client.close()
    
    def receive_messages(self):
        """接收服务器消息"""
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                
                if not message:
                    # 服务器关闭或连接断开
                    self.display_message("与服务器的连接已断开")
                    break
                
                if message == "NICK":
                    self.client.send(f"NICKNAME:{self.nickname}".encode('utf-8'))
                
                elif message.startswith("FILE_INCOMING:"):
                    # 处理文件传输
                    parts = message.split(":")
                    if len(parts) >= 4:
                        filename = parts[1]
                        filesize = int(parts[2])
                        sender_nickname = parts[3]
                        
                        # 询问用户是否接收文件
                        if messagebox.askyesno("文件传输", f"{sender_nickname} 想发送文件 {filename} ({filesize} bytes). 是否接收?"):
                            # 准备接收文件
                            self.client.send("FILE_TRANSFER_ACCEPT".encode('utf-8'))
                            
                            # 创建目录保存文件
                            os.makedirs("received_files", exist_ok=True)
                            filepath = os.path.join("received_files", filename)
                            
                            # 接收文件数据
                            with open(filepath, 'wb') as f:
                                remaining = filesize
                                while remaining > 0 and self.running:
                                    try:
                                        data = self.client.recv(min(4096, remaining))
                                        if not data:
                                            break
                                        f.write(data)
                                        remaining -= len(data)
                                    except:
                                        break
                            
                            if remaining == 0:
                                self.display_message(f"文件 {filename} 已保存到 received_files 目录")
                            else:
                                self.display_message("文件接收被中断或未完成")
                        else:
                            self.client.send("FILE_TRANSFER_DECLINE".encode('utf-8'))
                
                elif message == "FILE_TRANSFER_READY":
                    # 服务器准备好接收文件
                    if self.current_file_transfer:
                        self.client.send("FILE_TRANSFER_START".encode('utf-8'))
                        
                        # 发送文件数据
                        try:
                            with open(self.current_file_transfer['path'], 'rb') as f:
                                while True and self.running:
                                    data = f.read(4096)
                                    if not data:
                                        break
                                    self.client.send(data)
                            
                            self.display_message(f"文件 {self.current_file_transfer['name']} 发送完成")
                            self.current_file_transfer = None
                        except Exception as e:
                            self.display_message(f"文件发送失败: {e}")
                            self.current_file_transfer = None
                
                else:
                    self.display_message(message)
            
            except ConnectionAbortedError:
                self.display_message("与服务器的连接已断开")
                break
            except Exception as e:
                self.display_message(f"接收消息时出错: {e}")
                break
        
        # 连接断开后的清理
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
    
    def display_message(self, message):
        """在聊天区域显示消息"""
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
    
    def send_message(self):
        """发送文本消息"""
        message = self.msg_entry.get("1.0", tk.END).strip()
        if message:
            try:
                self.client.send(message.encode('utf-8'))
                self.msg_entry.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("发送错误", f"无法发送消息: {e}")
    
    def send_file(self):
        """发送文件"""
        filepath = filedialog.askopenfilename()
        if filepath:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            try:
                # 发送文件传输请求
                self.client.send(f"FILE_TRANSFER_REQUEST:{filename}:{filesize}:{self.nickname}".encode('utf-8'))
                
                # 保存文件信息等待服务器确认
                self.current_file_transfer = {
                    'name': filename,
                    'path': filepath,
                    'size': filesize
                }
                
                self.display_message(f"正在发送文件 {filename}...")
            
            except Exception as e:
                messagebox.showerror("发送错误", f"无法发送文件: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()