import socket
import time
from time import ctime
import json
import string
import random

# TODO: fix log out then in and recent messages, then be able to run all in succession
# @james not every test works right now, will fix the remaining ones soon


def rand_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(6))


def calum_login(sock1):
    login_input = '/login'
    user_input = 'calum'
    pass_input = 'test'

    sock1.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(user_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(pass_input.encode('utf-8'))

    return sock1


def joe_login(sock2):
    login_input = '/login'
    user_input = 'joe'
    pass_input = 'test'

    sock2.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock2.send(user_input.encode('utf-8'))
    sock2.recv(1024)
    time.sleep(0.1)
    sock2.send(pass_input.encode('utf-8'))
    time.sleep(0.1)

    return sock2


def test_valid_login():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5000))

    calum_login(client_socket)

    data = client_socket.recv(1024).decode('utf-8')
    print(data)
    client_socket.close()
    return True if data == 'logged \n' else False


def test_invalid_login_user_online():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    calum_login(sock1)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    login_input = '/login'
    user_input = 'calum'

    time.sleep(0.5)
    sock2.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock2.send(user_input.encode('utf-8'))
    data = sock2.recv(1024).decode('utf-8')

    sock1.close()
    sock2.close()

    return True if data == 'denied' else False


def test_invalid_login_account_doesnt_exist():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5000))

    login_input = '/login'
    user_input = 'heghegdfg'

    sock.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock.send(user_input.encode('utf-8'))

    data = sock.recv(1024).decode('utf-8')
    sock.close()

    return True if data == 'error' else False


def test_logout_and_login():

    # TODO: fails for now, fix closing receive thread - unimportant for now

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5000))

    exit_input = '/exit'

    calum_login(sock)

    sock.send(exit_input.encode('utf-8'))
    time.sleep(1)

    calum_login(sock)

    data = sock.recv(1024).decode('utf-8')
    sock.close()

    return True if data == 'accepted' else False


def test_create_user_success():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    create_input = '/create'
    user_input = rand_string()
    pass_input = 'test'

    sock1.send(create_input.encode('utf-8'))
    sock1.recv(1024)
    sock1.send(user_input.encode('utf-8'))
    sock1.recv(1024)
    sock1.send(pass_input.encode('utf-8'))

    time.sleep(1)

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/users.txt', 'r') as f:
        user_list = json.load(f)

    print(user_input)
    print(list(user_list.keys())[-1])

    return True if list(user_list.keys())[-1] == user_input else False


def test_create_user_fail():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    create_input = '/create'
    user_input = 'calum'

    sock1.send(create_input.encode('utf-8'))
    sock1.recv(1024)
    sock1.send(user_input.encode('utf-8'))
    data = sock1.recv(1024).decode('utf-8')

    return True if data == 'error' else False


def test_delete_user():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/users.txt', 'r') as f:
        list1 = json.load(f)

    login_input = '/login'
    user_input = list(list1.keys())[-1]
    pass_input = 'test'
    delete = '/delete'

    sock1.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(user_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(pass_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(delete.encode('utf-8'))
    time.sleep(0.1)
    sock1.recv(1024)

    del_input = 'y'
    sock1.send(del_input.encode('utf-8'))

    time.sleep(0.5)

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/users.txt', 'r') as f:
        user_list = json.load(f)

    print(user_input)
    print(list(user_list.keys())[-1])

    return True if list(user_list.keys())[-1] != user_input else False


def test_send_and_receive_message():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    calum_login(sock1)
    joe_login(sock2)

    time.sleep(1)
    message = "hello world"
    sock1.send(message.encode('utf-8'))
    time.sleep(0.1)
    data = sock2.recv(1024).decode('utf-8')
    print(data)

    sock1.close()
    sock2.close()

    return True if data.splitlines()[-1] == 'calum (' + ctime()[11:16] + "): hello world" else False


def test_direct_messages():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    calum_login(sock1)
    joe_login(sock2)

    time.sleep(0.5)
    sock2.recv(1024)
    time.sleep(1)

    message = "hello joe"
    dm = '/dm joe'
    sock1.send(dm.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(message.encode('utf-8'))
    data = sock2.recv(1024).decode('utf-8')
    print(data)

    sock1.close()
    sock2.close()

    return True if data == ('(PM) calum says: ' + message) else False


def test_offline_direct_messages():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    calum_login(sock1)

    time.sleep(0.5)

    message = "hello joe"
    dm = '/dm joe'
    sock1.send(dm.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(message.encode('utf-8'))
    time.sleep(0.1)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    joe_login(sock2)
    time.sleep(0.5)
    data = sock2.recv(1024).decode('utf-8')
    result = data.splitlines()[-1]
    print(result)

    sock1.close()
    sock2.close()

    return True if result == ('calum (' + ctime()[:16] + '): ' + message) else False


def test_recent_messages():

    # TODO: fix

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5000))

    calum_login(sock)

    time.sleep(0.5)

    data = sock.recv(1024).decode('utf-8')
    recent = 'DMs received while offline: \n'

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/messages.txt', 'r') as f:
        recent_messages = json.load(f)

    test = data.splitlines()[1:7]
    print(test)

    for message in recent_messages:
        data = message.split('||||')
        recent += data[0] + ' (' + data[1] + '): ' + data[2] + '\n'

    sock.close()

    return True if test == recent else False


def test_check_online_users():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    online_input = '/online'

    calum_login(sock1)
    time.sleep(0.5)
    sock1.recv(1024)

    sock1.send(online_input.encode('utf-8'))
    data1 = sock1.recv(1024).decode('utf-8')

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    joe_login(sock2)

    time.sleep(0.5)
    sock1.recv(1024)

    sock1.send(online_input.encode('utf-8'))
    data2 = sock1.recv(1024).decode('utf-8')

    print(data1)
    print(data2)

    check1 = "Currently online users: calum, "
    check2 = "Currently online users: calum, joe, "

    return True if data1 == check1 and data2 == check2 else False


def test_friend_online_message():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    calum_login(sock1)
    time.sleep(0.5)
    sock1.recv(1024)

    time.sleep(2)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    joe_login(sock2)

    data = sock1.recv(1024).decode('utf-8')
    print(data)

    return True if data == "Your friend joe has joined the server!" else False


def test_add_friend():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/users.txt', 'r') as f:
        user_list = json.load(f)

    calum_login(sock1)
    time.sleep(0.1)
    sock1.recv(1024)

    while True:
        random_user = random.choice(list(user_list.keys()))
        add_input = '/add ' + random_user
        sock1.send(add_input.encode('utf-8'))
        data = sock1.recv(1024).decode('utf-8')

        if data == random_user + ' has been added to your friend list':
            break

    time.sleep(0.1)

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/friends.txt', 'r') as f:
        all_friends_list = json.load(f)

    friend_list = all_friends_list.get('calum')

    return True if random_user in friend_list else False


def test_remove_friend():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    calum_login(sock1)
    time.sleep(0.1)
    sock1.recv(1024)

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/friends.txt', 'r') as f:
        all_friends_list = json.load(f)

    friend_list = all_friends_list.get('calum')
    remove = friend_list[-1]
    delete_message = '/remove ' + remove
    sock1.send(delete_message.encode('utf-8'))

    time.sleep(0.5)

    with open('C:/Users/omahonyc/PycharmProjects/chatserver/omahonyc_workspace/friends.txt', 'r') as f:
        updated_friend_list = json.load(f)

    return True if remove not in updated_friend_list.get('calum') else False


def test_check_online_friends():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('127.0.0.1', 5000))

    friend_input = '/friends'

    calum_login(sock1)
    time.sleep(0.5)
    sock1.recv(1024)

    time.sleep(2)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('127.0.0.1', 5000))

    joe_login(sock2)

    sock1.recv(1024)
    sock1.send(friend_input.encode('utf-8'))
    data = sock1.recv(1024).decode('utf-8')

    check = "Online: joe\n Offline: "
    print(data)

    return True if data == check else False
