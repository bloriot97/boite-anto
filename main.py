# -*- coding: utf-8 -*-

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
password  = config['TEST']['password']

class ScreenState(Enum):
	READING = 1
	WAITING = 2
	SETTINGS = 3
	WRITTING = 4

class Vector2():
	def __init__(self, x, y):
		self.x = x
		self.y = y

class VirtualKeyBoard:


	def __init__(self):
		self.font_size = 60
		self.buffer_font_size = 32
		self.font = pygame.font.SysFont('Comic Sans MS', self.font_size)
		self.buffer_font = pygame.font.SysFont('Comic Sans MS', self.buffer_font_size)
		self.caps = False
		self.lines = [
			'0123456789',
			'azertyuiop',
			'qsdfghjklm',
			'^wxcvbn@.<'
		]
		self.pos = Vector2(10, 60)
		self.buffer_pos = Vector2(13, 15)
		self.key_size = Vector2(self.font_size * 0.8, self.font_size * 0.8)
		self.buffer = ''
		self.last_key_pressed = ''

	def clear(self):
		self.buffer = ''
		return self.buffer

	def get_buffer(self):
		return self.buffer

	def clear(self):
		self.buffer = ''

	def draw(self, surface):
		for line_id, line in enumerate(self.lines):
			for char_id, char in enumerate(line):
				textsurface = self.font.render(char, False, (255, 255, 255))
				surface.blit(textsurface, (self.pos.x + self.key_size.x * char_id, self.pos.y + self.key_size.y * line_id))
		textsurface = self.buffer_font.render(self.buffer, False, (255, 255, 255))
		surface.blit(textsurface, (self.buffer_pos.x , self.buffer_pos.y))

	def get_key_pressed(self, x, y):
		key_x = int( ( x - self.pos.x ) / self.key_size.x )
		key_y = int( ( y - self.pos.y ) / self.key_size.y )

		if key_y < len(self.lines) and key_y >= 0:
			line = self.lines[key_y]
			if key_x < len(line) and key_x >= 0:
				return line[key_x]
		return None

	def mouse_down(self, x, y):
		self.last_key_pressed = self.get_key_pressed(x, y)
		if self.last_key_pressed and self.last_key_pressed not in '^<':
			self.buffer += self.last_key_pressed
		elif self.last_key_pressed == '<':
			self.buffer = self.buffer[:-1]

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

		self.keyboard = VirtualKeyBoard()

		self.screen_state = ScreenState.WRITTING
		self.message = ''
		self.newMessage = False;
		self.ledCircle.animation = 'off'

	def init_font(self):
		pygame.font.init()
		self.font = pygame.font.SysFont('Comic Sans MS', 32)
		self.font_big = pygame.font.SysFont('Comic Sans MS', 80)

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
				# print(self.pos)
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
				elif self.screen_state == ScreenState.WRITTING:
					self.keyboard.mouse_down(int(self.mouse.getX()), int(self.mouse.getY()))


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
		elif self.screen_state == ScreenState.SETTINGS:
			pass
		elif self.screen_state == ScreenState.WRITTING:
			self.keyboard.draw(self.screen)

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
