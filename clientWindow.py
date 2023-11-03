import time

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, \
    QHBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import config
from serverCommunication import server_communication


class ChatClient(QMainWindow):

    def __init__(self, client_socket):
        super().__init__()
        # 初始化程序主界面
        self.client_socket = client_socket
        self.server = server_communication(client_socket)
        self.input_edit = None
        self.text_edit = None
        self.server_info = None
        self.initUI()

    def initUI(self):
        font = QFont(config.font_family, config.font_size)
        self.setWindowTitle('客户端')
        self.setGeometry(100, 100, int(config.desktop_width / 3), int(config.desktop_height / 2))
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        # 添加服务器信息字段
        self.server_info = QLabel(central_widget)
        self.server_info.setAlignment(Qt.AlignCenter)
        self.server_info.setFont(font)
        self.server_info.setText(f'{config.client_username} : 已连接至服务器 {config.server_ip}:{config.server_port}')
        # 创建一个文本编辑框用于显示聊天消息
        self.text_edit = QTextEdit(central_widget)
        self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)
        # 创建一个文本输入框用于输入消息
        self.input_edit = QTextEdit(central_widget)
        self.input_edit.setMaximumHeight(100)
        self.input_edit.setFont(font)
        # 创建发送按钮
        send_button = QPushButton('发送', central_widget)
        send_button.setFont(font)
        send_button.setMaximumHeight(100)
        send_button.clicked.connect(self.send_message)
        # 创建连接按钮
        # connect_button = QPushButton('连接服务器', central_widget)
        # connect_button.clicked.connect(self.connect_server)
        # 布局
        main_vbox = QVBoxLayout()
        vbox = QVBoxLayout()
        hbox_bottom = QHBoxLayout()
        hbox_bottom.addWidget(self.input_edit)
        hbox_bottom.addWidget(send_button)
        hbox_serverInfo = QHBoxLayout()
        hbox_serverInfo.addWidget(self.server_info)
        vbox.addWidget(self.text_edit)
        vbox.addLayout(hbox_bottom)
        # vbox.addWidget(connect_button)
        main_vbox.addLayout(hbox_serverInfo)
        main_vbox.addLayout(vbox)
        central_widget.setLayout(main_vbox)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出确认', '确定要退出吗？', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            config.keep_broadcasting = False  # 停止广播线程
            time.sleep(0.05)  # 等待广播线程结束
            self.client_socket.close()  # 关闭socket
            event.accept()
        else:
            event.ignore()

    # 通过发送按钮发送一条消息
    def send_message(self):
        message_input = self.input_edit.toPlainText()
        # time.sleep(0.05)

        if message_input:
            self.input_edit.clear()
            self.server.send_one_message(message_input)
            # 缓冲
            time.sleep(0.05)
