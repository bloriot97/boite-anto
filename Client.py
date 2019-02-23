import random
import sys
from threading import Thread
import time
from datetime import datetime

import requests

class Client(Thread):
    period = 5

    def  __init__(self, ip, port):
        Thread.__init__(self)
        self.daemon = True
        self.ip = ip
        self.port = port
        self.inbox = []
        self.shut_down = False
        self.connected = False

    def get_uri(self, path):
        return f'http://{self.ip}:{self.port}/api/v1{path}'

    def login(self, username, password):
        post_data = {
            'username': username,
            'password': password
        }
        r = requests.post(self.get_uri('/auth/login'), data = post_data)
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
        return self.inbox

    def get_last_update(self):
        return self.last_update

    def read_message(self, id):
        pass

    def pop_message(self):
        pass

    def checkout_inbox(self):
        r = requests.get(self.get_uri('/messages/inbox'),
            headers = {'Authorization': f'Bearer {self.token}'}
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

    def run(self):
        """Code à exécuter pendant l'exécution du thread."""
        while not self.shut_down:
            if not self.connected:
                self.login()
            else:
                self.checkout_inbox()
            time.sleep(self.period)
