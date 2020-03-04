import unittest

from setuptools.command.test import test

import server
import User
import Message
import socket
import json
from passlib.hash import pbkdf2_sha256
from time import ctime
import threading


"""
class ServerTest(unittest.TestCase):

    def test_login(self):
        self.server = server.create_socket()
        self.test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.test_socket.connect(('127.0.0.1', 5000))
        data = self.test_socket.recv(1024).decode('utf-8')
        self.assertEqual('connect', data)
"""


class UserTest(unittest.TestCase):

    def test_get_friends_list(self):
        list_one = User.get_all_friends()

        with open("friends.txt") as f:
            list_two = json.load(f)

        self.assertDictEqual(list_one, list_two)

    def test_get_user_list(self):
        list_one = User.get_user_list()

        with open('users.txt') as f:
            list_two = json.load(f)

        self.assertDictEqual(list_one, list_two)

    def test_get_passwords(self):
        list_one = User.get_passwords()

        with open('passwords.txt') as f:
            list_two = json.load(f)

        self.assertDictEqual(list_one, list_two)

    """
    def test_hash_password(self):
        password_one = User.hash_password('test')
        password_two = pbkdf2_sha256.hash('test')

        self.assertEqual(password_one, password_two)
    """

    def test_check_password(self):
        password_test = pbkdf2_sha256.hash('test')

        result_one = User.check_password(password_test, 'test')
        result_two = pbkdf2_sha256.verify('test', password_test)

        self.assertEqual(result_one, result_two)


class MessageTest(unittest.TestCase):

    def test_saving_messages(self):
        message = 'test'.encode('utf-8')
        time = ctime()[:16]
        Message.save_message('calum', message)

        with open('messages.txt') as f:
            recent_messages = json.load(f)

        self.assertEqual("calum||||" + time + "||||test", recent_messages[-1])

        del recent_messages[-1]
        with open('messages.txt', 'w') as outfile:
            json.dump(recent_messages, outfile)

    def test_saving_direct_messages(self):
        message = '||||'
        time = ctime()[:16]
        Message.save_direct_message('calum', 'joe', message)

        with open('directmessages.txt') as f:
            recent_dm = json.load(f)

        self.assertEqual("calum||||" + time + "||||" + message + "||||joe", recent_dm[-1])

        del recent_dm[-1]
        with open('directmessages.txt', 'w') as outfile:
            json.dump(recent_dm, outfile)


if __name__ == '__main__':
    unittest.main()
