import threading
import time
from queue import Queue
import os

from PyQt5.QtGui import QTextCursor

import config


class fileTransferThreads:

    def __init__(self, client_socket, text_edit):
        self.client_socket = client_socket
        self.text_edit = text_edit
        self.run_flag = False
        # 接收队列
        self.recvQueue = Queue()
        # 创建一个线程用于文件传输
        self.text_edit_lock = threading.Lock()  # 创建锁对象
        self.fileTransfer_thread = threading.Thread(target=self.run)
        self.fileTransfer_thread.daemon = True  # 设置为守护线程，随着主线程退出而退出
        self.fileTransfer_thread.start()

    def open(self, file_name):
        self.recvQueue.put(file_name)
        self.run_flag = True

    def run(self):
        try:
            while True:
                flag = False
                while self.run_flag and self.recvQueue.empty() is not True:
                    file_name = self.recvQueue.get()
                    file_path = os.path.join(config.loadFile_path, file_name)
                    self.client_socket.send(f'{len(file_name) + 1:08d}{0:08d}${file_name}'.encode('utf-8'))
                    blockNum = int(self.client_socket.recv(8).decode('utf-8'))
                    # bug：因为广播线程总会在吞掉8字节后停止，所以服务器端写的发送两次8字节（一次0，一次blockNum），但会导致连续下载文件时（中间不开启广播线程）接收不到正确的 blockNum
                    if flag is True:
                        blockNum = int(self.client_socket.recv(8).decode('utf-8'))

                    # 用户要求下载的文件不存在
                    if blockNum == 0:
                        with self.text_edit_lock:
                            self.text_edit.append(f'{file_name}文件不存在!\n')
                            # 自动滚屏
                            self.text_edit.moveCursor(QTextCursor.End)
                    # 下载文件
                    else:
                        with open(file_path, 'wb') as file:
                            for _ in range(blockNum):
                                data = self.client_socket.recv(10240)
                                file.write(data)

                        with self.text_edit_lock:
                            self.text_edit.append(f'{file_name}下载完成!\n')
                            # 自动滚屏
                            self.text_edit.moveCursor(QTextCursor.End)

                    flag = True
                    time.sleep(0.5)

                self.run_flag = False
                config.keep_broadcasting = True
                time.sleep(1)

        except Exception as e:
            print(f"Error in receive_broadcast: {e}")
