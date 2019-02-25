import random
import sys
from threading import Thread
import time
from datetime import datetime

import requests

class Client():
    period = 5

    def  __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.inbox = []
        self.shut_down = False
        self.connected = False

    def get_uri(self, path):
        return f'http://{self.ip}:{self.port}/api/v1{path}'

    def add_headers(args):
        if 'headers' in args:
            args['headers'] = {
                **headers,
                **self.get_headers()
            }
        else:
            args['headers'] = self.get_headers()
        return args

    def send_post(self, endpoint, **args):
        return requests.post(
            self.get_uri(endpoint),
            **add_headers(args)
        )

    def send_message(self, to, messages, animation='rainbow'):
        post_data = {
            'to': to,
            'content': messages,
            'animation': animation
        }
        r = self.send_post('/messages', data=post_data)
        return r.status_code


    def login(self, username, password):
        post_data = {
            'username': username,
            'password': password
        }
        r = self.send_post(
            '/auth/login',
            data = post_data
        )
        parsed_res = r.json()
        if parsed_res['status'] == 'success':
            self.token = parsed_res['token']
            self.connected = True
        return self.connected

    def disconnect(self):
        self.shut_down = True
        self.token = ''
        self.connected = False

    def get_inbox(self):
        self.checkout_inbox()
        return self.inbox

    def get_last_update(self):
        return self.last_update

    def read_message(self, id):
        r = requests.get(self.get_uri(f'/messages/read/{id}'),
            headers = self.get_headers()
        )
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            self.connected = False
            return False
        return False

    def pop_message(self):
        message_info = self.get_inbox().pop()
        return self.read_message(message_info['_id'])

    def get_headers(self):
        headers = {}
        if self.connected:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def checkout_inbox(self):
        r = requests.get(self.get_uri('/messages/inbox'),
            headers = self.get_headers()
        )
        if r.status_code == 200:
            parsed_res = r.json()
            self.inbox = parsed_res
            self.last_update = datetime.now()
            return True
        elif r.status_code == 401:
            self.connected = False
            return False
        return False
