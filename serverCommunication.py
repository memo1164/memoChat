import socket
import os
from math import ceil
from PyQt5.QtWidgets import QMessageBox, QWidget
import config
import message
from serverInfoDialog import ServerInfoDialog


# 以对话框形式获取服务器地址、端口和用户名
def get_server_info():
    # 服务器信息对话框类
    server_info_dialog = ServerInfoDialog()
    result = server_info_dialog.exec_()
    # 保存用户输入信息作为服务器信息
    if result == server_info_dialog.Accepted:
        config.client_username = server_info_dialog.username_edit.text()
        config.server_ip = server_info_dialog.server_ip_edit.text()
        config.server_port = int(server_info_dialog.server_port_edit.text())


class server_communication(QWidget):

    def __init__(self, client_socket):
        super().__init__()
        self.broadcast_thread = None
        self.text_edit_lock = None
        self.client_socket = client_socket

    # 连接服务器方法
    def connect_server(self):
        while True:
            try:
                # 调用get_server_info方法获取服务器地址、端口和用户名
                get_server_info()
                # 如果服务器信息正常，连接服务器
                if config.client_username and config.server_ip and config.server_port:
                    self.client_socket.connect((config.server_ip, config.server_port))
                    break
                else:
                    # 输入信息不完整，显示错误消息
                    QMessageBox.critical(self, '错误', '信息不完整，请输入用户名、服务器地址和端口')
            except (socket.error, ValueError) as e:
                # 连接失败或输入无效，显示错误消息
                QMessageBox.critical(self, '错误', f'无法连接到服务器，请检查服务器地址和端口:{e}')

    # 通知服务器需要读取历史消息
    def load_start(self):
        load_start_len = len(config.load_check_start)
        self.client_socket.send(f'{load_start_len:08d}{0:08d}{config.load_check_start}'.encode('utf-8'))

    def get_len(self):
        return self.client_socket.recv(8)

    # 从服务器读取一条消息
    def load_one_message(self):
        message_len = int(self.get_len())
        return self.client_socket.recv(message_len).decode('utf-8')

    # 向服务器发送一条消息
    def send_one_message(self, client_message):
        self.client_socket.send(message.data_to_message_client(config.client_username, client_message, 0).encode('utf-8'))

    def send_one_file(self, file_path=""):
        file_name = file_path[file_path.rfind('/') + 1 :]
        blockNum = ceil(os.path.getsize(file_path) / 10240)
        self.client_socket.send(message.data_to_message_client(config.client_username, file_name, blockNum).encode('utf-8'))
        # 打开要发送的文件分块发送
        with open(file_path, 'rb') as file:
            for _ in range(blockNum):
                data = file.read(10240)
                self.client_socket.send(data)

    # 读取历史消息
    def load_history_message(self, text_edit):
        # 通知服务器端
        self.load_start()
        while True:
            received_message = self.load_one_message()
            # 读取到结束消息
            if received_message == config.load_check_end:
                break
            # 读取到普通消息
            else:
                received_message = message.data_to_text_client(message.message_to_data_client(received_message))
                text_edit.append(f'{received_message}\n')
        text_edit.append(f'----------以上为历史消息----------\n')
