import time

import config
from PyQt5.QtWidgets import QWidget, QListWidget, QScrollBar, QVBoxLayout, QPushButton


class fileInfoDialog(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server

        self.vbox = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.downloadButton = QPushButton()

        self.initUI()

    def initUI(self):
        self.setMaximumWidth(int(config.desktop_width / 9))

        # 创建列表
        scroll_bar = QScrollBar(self)
        self.list_widget.setVerticalScrollBar(scroll_bar)
        # 创建下载按钮
        self.downloadButton.setText("Download")
        self.downloadButton.setMinimumHeight(80)

        self.vbox.addWidget(self.list_widget)
        self.vbox.addWidget(self.downloadButton)

    def initItem(self, FilesName):
        for filename in FilesName:
            self.list_widget.addItem(filename)

    def push_downloadButton(self, fileTransfer_t):
        currentItem = self.list_widget.currentItem()
        if currentItem is not None:
            # print(currentItem.text())
            config.keep_broadcasting = False
            fileTransfer_t.open(currentItem.text())
        else:
            pass

    def set_downloadButton_connect(self, fileTransfer_t):
        self.downloadButton.clicked.connect(lambda: self.push_downloadButton(fileTransfer_t))
