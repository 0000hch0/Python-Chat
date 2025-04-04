# 🚀 **Tutorial for Using a LAN Chat Tool**  

This tutorial will guide you through using a Python-based LAN chat tool, including server and client configuration, running methods, and how to achieve remote communication via **SakuraFRP**.  

---

## 📌 **Table of Contents**  
1. [Environment Preparation](#-environment-preparation)  
2. [Server Configuration](#-server-configuration)  
3. [Client Configuration](#-client-configuration)  
4. [LAN Chat Testing](#-lan-chat-testing)  
5. [Remote Communication via SakuraFRP](#-remote-communication-via-sakurafrp)  
6. [Common Issues](#-common-issues)  

---

## 🛠 **Environment Preparation**  
### **1. Install Python**  
- Ensure that your computer has **Python 3.6+** installed.  
- Download address: [Python Official Website](https://www.python.org/downloads/)  

### **2. Install Dependencies**  
Run the following command in the terminal to install the necessary libraries:  
```bash
pip install tkinter scrolledtext
```  
(`tkinter` is usually installed with Python and does not require additional installation.)  

---

## 💻 **Server Configuration**  
### **1. Download the Server Code**  
Save `server.py` to your computer (the code is provided in the previous section).  

### **2. Run the Server**  
Navigate to the directory where `server.py` is located in the terminal and run:  
```bash
python server.py
```  
By default, it listens on `0.0.0.0:12345`. If you need to change the port, you can edit the `host` and `port` variables in the code.  

✅ **After successful execution, you will see:**  
```  
Server started, listening on 0.0.0.0:12345  
```  

---

## 📱 **Client Configuration**  
### **1. Download the Client Code**  
Save `client.py` to your computer (the code is provided in the previous section).  

### **2. Run the Client**  
Navigate to the directory where `client.py` is located in the terminal and run:  
```bash
python client.py
```  

✅ **The client interface looks like this:**  
![Client Interface](https://via.placeholder.com/400x300?text=Chat+Client+UI)  

### **3. Connect to the Server**  
- **Server Address**: Enter the LAN IP of the server (e.g., `192.168.1.100`)  
- **Port**: `12345` (default)  
- **Nickname**: Customize your username  
- Click **"Connect"**  

---

## 🌐 **LAN Chat Testing**  
1. **Send Text Messages**  
   - Type text in the input box and click **"Send"**  
   - All clients and the server will receive the message  

2. **Send Files/Pictures**  
   - Click **"Send File"**, select a file  
   - The recipient will receive a confirmation prompt, and the file will be saved to the `received_files` directory after acceptance  

---

## 🌍 **Remote Communication via SakuraFRP**  
If your friend is not on the same LAN, you can use **SakuraFRP** for NAT traversal.  

### **1. Register a SakuraFRP Account**  
- Official website: [SakuraFRP](https://www.natfrp.com/)  

### **2. Create a Tunnel**  
1. Log in and go to **"Tunnel List"** → **"Create Tunnel"**  
2. Select **"TCP"** protocol and fill in:  
   - **Local IP**: `127.0.0.1` (if the server is running on the same machine)  
   - **Local Port**: `12345` (consistent with the server port)  
3. Select an **"Overseas Node"** (e.g., Tokyo, Japan, no filing required)  

### **3. Launch the SakuraFRP Client**  
1. Download the client for your system: [SakuraFRP Download Page](https://www.natfrp.com/user/download)  
2. Run and log in:  
   ```bash
   ./frpc -f <your_tunnel_ID>
   ```  
3. You will be provided with a **public IP:port** (e.g., `123.123.123.123:12345`)  

### **4. Connect to the Public Server**  
- Enter the **public IP and port provided by SakuraFRP** in the client  
- Click **"Connect"** to achieve remote chatting  

---

## ❓ **Common Issues**  
### **Q1: Client Connection Failure**  
- Check if the server is running  
- Ensure that the firewall allows traffic on port `12345`  

### **Q2: File Transfer Failure**  
- Ensure the `received_files` directory exists  
- Check the network stability  

### **Q3: Slow SakuraFRP Speed**  
- Try changing the node (e.g., Hong Kong, Singapore)  
- The free version is speed-limited; consider upgrading to a paid plan  

---

## 🎉 **Summary**  
✅ **For LAN Use**: Simply run `server.py` and `client.py`  
✅ **For Remote Use**: Map port `12345` via SakuraFRP  
✅ **File Transfer**: Supports images, documents, and any other files  

Now you can chat with your friends happily! 🚀💬