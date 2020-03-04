import socket
import threading
import sys
import User
from time import ctime
import Message
import sqlite3

clients = set()
clients_lock = threading.Lock()
online_users = []
user_sockets = {}
BUFFER_SIZE = 8192

# TODO: remove deleted users from friends lists and password dictionary


def create_socket():
    """
    First creating the server socket, binding the host and port to it,
    then making it listen for any incoming client connections and when the
    connection comes in, create a thread for it.
    """
    host = '127.0.0.1'
    port = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(10)
    print("Server setup")

    while True:
        conn, address = sock.accept()
        print(address, "has connected to the server")
        threading.Thread(target=authenticate, args=(conn, address)).start()


def authenticate(client_socket, address):

    with clients_lock:
        if client_socket not in clients:
            clients.add(client_socket)

    while True:

        try:
            data = client_socket.recv(BUFFER_SIZE)
        except OSError:
            "Client disconnected"
            sys.exit(0)

        if data is not None:
            data_read = data
            data_decoded = data_read.decode('utf-8')

            if data_decoded == '/login':
                client_socket.send("login".encode('utf-8'))
                login(client_socket, address)

            elif data_decoded == '/create':
                client_socket.send("create".encode('utf-8'))
                User.create_user(client_socket, address)

            else:
                client_socket.send("fail".encode('utf-8'))


def new_client(client_socket, address, username, online_user_list):
    """
    Add the client to a list of clients then waits to receive data. When the data
    comes in, it is unpacked to find out the length of the message and the ID of
    the sender of the message, then is repacked and sent out to all clients barring the
    one who sent the message.
    """

    all_friend_list = User.get_all_friends()
    friend_keys = []
    for key, value in all_friend_list.items():
        if username in value:
            friend_keys.append(key)

    for name, user_socket in user_sockets.items():
        if name in friend_keys:

            try:
                user_sockets.get(name).send("Your friend {0} has joined the server!".format(username).encode('utf-8'))
            except ConnectionResetError:
                print("Client disconnected")
            except OSError:
                print("Client disconnected")

    while True:

        try:
            data = client_socket.recv(BUFFER_SIZE)
        except OSError:
            "Client disconnected"
            sys.exit(0)

        while data is not None:
            data_decoded = data.decode('utf-8')

            if data_decoded == '/delete':
                User.delete_user(client_socket, username, address)

            elif data_decoded == '/online':
                show_online(client_socket, online_user_list)
                break

            elif data_decoded[:3] == '/dm':
                target = data_decoded[4:]
                if target in online_users:
                    direct_message(client_socket, username, user_sockets, target)

                elif target not in online_users and target in User.get_user_list():
                    dm_message = "{0} is offline, they will see the message when next logging in: ".format(target)
                    client_socket.send(dm_message.encode('utf-8'))

                    data = client_socket.recv(BUFFER_SIZE)
                    data = data.decode('utf-8')
                    Message.save_direct_message(username, target, data)

                else:
                    error_msg = 'User does not exist'

                    client_socket.send(error_msg.encode('utf-8'))
                break

            elif data_decoded[:4] == '/add':
                friend = data_decoded[5:]
                User.add_friend(client_socket, username, friend)
                break

            elif data_decoded[:7] == '/remove':
                target = data_decoded[8:]
                User.remove_friend(client_socket, username, target)
                break

            elif data_decoded == '/friends':
                online_friends, offline_friends = User.show_online_friends(online_user_list, username)

                separator = ', '
                online = separator.join(online_friends)
                offline = separator.join(offline_friends)

                message = "Online: {0} \n Offline: {1}".format(online, offline)

                client_socket.send(message.encode('utf-8'))
                break

            elif data_decoded == '/exit':
                online_users.remove(username)
                with clients_lock:
                    clients.remove(client_socket)

                threading.Thread(target=authenticate, args=(client_socket, address)).start()

            print(username, ": ", data)

            if data_decoded[0] != '/':
                Message.save_message(username, data)

            with clients_lock:
                for c in clients:
                    is_not_sender = c != client_socket
                    if is_not_sender:

                        try:
                            c.send("{0} ({1}): {2}".format(username, ctime()[11:16], data_decoded).encode('utf-8'))
                        except ConnectionResetError:
                            print("Client disconnected")
                        except OSError:
                            print("Client disconnected")

            break


def login(client_socket, address):

    user_list = User.get_user_list()
    password_list = User.get_passwords()

    while True:
        data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        name = data.lower()

        if name in user_list and name not in online_users:
            client_socket.send("accepted".encode('utf-8'))

            password = password_list.get(name)
            print(password)
            data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            print(data)
            print(User.check_password(password, 'test'))

            if User.check_password(password, data) is True:
                online_users.append(name)
                print(online_users)

                user_sockets[name] = client_socket
                print(user_sockets)

                client_socket.send("logged \n".encode('utf-8'))

                Message.show_recent_messages(client_socket),
                Message.show_dms(client_socket, name),
                new_client(client_socket, address, name, online_users)
            else:
                print("login failed")

        elif name in online_users:
            client_socket.send("denied".encode('utf-8'))

        elif name not in user_list:
            client_socket.send("error".encode('utf-8'))


def direct_message(client_socket, username, sockets, target):
    dm_message = "Enter your message for {0}: ".format(target)

    client_socket.send(dm_message.encode('utf-8'))

    data = client_socket.recv(BUFFER_SIZE)
    data_to_send = "(PM) {0} says: {1}".format(username, data.decode('utf-8'))

    try:
        sockets.get(target).send(data_to_send.encode('utf-8'))
        Message.save_direct_message(username, target, data_to_send)
    except ConnectionResetError:
        print("Client disconnected")
    except OSError:
        print("Client disconnected")


def show_online(client_socket, online_user_list):

    online_message = 'Currently online users: '
    for user in online_user_list:
        online_message += user + ', '

    client_socket.send(online_message.encode('utf-8'))


if __name__ == '__main__':
    create_socket()
