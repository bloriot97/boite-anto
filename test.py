import unittest
import time
import requests

from Client import Client

api_ip= '51.38.235.157'
api_port = '3003'
username = 'anto'
password = 'password'

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

    def test_pop_message(self):
        c = Client(api_ip ,api_port)
        c.login(username, password)

        c.checkout_inbox()
        c.disconnect()

if __name__ == '__main__':
    unittest.main()
