import unittest
import time
import requests

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

from Client import Client
from Getter import Getter

api_ip= config['TEST']['api_ip']
api_port = config['TEST']['api_port']
username = config['TEST']['username']
password = config['TEST']['password']

class TestClient(unittest.TestCase):
    def test_login_disconnect(self):
        """
        Test if the client can connect and disconnect
        """
        c = Client(api_ip ,api_port)
        self.assertTrue(c.login(username, password))
        c.disconnect()

    def test_checkout_inbox(self):
        c = Client(api_ip ,api_port)
        c.login(username, password)
        self.assertTrue(c.checkout_inbox())
        c.disconnect()

    def test_send_message(self):
        c = Client(api_ip ,api_port)
        c.login(username, password)
        inbox_len = len(c.get_inbox())
        self.assertEqual(c.send_message(username, 'message'), 200)
        self.assertEqual(inbox_len + 1, len(c.get_inbox()))
        c.disconnect()

    def test_pop_message(self):
        c = Client(api_ip ,api_port)
        c.login(username, password)
        c.send_message(username, 'message')
        inbox_len = len(c.get_inbox())
        c.pop_message()
        new_inbox_len = len(c.get_inbox())
        self.assertEqual(inbox_len - 1, new_inbox_len)
        c.disconnect()

class TestGetter(unittest.TestCase):
    def test_integration(self):
        c = Client(api_ip ,api_port)
        c.login(username, password)
        c.send_message(username, 'message')
        g = Getter(api_ip, api_port, username, password)
        g.start()
        time.sleep(g.get_period())
        self.assertGreater(len(g.get_inbox()), 0)


if __name__ == '__main__':
    unittest.main()
