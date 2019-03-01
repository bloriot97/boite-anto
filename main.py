import os
import pygame
import time
import sys
import random
import signal
from enum import Enum

from TouchMouse import TouchMouse
from LedCircle import LedCircle
from Getter import Getter

ratio = 480 / 320
width = 480
height = 320

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

api_ip= config['TEST']['api_ip']
api_port = config['TEST']['api_port']
username = config['TEST']['username']
password = config['TEST']['password']

class ScreenState(Enum):
	READING = 1
	WAITING = 2

class pyscope:
	screen = None
	def __init__(self):
		self.mouse = TouchMouse()
		self.ledCircle = LedCircle()
		self.ledCircle.start()
		self.getter = Getter(api_ip, api_port, username, password)
		self.getter.start()

		self.init_screen()
		self.init_font()

		self.screen_state = ScreenState.WAITING
		self.message = ''
		self.newMessage = False;
		self.ledCircle.animation = 'off'

	def init_font(self):
		pygame.font.init()
		self.font = pygame.font.SysFont('Comic Sans MS', 32)

	def init_screen(self):
		disp_no = os.getenv('DISPLAY')
		if disp_no:
			print 'Running under X server {0}'.format(disp_no)
		drivers = ['svgalib', 'directfb', 'fbcon']
		found = False
		os.putenv('SDL_FBDEV', '/dev/fb1')
		os.putenv('TSLIB_FBDEV', '/dev/fb1')
		for driver in drivers:
			if not os.getenv('SDL_VIDEODRIVER'):
				os.putenv('SDL_VIDEODREIVER', driver);
			try:
				pygame.display.init()
			except pygame.error:
				print 'Driver: {0} failed'.format(driver)
				continue
			found = True
			break

		if not found:
			print 'No suitable driver'
		size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
		print 'FRAMEBUFFER size = {0}x{1}'.format(size[0], size[1])
		self.screen = pygame.display.set_mode(size,  pygame.NOFRAME)
		self.screen.fill((0, 0, 0))

		pygame.display.update()
		self.pos = (0,0)
		pygame.mouse.set_visible(False)

	def __del__(self):
		#self.ledCircle.stop()
		print 'close'

	def update_inbox(self, force_update=False):
		#TODO : update new getter
		self.inbox = self.getter.get_inbox(force_update=force_update);

	def drawText(self, surface, text, color, font, aa=False, bkg=None):
		y = 10
		lineSpacing = -2

		# get the height of the font
		fontHeight = font.size('Tg')[1]

		while text:
			i = 1

			# determine if the row of text will be outside our area
			if y + fontHeight > 320:
				break

			# determine maximum width of line
			while font.size(text[:i])[0] < 480 and i < len(text):
				i += 1

			# if we've wrapped the text, then adjust the wrap to the last word
			if i < len(text):
				i = text.rfind(' ', 0, i) + 1

			# render the line and blit it to the surface
			if bkg:
				image = font.render(text[:i], 1, color, bkg)
				image.set_colorkey(bkg)
			else:
				image = font.render(text[:i], aa, color)

			surface.blit(image, (0, y))
			y += fontHeight + lineSpacing

			# remove the text we just blitted
			text = text[i:]

		return text

	def close(self):
		self.ledCircle.stop()

	def pop_message(self):
		self.message = self.getter.pop_message()
		self.update_inbox(force_update=True)
		return self.message

	def update(self):
		self.update_inbox()

		ev = self.mouse.getEvents()
		for event in ev:
			if event == 'MOUSEMOTION':
				self.pos = (int(self.mouse.getX()), int(self.mouse.getY()))
				print(self.pos)
			if event == 'MOUSEDOWN':
				if self.screen_state == ScreenState.WAITING:
					if len(self.inbox) > 0:
						self.screen_state = ScreenState.READING
						self.pop_message()
				elif self.screen_state == ScreenState.READING:
					if len(self.inbox) > 0:
						self.pop_message()
					else:
						self.screen_state = ScreenState.WAITING


	def draw(self):
		self.update()
		self.screen.fill((0, 0, 0))

		message = ''

		if self.screen_state == ScreenState.WAITING:
			if len(self.inbox) > 0:
				message = 'Vous avez %s nouveaux messages' % str(len(self.inbox))
				self.ledCircle.animation = self.inbox[0]['animation']
				self.drawText(self.screen, message, (255, 255, 255), self.font)
			else:
				self.ledCircle.animation = 'off'
		elif self.screen_state == ScreenState.READING:
			message = self.message['content'] + '(' + str(len(self.inbox)) + ')'
			self.drawText(self.screen, message, (255, 255, 255), self.font)

		#textsurface = self.font.render(self.message, False, (255, 255, 255))
		#self.screen.blit(textsurface,((width-textsurface.get_width())/2 ,(height - textsurface.get_height())/2))
		pygame.display.update()

out = open('out.log', 'w')
#sys.stdout = out
err = open('err.log', 'w')
#sys.stderr = err

def fermer_programme(signal, frame):
	sys.__stdout__.write('\nFermeture par interuption!\n')
	print('\nFermeture par interuption!\n')
	global scope
	scope.close()
	del scope
	out.close()
	err.close()
	sys.exit(0)

signal.signal(signal.SIGINT, fermer_programme)


print('test')

scope = pyscope()
while 1:
	scope.draw()
	time.sleep(0.1)
