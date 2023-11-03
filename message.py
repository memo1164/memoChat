import os

def message_to_data_client(message):
    # &(用户) !(时间) #(文本)
    username_str = ""
    message_str = ""
    time_str = ""
    data_type = 0
    for i in message:
        if data_type == 0 and i == '&':
            data_type = 1
            continue
        if data_type == 1 and i == '!':
            data_type = 2
            continue
        if data_type == 2 and i == '#':
            data_type = 3
            continue
        if data_type == 1:
            username_str = username_str + i
        if data_type == 2:
            time_str = time_str + i
        if data_type == 3:
            message_str = message_str + i

    return [username_str, time_str, message_str]


def data_to_text_client(data):
    return f'[{data[0]}] ({data[1]})\n{data[2]}'


def data_to_message_client(username, message):
    message_len = len(f'&{username}#{message}'.encode('utf-8'))
    return f'{message_len:08d}&{username}#{message}'


def data_to_message_server(username, timestamp, message):
    # &(用户) !(时间) #(文本)
    return '&' + username + '!' + str(timestamp) + '#' + message


def message_to_data_server(message_str):
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


def file_path_check(message=""):
    if message.startswith('file:///') is True:
        path = message[:8]
        if os.path.exists(path):
            return path
        else:
            return None
    else:
        return None
