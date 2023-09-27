import socket
import sys
from PyQt5.QtWidgets import QApplication

from broadcastThread import broadcast_thread
from clientWindow import ChatClient
from serverCommunication import server_communication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 创建server_communication类
    server = server_communication(client_socket)
    # 连接服务器
    server.connect_server()
    # 创建程序主界面类
    client_window = ChatClient(client_socket)
    # 读取历史消息
    server.load_history_message(client_window.text_edit)
    client_window.show()
    # 开启接收广播消息线程
    broadcast_t = broadcast_thread(client_socket, client_window.text_edit)
    sys.exit(app.exec_())
