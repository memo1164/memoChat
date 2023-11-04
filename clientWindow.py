import time

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, \
    QHBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import config
import message
from serverCommunication import server_communication
from fileInfoDialog import fileInfoDialog


class ChatClient(QMainWindow):

    def __init__(self, client_socket):
        super().__init__()
        # 初始化程序主界面
        self.client_socket = client_socket
        self.server = server_communication(client_socket)
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
        self.send_button = QPushButton('发送', central_widget)
        self.send_button.setFont(font)
        self.send_button.setMaximumHeight(100)
        self.send_button.clicked.connect(self.send_message)

        # 创建文件窗口
        self.fileDialog = fileInfoDialog()

        # 创建连接按钮
        # connect_button = QPushButton('连接服务器', central_widget)
        # connect_button.clicked.connect(self.connect_server)

        # 左侧布局
        leftBox = QVBoxLayout()         # 左侧发送窗口
        leftBox_vbox = QVBoxLayout()    # 左侧发送窗口的垂直布局
        leftBox_hbox = QHBoxLayout()     # 左侧发送窗口的水平布局
        hbox_serverInfo = QHBoxLayout()  # 左侧发送窗口上方的信息栏的水平布局

        # 添加文本编辑框
        leftBox_vbox.addWidget(self.text_edit)
        # 添加文本输入框与发送按钮
        leftBox_hbox.addWidget(self.input_edit)
        leftBox_hbox.addWidget(self.send_button)
        # 添加信息标签
        hbox_serverInfo.addWidget(self.server_info)
        
        leftBox.addLayout(hbox_serverInfo)
        leftBox.addLayout(leftBox_vbox)
        leftBox.addLayout(leftBox_hbox)

        # 右侧布局
        rightBox = QVBoxLayout()
        rightBox.addWidget(self.fileDialog)

        # 主布局
        mainBox = QHBoxLayout()
        mainBox.addLayout(leftBox)
        mainBox.addLayout(rightBox)

        central_widget.setLayout(mainBox)

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

        if message_input:
            self.input_edit.clear()

            # 文件检查与发送
            message_is_file = message.file_path_check(message_input)
            print(message_is_file)
            if message_is_file is not None:
                self.server.send_one_file(message.file_path_check(message_input))
            # 文本发送（不存在的文件将以文本发送）
            else:
                self.server.send_one_message(message_input)
