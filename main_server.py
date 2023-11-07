# 待重构
import os
import time
import socket
import sqlite3
import threading
from queue import Queue
from math import ceil

# 创建队列用于消息广播
message_queue = Queue()


# 客户端线程
# 参数：<client_socket对象:socket><客户端地址:str>
# 返回值：无
def handle_client(client_socket, client_address):
    # 规定的关键字
    load_check_start = "LOAD_START"
    load_check_end = "LOAD_END"

    # 读取历史消息的最大长度
    load_len = 30
    # 服务器端文件存储路径
    file_path = os.path.curdir

    # 创建数据库连接
    conn = sqlite3.connect('chat_messages.db')
    cursor = conn.cursor()

    # 创建消息表格（如果不存在）
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT,
                       content TEXT,
                       timestamp DATETIME)''')
    conn.commit()

    try:
        while True:
            # 等待客户端发送消息 #

            # 接收消息的字节数
            received_message_len = client_socket.recv(8)
            # 接收消息的类型（大于0为文件类型，此时received_message_type代表文件的分块数量）
            received_message_type = client_socket.recv(8)
            # 接收消息的文本内容
            received_message = client_socket.recv(int(received_message_len)).decode('utf-8')

            # 空消息处理
            if not received_message:
                break

            # 消息内容为客户端消息为请求历史消息
            if received_message == load_check_start:
                # 发送历史消息 #
                # 查找数据库
                cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?', (load_len,))
                recent_messages = cursor.fetchall()
                # 遍历查找结果
                for message in reversed(recent_messages):
                    # 数据转换为消息(普通消息格式)
                    message_str = data_to_message(message[1], message[3], message[2])
                    send_one_message(client_socket, message_str)

                # 发送文件列表 #
                # 获取并筛选路径下文件列表（目前不支持目录） #
                files = os.listdir(file_path)
                files_list = [file for file in files if os.path.isfile(os.path.join(file_path, file))]
                # 遍历发送
                for file_name in files_list:
                    message_str = '$' + file_name
                    send_one_message(client_socket, message_str)

                # 告知客户端数据流结束
                message_str = load_check_end
                send_one_message(client_socket, message_str)

            # 接收到客户端文本消息
            elif int(received_message_type) == 0:
                # 获取时间戳
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                # 收到文件下载请求消息
                if received_message[0] == '$':
                    file_name = received_message[1:]
                    if os.path.exists(os.path.join(file_path, file_name)):
                        send_one_file(client_socket, os.path.join(file_path, file_name))
                    else:
                        # 文件不存在则告知分块数量为0
                        client_socket.send(f'{0:08d}'.encode('utf-8'))
                        client_socket.send(f'{0:08d}'.encode('utf-8'))

                # 收到普通消息
                else:
                    print(f'*[{client_address}] {received_message}')
                    # 消息转换为数据
                    data = message_to_data(received_message)
                    # 加入数据库
                    cursor.execute("INSERT INTO messages (username, content, timestamp) VALUES (?, ?, ?)",
                                   (data[0], data[1], timestamp))
                    conn.commit()
                    # 数据转换为消息(广播消息格式)
                    message_str = data_to_broadcast_messages(data[0], timestamp, data[1])
                    # 将消息发送到广播消息队列
                    message_queue.put(message_str)

            # 客户端发送文件
            elif int(received_message_type) > 0:
                file_name = received_message[received_message.find('#') + 1:]
                blockNum = int(received_message_type)
                with open(os.path.join(file_path, file_name), 'wb') as file:
                    for _ in range(blockNum):
                        data = client_socket.recv(10240)
                        file.write(data)
                # 接收完成消息提示添加到广播队列
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                message_str = file_received_broadcast_message(file_name, timestamp)
                message_queue.put(message_str)

    except ConnectionResetError as CE:
        # 客户端强制关闭连接的异常处理
        print(f'[CLIENT ERROR] {CE}')
        print(f'客户端 {client_address} 关闭连接,现有线程数 {len(clients) - 1}')

    finally:
        # 在无论如何结束线程之前，将客户端从列表中移除
        clients.remove(client_socket)
        client_socket.close()


# 消息发送 #

# 发送一条（未添加头部的）消息文本
# 参数：<client_socket对象:socket><消息文本:str>
# 返回值：无
def send_one_message(client_socket, message_str):
    message_len = len(message_str.encode('utf-8'))
    client_socket.send(f'{message_len:08d}{message_str}'.encode('utf-8'))


# 发送单个文件
# 参数：<client_socket对象:socket><文件路径:str>
# 返回值：无
def send_one_file(client_socket, file_path):
    blockNum = ceil(os.path.getsize(file_path) / 10240)
    # 会被客户端的广播接收线程吞掉一次8字节的send
    client_socket.send(f'{0:08d}'.encode('utf-8'))
    client_socket.send(f'{blockNum:08d}'.encode('utf-8'))

    # 打开要发送的文件分块发送
    with open(file_path, 'rb') as file:
        for _ in range(blockNum):
            data = file.read(10240)
            client_socket.send(data)

    time.sleep(0.1)


# 消息文本处理 #
# 注意要以utf8编码取长度 #

# 数据转消息文本（不添加头部）
# 参数：<用户名:str><时间戳:str><消息文本:str>
# 返回值：<消息文本:str>
def data_to_message(username, timestamp, message):
    # &(用户) !(时间) #(文本)
    return f'&{username}!{timestamp}#{message}'


# 数据转广播消息文本（添加头部）
# 参数：<用户名:str><时间戳:str><消息文本:str>
# 返回值：<消息文本:str>
def data_to_broadcast_messages(username, timestamp, message):
    # &(用户) !(时间) #(文本)
    message = f'&{username}!{timestamp}#{message}'
    message_len = len(message.encode('utf-8'))
    return f'{message_len:08d}{message}'


# 数据文件接受完毕的广播消息文本
# 参数：<文件名:str><时间戳:str>
# 返回值：<消息文本:str>
def file_received_broadcast_message(filename, timestamp):
    message = f'&SERVER!{timestamp}#文件[{filename}]已接收！'
    message_len = len(message.encode('utf-8'))
    return f'{message_len:08d}{message}'


# 消息文本转数据
# 参数：<消息文本:str>
# 返回值：[<用户名:str>,<消息文本:str>]
def message_to_data(message_str):
    # &(用户) #(文本)
    username = ""
    message = ""
    data_type = 0

    for i in message_str:
        if data_type == 0 and i == '&':
            data_type = 1
            continue
        if data_type == 1 and i == '#':
            data_type = 2
            continue
        if data_type == 1:
            username = username + i
            continue
        if data_type == 2:
            message = message + i

    return [username, message]


# 广播线程 #
# 用于将消息队列中的内容广播给所有已连接的客户端
def broadcast_messages():
    while True:
        # 从消息队列获取消息
        message = message_queue.get()
        if message is None:
            break

        print(f'*[SERVER BROADCAST] {message}')

        # 向所有客户端广播消息
        for client in clients:
            try:
                client.send(message.encode('utf-8'))
            except socket.error as e:
                print(f'[SOCKET ERROR] {e}')


# 客户端线程组
clients = []

# 创建线程来广播消息
broadcast_thread = threading.Thread(target=broadcast_messages)
broadcast_thread.start()


def main():
    # 开启主机socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0'
    port = 12312
    server_socket.bind((host, port))

    # 开启监听并设置挂起的连接队列的最大长度
    server_socket.listen(10)
    print(f"等待客户端连接在 {host}:{port}")

    while True:
        # 收到连接
        client_socket, client_address = server_socket.accept()
        print(f"连接来自 {client_address} ,现有线程数 {len(clients) + 1}")
        clients.append(client_socket)

        # 为连接的客户端开启线程
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()


if __name__ == '__main__':
    main()
