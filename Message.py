import json
from time import ctime


def save_message(username, data_read):

    with open('messages.txt') as f:
        recent_messages = json.load(f)

    if len(recent_messages) > 5:
        del recent_messages[0]

    recent_messages.append("{0}||||{1}||||{2}".format(username, ctime()[:16], data_read.decode('utf-8')))

    with open('messages.txt', 'w') as outfile:
        json.dump(recent_messages, outfile)


def save_direct_message(username, target, data):

    with open('directmessages.txt') as f:
        dm = json.load(f)

    dm.append("{0}||||{1}||||{2}||||{3}".format(username, ctime()[:16], data, target))

    with open('directmessages.txt', 'w') as outfile:
        json.dump(dm, outfile)


def show_recent_messages(client_socket):

    message_to_send = 'Recent messages: \n'

    with open('messages.txt') as f:
        recent_messages = json.load(f)

    for message in recent_messages:
        data = message.split('||||')
        message_to_send += "{0} ({1}): {2} \n".format(data[0], data[1], data[2])

    client_socket.send(message_to_send.encode('utf-8'))


def show_dms(client_socket, username):

    # TODO: bug - only shows first dm from each person

    message_to_send = 'DMs received while offline: \n'

    with open('directmessages.txt') as f:
        dm = json.load(f)

    for message in dm:
        data = message.split('||||')
        if data[3] == username:
            message_to_send += "{0} ({1}): {2} \n".format(data[0], data[1], data[2])
            dm.remove(message)

    client_socket.send(message_to_send.encode('utf-8'))

    with open('directmessages.txt', 'w') as outfile:
        json.dump(dm, outfile)
