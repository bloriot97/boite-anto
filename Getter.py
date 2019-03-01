import requests
import threading
import time
from Client import Client

class Getter(threading.Thread):
	period = 5

	def __init__(self, api_ip, api_port, username, password):
		super(Getter, self).__init__()
		self.daemon = True
		self.client = Client(api_ip, api_port)
		self.username = username
		self.password = password
		self.stop = False
		self.inbox = []
		self.client.login(self.username, self.password)

	def run(self):
		while not self.stop:
			self.update()
			time.sleep(self.period)

	def update(self):
		if self.client.connected:
			self.inbox = self.client.get_inbox()
		else:
			self.client.login(self.username, self.password)

	def is_connected(self):
		return self.client.connected

	def get_inbox(self, force_update=False):
		if force_update:
			self.update()
		return self.inbox

	def pop_message(self):
		res = self.client.pop_message()
		self.update()
		return res

	def get_period(self):
		return self.period
