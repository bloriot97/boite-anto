import time
import threading
from neopixel import *
import random
import math

LED_COUNT      = 24      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

class LedCircle(threading.Thread):
	# LED strip configuration:



	def __init__(self):
		super(LedCircle, self).__init__()
		self.daemon = True
		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
		self.strip.begin()
		self.running = True
		self.animation = "rainbow"
		self.duration = 3
		self.delay = 0.01
		self.color = (52, 152, 219)
		self.color2 = (255, 0, 0)
		self.lastTime = time.time()
		self.temps = 0

	def wheel(self, pos):
		"""Generate rainbow colors across 0-255 positions."""
		if pos < 85:
			return Color(pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return Color(255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return Color(0, pos * 3, 255 - pos * 3)

	def stop(self):
		self.running = False
		time.sleep(0.1)
		for i in range(0, self.strip.numPixels()):
			self.strip.setPixelColor(i, Color(0,0,0))
		self.strip.show()
		print "close"

	def run(self):
		while self.running:
			percentage = 0
			dt = time.time() - self.lastTime
			self.lastTime = time.time()
			self.temps = ((self.temps + dt) % self.duration)
			percentage = self.temps / self.duration
			for i in range(0, self.strip.numPixels()):
				#self.strip.setPixelColor(i, Color(int(random.random() * 255),int(random.random() * 255), int(random.random() * 255)))
				if (self.animation == "rainbow"):
					j = int(percentage * 255)
					self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
				elif (self.animation == "off"):
					self.strip.setPixelColor(i, Color(0,0,0))
				elif (self.animation == "fade"):
					ratio = math.pow(math.sin(percentage*math.pi),2)
					r = int( ratio * self.color[0])
					g = int( ratio * self.color[1])
					b = int( ratio * self.color[2])
					self.strip.setPixelColor(i, Color(r,g,b))
				elif (self.animation == "pingpong"):
					ratio = math.pow(math.sin(percentage*math.pi),2)
					r = int( self.color[0])
					g = int( self.color[1])
					b = int( self.color[2])
					if (  ratio <= float(i) / LED_COUNT):
						self.strip.setPixelColor(i, Color(r,g,b))
					else:
						self.strip.setPixelColor(i, Color(self.color2[0],self.color2[1],self.color2[2]))

			self.strip.show()
			#time.sleep(self.delay)

if __name__ == "__main__":
	print("main")
	ledCircle = LedCircle()
	ledCircle.animation = "pingpong"
	ledCircle.color = (217, 20, 255)
	ledCircle.color2 = (157, 36, 255)
	ledCircle.duration = 20
	ledCircle.start()
	while 1:
		time.sleep(1)
