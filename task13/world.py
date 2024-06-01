from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent, AGENT_MODES  # Agent with seek, arrive, flee and pursuit

class obstacles(object):
	def __init__(self, x=0, y=0, rad=0):
		self.x = x
		self. y = y
		self.pos = Vector2D(x, y)
		self.radius = rad
		self.shape = pyglet.shapes.Circle(self.x, self. y,
		self.radius, segments=30,
		color=COLOUR_NAMES['RED'],
		batch=window.get_batch('main'))
		

class World(object):

	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.target = Vector2D(cx / 2, cy / 2)
		self.hunter = None
		self.agents = []
		self.paused = True
		self.show_info = True
		self.target = pyglet.shapes.Star(
			cx / 2, cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")
		)
		self.circles = []
		self.objects = self.objects = [obstacles(100, 100, 50), obstacles(700, 100, 50), obstacles(100, 700, 50), obstacles(700, 700, 50)]


	def update(self, delta):
		if not self.paused:
			for agent in self.agents:
				agent.update(delta)

	def wrap_around(self, pos):
		''' Treat world as a toroidal space. Updates parameter object pos '''
		max_x, max_y = self.cx, self.cy
		if pos.x > max_x:
			pos.x = pos.x - max_x
		elif pos.x < 0:
			pos.x = max_x - pos.x
		if pos.y > max_y:
			pos.y = pos.y - max_y
		elif pos.y < 0:
			pos.y = max_y - pos.y

	def transform_points(self, points, pos, forward, side, scale):
		''' Transform the given list of points, using the provided position,
			direction and scale, to object world space. '''
		# make a copy of original points (so we don't trash them)
		wld_pts = points.copy()
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform all the points (vertices)
		mat.transform_vector2d_list(wld_pts)
		# done
		return wld_pts

	def input_mouse(self, x, y, button, modifiers):
		if button == 1:  # left
			self.target.x = x
			self.target.y = y
	
	def input_keyboard(self, symbol, modifiers):
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
		if symbol == pyglet.window.key.A:
			self.agents.append(Agent(self))
		if symbol == pyglet.window.key.H:
			self.hunter = Agent(self)
			self.hunter.mode = 'wander'
			self.hunter.color = COLOUR_NAMES['RED']
			self.agents.append(self.hunter)
		#Pressing J will create a new agent that will hide from the hunter
		if symbol == pyglet.window.key.J:
			self.prey = Agent(self)
			self.prey.mode = 'hide'
			self.prey.color = COLOUR_NAMES['BLUE']
			self.agents.append(self.prey)
		elif symbol in AGENT_MODES:
			for agent in self.agents:
				agent.mode = AGENT_MODES[symbol]
    
	def on_key_press(self, symbol):
		if symbol == pyglet.window.key.R:
			for agent in self.agents:
				agent.randomise_path()
