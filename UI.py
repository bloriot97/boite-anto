from enum import Enum
import pygame
from Getter import Getter

class InboxState(Enum):
	READING = 1
	WAITING = 2

class Vector2():
	def __init__(self, x, y):
		self.x = x
		self.y = y

class UIElement:

	def __init__(self, surface):
		self.surface = surface
		self.font = pygame.font.SysFont('Comic Sans MS', 32)
		self.font_big = pygame.font.SysFont('Comic Sans MS', 80)

	def update(self):
		pass

	def drawText(self, text, color, font, aa=False, bkg=None):
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

			self.surface.blit(image, (0, y))
			y += fontHeight + lineSpacing

			# remove the text we just blitted
			text = text[i:]

		return text

	def mouse_down(self, x, y):
		pass

	def draw(self):
		pass

class VirtualKeyBoard(UIElement):

	def __init__(self, surface):
		UIElement.__init__(self, surface)
		self.font_size = 60
		self.buffer_font_size = 32
		self.key_font = pygame.font.SysFont('Comic Sans MS', self.font_size)
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

	def draw(self):
		UIElement.draw(self)
		for line_id, line in enumerate(self.lines):
			for char_id, char in enumerate(line):
				textsurface = self.key_font.render(char, False, (255, 255, 255))
				self.surface.blit(textsurface, (self.pos.x + self.key_size.x * char_id, self.pos.y + self.key_size.y * line_id))
		textsurface = self.buffer_font.render(self.buffer, False, (255, 255, 255))
		self.surface.blit(textsurface, (self.buffer_pos.x , self.buffer_pos.y))

	def get_key_pressed(self, x, y):
		key_x = int( ( x - self.pos.x ) / self.key_size.x )
		key_y = int( ( y - self.pos.y ) / self.key_size.y )

		if key_y < len(self.lines) and key_y >= 0:
			line = self.lines[key_y]
			if key_x < len(line) and key_x >= 0:
				return line[key_x]
		return None

	def mouse_down(self, x, y):
		UIElement.mouse_down(self, x, y)
		self.last_key_pressed = self.get_key_pressed(x, y)
		if self.last_key_pressed and self.last_key_pressed not in '^<':
			self.buffer += self.last_key_pressed
		elif self.last_key_pressed == '<':
			self.buffer = self.buffer[:-1]

class SettingsScreen(UIElement):

	def __init__(self, surface, config):
		UIElement.__init__(self, surface)
		self.config = config

	def draw(self):
		UIElement.draw(self)
		env = 'TEST'
		line_height = 40
		settings = self.config[env]
		for index, key in enumerate(settings):
			textsurface = self.font.render(key, False, (255, 255, 255))
			self.surface.blit(textsurface,( 10 , 10 + index * line_height))
			textsurface = self.font.render(settings[key], False, (255, 255, 255))
			self.surface.blit(textsurface,( 200 , 10 + index * line_height))

class Inbox(UIElement):
	def __init__(self, surface, config, ledCircle):
		UIElement.__init__(self, surface)
		api_ip = config['TEST']['api_ip']
		api_port = config['TEST']['api_port']
		username = config['TEST']['username']
		password  = config['TEST']['password']
		self.state = InboxState.WAITING
		self.getter = Getter(api_ip, api_port, username, password)
		self.getter.start()
		self.ledCircle = ledCircle
		pass

	def update_inbox(self, force_update=False):
		#TODO : update new getter
		self.inbox = self.getter.get_inbox(force_update=force_update)

	def mouse_down(self, x, y):
		UIElement.mouse_down(self, x, y)
		if self.state == InboxState.WAITING:
			if len(self.inbox) > 0:
				self.state = InboxState.READING
				self.pop_message()
		elif self.state == InboxState.READING:
			if len(self.inbox) > 0:
				self.pop_message()
			else:
				self.state = InboxState.WAITING

	def pop_message(self):
		self.message = self.getter.pop_message()
		self.update_inbox(force_update=True)
		return self.message

	def update(self):
		UIElement.update(self)
		self.update_inbox()

	def draw(self):
		UIElement.draw(self)
		if self.state == InboxState.WAITING:
			if len(self.inbox) > 0:
				message = 'Vous avez %s nouveaux messages' % str(len(self.inbox))
				self.ledCircle.animation = self.inbox[0]['animation']
				self.drawText(message, (255, 255, 255), self.font)
			else:
				self.ledCircle.animation = 'off'
		elif self.state == InboxState.READING:
			message = self.message['content'] + '(' + str(len(self.inbox)) + ')'
			self.drawText(message, (255, 255, 255), self.font)
