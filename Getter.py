import requests
import threading
import time

class Getter(threading.Thread):

	def __init__(self):
		super(Getter, self).__init__()
		self.daemon = True
		self.url = "http://benjaminloriot.com/anto"
		self.resp = {};
		self.update()

	def run(self):
		while(1):
			self.update()
			time.sleep(30)

	def update(self):
		r = requests.get(self.url + '/get.php?user=benjamin');
		self.resp = r.json()

	def get(self):
		return self.resp
