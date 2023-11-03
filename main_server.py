# 待重构
import time
import socket
import sqlite3
import threading
from queue import Queue

# 创建队列用于消息广播
message_queue = Queue()


# 客户端线程
def handle_client(client_socket, client_address):
    load_check_start = "LOAD_START"
    load_check_end = "LOAD_END"

    load_len = 30
    cushioning_time = 0.05

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
            # 等待客户端
            received_message_len = client_socket.recv(8)
            received_message = client_socket.recv(int(received_message_len)).decode('utf-8')
            # 这里收到的通过按钮发送的消息不对
            if not received_message:
                break

            # 客户端消息为请求历史消息
            if received_message == load_check_start:
                # 查找数据库
                cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?', (load_len,))
                recent_messages = cursor.fetchall()
                # 遍历查找结果
                for message in reversed(recent_messages):
                    # 数据转换为消息(广播消息格式)
                    message_str = data_to_message(message[1], message[3], message[2])
                    message_len = len(message_str.encode('utf-8'))
                    client_socket.send(f'{message_len:08d}'.encode('utf-8'))
                    client_socket.send(message_str.encode('utf-8'))
                    # client_socket.send(message_str.encode('utf-8'))
                    # 缓冲
                    # time.sleep(cushioning_time)

                # 告知客户端数据流结束
                end_check_len = len(load_check_end)
                client_socket.send(f'{end_check_len:08d}{load_check_end}'.encode('utf-8'))

            # 接收到客户端文本消息
            else:
                # 获取时间戳
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                print(f'*[{client_address}] {received_message}')

                # 消息转换为数据
                data = message_to_data(received_message)
                # 加入数据库
                cursor.execute("INSERT INTO messages (username, content, timestamp) VALUES (?, ?, ?)",
                               (data[0], data[1], timestamp))
                conn.commit()
                # 数据转换为消息(广播消息格式)
                message_str = data_to_message(data[0], timestamp, data[1])

                # 将消息发送到广播消息队列
                message_queue.put(message_str)

                # time.sleep(cushioning_time)

    except ConnectionResetError:
        # 客户端强制关闭连接的异常处理
        print(f'客户端 {client_address} 关闭连接,现有线程数 {len(clients) - 1}')

    finally:
        # 在无论如何结束线程之前，将客户端从列表中移除
        clients.remove(client_socket)
        client_socket.close()


# 消息处理
def data_to_message(username, timestamp, message):
    # &(用户) !(时间) #(文本)
    message_len = len(f'&{username}!{timestamp}#{message}'.encode('utf-8'))
    return f'{message_len:08d}&{username}!{timestamp}#{message}'


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


# 广播线程
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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0'
    port = 12312
    server_socket.bind((host, port))

    server_socket.listen(5)
    print(f"等待客户端连接在 {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"连接来自 {client_address} ,现有线程数 {len(clients) + 1}")
        clients.append(client_socket)

        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()


if __name__ == '__main__':
    main()
