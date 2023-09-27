from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, \
    QMessageBox, QLineEdit, QDialog, QLabel
from PyQt5.QtGui import QFont
import config


# 服务端信息输入窗口
class ServerInfoDialog(QDialog):

    def __init__(self, parent=None):
        super(ServerInfoDialog, self).__init__(parent)
        self.connect_button = None  # 连接按钮
        self.username_label = None  # 标签：用户名
        self.username_edit = None    # 输入框：用户名
        self.server_port_label = None   # 标签：服务器端口
        self.server_port_edit = None    # 输入框：服务器端口
        self.server_ip_label = None   # 标签：服务器地址
        self.server_ip_edit = None  # 输入框：服务器地址
        self.initUI()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出确认', '确定要退出吗？', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # 连接信息窗口UI
    def initUI(self):
        font = QFont(config.font_family, config.font_size)
        self.setWindowTitle('服务器连接信息')
        self.setGeometry(300, 300, 300, 150)

        # 标签与输入框设置
        self.server_ip_label = QLabel('地址:')
        self.server_ip_label.setFont(font)
        self.server_ip_edit = QLineEdit(self)
        self.server_port_label = QLabel('端口:')
        self.server_port_label.setFont(font)
        self.server_port_edit = QLineEdit(self)
        self.username_label = QLabel('用户:')
        self.username_label.setFont(font)
        self.username_edit = QLineEdit(self)
        self.server_ip_edit.setText("192.168.137.1")  # 预设服务器 IP
        self.server_ip_edit.setFont(font)
        self.server_port_edit.setText("12312")  # 预设端口号
        self.server_port_edit.setFont(font)
        self.username_edit.setText("memo-pc")  # 预设用户名
        self.username_edit.setFont(font)

        # 按钮设置
        self.connect_button = QPushButton('连接', self)
        self.connect_button.setFont(font)
        self.connect_button.clicked.connect(self.accept)

        # 布局
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox_serverInfo = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()

        hbox1.addWidget(self.server_ip_label)
        hbox1.addWidget(self.server_ip_edit)
        hbox_serverInfo.addWidget(self.server_port_label)
        hbox_serverInfo.addWidget(self.server_port_edit)
        hbox3.addWidget(self.username_label)
        hbox3.addWidget(self.username_edit)
        hbox4.addWidget(self.connect_button)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox_serverInfo)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)

        self.setLayout(vbox)
