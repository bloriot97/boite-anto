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
		self.keyboard_surface = pygame.Surface((460, 300))
		self.show = False
		self.font_size = 60
		self.buffer_font_size = 32
		self.key_font = pygame.font.SysFont('Comic Sans MS', self.font_size)
		self.buffer_font = pygame.font.SysFont('Comic Sans MS', self.buffer_font_size)
		self.caps = False
		self.lines = [
			'0123456789',
			'azertyuiop',
			'qsdfghjklm',
			'^wxcvbn@.<',
			'       X V'
		]
		self.pos = Vector2(10, 10)
		self.buffer_pos = Vector2(3, 5)
		self.key_size = Vector2(self.font_size * 0.8, self.font_size * 0.8)
		self.buffer = ''
		self.last_key_pressed = ''
		self.input_field = None

	def edit(self, input_field):
		self.show = True
		self.input_field = input_field
		self.buffer = input_field.value

	def done_edit(self):
		self.input_field.update_value(self.buffer)
		self.show = False

	def cancel_edit(self):
		self.show = False

	def clear(self):
		self.buffer = ''
		return self.buffer

	def get_buffer(self):
		return self.buffer

	def clear(self):
		self.buffer = ''

	def draw(self):
		if self.show:
			UIElement.draw(self)
			self.keyboard_surface.fill((50, 50, 50))
			for line_id, line in enumerate(self.lines):
				for char_id, char in enumerate(line):
					textsurface = self.key_font.render(char, False, (255, 255, 255))
					self.keyboard_surface.blit(textsurface, (self.key_size.x * char_id, self.key_size.y * (line_id+1)))
			textsurface = self.buffer_font.render(self.buffer, False, (255, 255, 255))
			self.keyboard_surface.blit(textsurface, (self.buffer_pos.x , self.buffer_pos.y))
			self.surface.blit(self.keyboard_surface, (self.pos.x , self.pos.y))


	def get_key_pressed(self, x, y):
		key_x = int( ( x - self.pos.x ) / self.key_size.x )
		key_y = int( ( y - self.pos.y ) / self.key_size.y ) - 1

		if key_y < len(self.lines) and key_y >= 0:
			line = self.lines[key_y]
			if key_x < len(line) and key_x >= 0:
				return line[key_x]
		return None

	def mouse_down(self, x, y):
		if self.show:
			UIElement.mouse_down(self, x, y)
			self.last_key_pressed = self.get_key_pressed(x, y)
			if self.last_key_pressed == None:
				pass
			elif self.last_key_pressed == '<':
				self.buffer = self.buffer[:-1]
			elif self.last_key_pressed == 'X':
				self.cancel_edit()
			elif self.last_key_pressed == 'V':
				self.done_edit()
			elif self.last_key_pressed == ' ':
				pass
			else:
				self.buffer += self.last_key_pressed

class Button:
	def __init__(self):
		pass

class InputField:
	def __init__(self, value):
		self.value = value
		self.size = Vector2(200, 32)
		self.font = pygame.font.SysFont('Comic Sans MS', 32)
		self.surface = pygame.Surface((self.size.x, self.size.y))
		self.update_surface()

	def get_value(self):
		return self.value

	def update_value(self, value):
		self.value = value
		self.update_surface()
		return self.get_value()

	def is_mouse_in(self, x, y):
		return x >= 0 and y >= 0 and x <= self.size.x and y <= self.size.y

	def update_surface(self):
		textsurface = self.font.render(self.get_value(), False, (255, 255, 255))
		self.surface.fill((50, 50, 50))
		self.surface.blit(textsurface, (0, 0))
		return self.get_surface()

	def get_surface(self):
		return self.surface

class SettingsScreen(UIElement):

	def __init__(self, surface, config):
		UIElement.__init__(self, surface)
		self.config = config
		self.keyboard = VirtualKeyBoard(self.surface)
		self.typing = True
		self.env = 'TEST'
		self.line_height = 40
		self.settings = self.config[self.env]
		self.input_fields = {key:InputField(self.settings[key]) for key in self.settings}

	def mouse_down(self, x, y):
		self.keyboard.mouse_down(x, y)
		if not self.keyboard.show:
			for index, key in enumerate(self.settings):
				if self.input_fields[key].is_mouse_in(x - 200, y - (10 + index * self.line_height)):
					self.keyboard.edit(self.input_fields[key])

	def draw(self):
		UIElement.draw(self)
		for index, key in enumerate(self.settings):
			textsurface = self.font.render(key, False, (255, 255, 255))
			self.surface.blit(textsurface,( 10 , 10 + index * self.line_height))
			self.surface.blit(
				self.input_fields[key].get_surface(),
				(200 , 10 + index * self.line_height)
			)
		self.keyboard.draw()


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
