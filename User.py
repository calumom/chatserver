import json
import server
from passlib.hash import pbkdf2_sha256

BUFFER_SIZE = 8192


def get_all_friends():

    with open("friends.txt") as f:
        all_friends_list = json.load(f)

    return all_friends_list


def get_user_list():

    with open('users.txt') as f:
        if 'users.txt' is not None:
            user_list = json.load(f)
        else:
            user_list = {}

    return user_list


def get_passwords():

    with open('passwords.txt') as f:
        password_list = json.load(f)

    return password_list


def add_friend(client_socket, username, target_friend):

    # TODO: shouldn't be able to add self

    all_friends_list = get_all_friends()
    user_list = get_user_list()

    if target_friend in user_list:
        if all_friends_list.get(username) is not None:
            friends = all_friends_list.get(username)
        else:
            all_friends_list[username] = []
            friends = []

        if target_friend not in all_friends_list.get(username):
            friends.append(target_friend)
            all_friends_list[username] = friends

            message = "{0} has been added to your friend list".format(target_friend)
            client_socket.send(message.encode('utf-8'))
        else:
            message = "User already in friends list"
            client_socket.send(message.encode('utf-8'))
    else:
        message = "User does not exist"
        client_socket.send(message.encode('utf-8'))

    with open('friends.txt', 'w') as outfile:
        json.dump(all_friends_list, outfile)

    return


def hash_password(password):
    return pbkdf2_sha256.hash(password)


def check_password(hashed_password, input_password):
    return pbkdf2_sha256.verify(input_password, hashed_password)


def remove_friend(client_socket, username, target_remove):
    all_friends_list = get_all_friends()
    user_list = get_user_list()

    if target_remove in user_list:
        friends = all_friends_list.get(username)

        if target_remove in friends:
            friends.remove(target_remove)
            all_friends_list[username] = friends

            message = "{0} has been removed from your friend list".format(target_remove)
            client_socket.send(message.encode('utf-8'))
    else:
        message = "User does not exist"
        client_socket.send(message.encode('utf-8'))

    with open('friends.txt', 'w') as outfile:
        json.dump(all_friends_list, outfile)

    return


def show_online_friends(online_users, username):

    all_friends_list = get_all_friends()
    user_friends = all_friends_list.get(username)
    online_friends = []
    offline_friends = []

    if user_friends is None:
        user_friends = {}

    for friends in user_friends:
        if friends in online_users:
            online_friends.append(friends)
        else:
            offline_friends.append(friends)

    return online_friends, offline_friends


def create_user(client_socket, address):

    user_list = get_user_list()
    password_list = get_passwords()

    while True:
        data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        name = data.lower()

        if name == '--':
            server.authenticate(client_socket, address)

        if name not in user_list:
            client_socket.send('pass'.encode('utf-8'))
            break
        else:
            client_socket.send('error'.encode('utf-8'))

    password = client_socket.recv(BUFFER_SIZE).decode('utf-8')
    hashed_password = hash_password(password)

    if not bool(user_list):
        identifier = 1
    else:
        identifier = max(user_list.values()) + 1

    user_list[name] = identifier
    password_list[name] = hashed_password

    with open('users.txt', 'w') as outfile:
        json.dump(user_list, outfile)

    with open('passwords.txt', 'w') as outfile:
        json.dump(password_list, outfile)

    server.login(client_socket, address)


def delete_user(client_socket, username, address):

    user_list = get_user_list()

    data = client_socket.recv(BUFFER_SIZE).decode('utf-8')

    if data == 'y':
        del user_list[username]
    else:
        return

    with open('users.txt', 'w') as outfile:
        json.dump(user_list, outfile)

    server.login(client_socket, address)
