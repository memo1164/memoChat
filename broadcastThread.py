import threading
from PyQt5.QtGui import QTextCursor

import config
import time
import message


class broadcast_thread:

    def __init__(self, client_socket, text_edit):
        self.client_socket = client_socket
        self.text_edit = text_edit
        # 创建一个线程用于接收广播消息
        self.text_edit_lock = threading.Lock()  # 创建锁对象
        self.broadcast_thread = threading.Thread(target=self.receive_broadcast)
        self.broadcast_thread.daemon = True  # 设置为守护线程，随着主线程退出而退出
        self.broadcast_thread.start()

    def receive_broadcast(self):
        try:
            while True:
                if config.keep_broadcasting:
                    # 线程被开启
                    broadcast_message = self.load_one_message()
                    # 空消息跳过处理
                    if broadcast_message is None:
                        pass
                    else:
                        # print(broadcast_message)
                        broadcast_message = message.data_to_text_client(
                            message.message_to_data_client(broadcast_message))
                        # 将广播消息添加到对话框
                        with self.text_edit_lock:
                            self.text_edit.append(f'{broadcast_message}\n')
                            # 自动滚屏
                            self.text_edit.moveCursor(QTextCursor.End)
                else:
                    time.sleep(0.2)
        except Exception as e:
            print(f"Error in receive_broadcast: {e}")

    # 从服务器读取一条消息
    def load_one_message(self):
        message_len = int(self.client_socket.recv(8))
        if message_len == 0:
            return None
        else:
            return self.client_socket.recv(message_len).decode('utf-8')
