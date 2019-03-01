# -*- coding: utf-8 -*-

import os
import pygame
import time
import sys
import random
import signal

from TouchMouse import TouchMouse
from LedCircle import LedCircle
from UI import *

ratio = 480 / 320
width = 480
height = 320

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

class pyscope:
	screen = None
	def __init__(self):
		self.mouse = TouchMouse()
		self.ledCircle = LedCircle()
		self.ledCircle.start()

		self.init_screen()
		self.init_font()

		self.keyboard = VirtualKeyBoard(self.screen)
		self.settings = SettingsScreen(self.screen, config)
		self.inbox = Inbox(self.screen, config, self.ledCircle)
		self.current_screen = self.settings

		# self.screen_state = ScreenState.SETTINGS
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

	def close(self):
		self.ledCircle.stop()

	def update(self):
		self.current_screen.update()

		ev = self.mouse.getEvents()
		for event in ev:
			if event == 'MOUSEMOTION':
				self.pos = (int(self.mouse.getX()), int(self.mouse.getY()))
				# print(self.pos)
			if event == 'MOUSEDOWN':
				self.current_screen.mouse_down(int(self.mouse.getX()), int(self.mouse.getY()))

	def draw(self):
		self.update()
		self.screen.fill((0, 0, 0))

		message = ''

		self.current_screen.draw()

		if True:
			textsurface = self.font.render('x', False, (255, 255, 255))
			self.screen.blit(textsurface,(int(self.mouse.getX()) - 10 , int(self.mouse.getY()) - 16))

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


scope = pyscope()
while 1:
	scope.draw()
	time.sleep(0.1)
