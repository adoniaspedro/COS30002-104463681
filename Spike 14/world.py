from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from pyglet.window import key
from graphics import COLOUR_NAMES, window
from agent import Agent, AGENT_MODES  # Agent with seek, arrive, flee and pursuit
from pyglet.text import Label

class World(object):

	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.target = Vector2D(cx / 2, cy / 2)
		self.hunter = None
		self.agents = []
		self.display_labels = []# Initialise display_labels as an empty list
		self.paused = True
		self.show_info = True
		self.target = pyglet.shapes.Star(
			cx / 2, cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")
		)
		window.push_handlers(self.on_key_press)
		self.display_label = pyglet.text.Label('', x=10, y=self.cy - 20)
  
		# Create labels
		self.cohesion_label = Label('Cohesion Weight: ', x=10, y=cy - 20)
		self.neighbour_distance_label = Label('Neighbour Distance: ', x=10, y=cy - 40)
  
		# Create a label to display parameter values
		self.parameter_label = pyglet.text.Label(
            text=self.get_parameter_text(),
            x=10, y=cy - 10,
            anchor_x='left', anchor_y='top',
            multiline=True,
            width=cx // 3,
            batch=window.get_batch("info")
        )
  
	def wrap_around(self, pos):
		if pos.x > self.cx:
			pos.x = 0.0
		elif pos.x < 0:
			pos.x = self.cx

		if pos.y > self.cy:
			pos.y = 0.0
		elif pos.y < 0:
			pos.y = self.cy
   
	def get_parameter_text(self):
		if not self.agents:
			#return "No agents available."
			#return f"Cohesion Weight: {agent_params['cohesion_weight']}\n"
			return " "
		agent_params = self.agents[0].get_steering_parameters()
		return (
            f"Cohesion Weight: {agent_params['cohesion_weight']}\n"
            f"Separation Weight: {agent_params['separation_weight']}\n"
            f"Alignment Weight: {agent_params['alignment_weight']}\n"
            f"Wander Weight: {agent_params['wander_weight']}\n"
            f"Neighbour Distance: {agent_params['neighbour_distance']}"
        )
  
	def update_parameter_label(self):
		self.parameter_label.text = self.get_parameter_text()

	def get_neighbours(self, agent, radius):
		return [a for a in self.agents if (a.pos - agent.pos).lengthSq() < (radius * radius)]

	def update(self, delta):
		if not self.paused:
			for agent in self.agents:
				agent.update(delta)
    
    
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
		if symbol == pyglet.window.key.SPACE:
			for i in range(0, 3):
				self.agents.append(Agent (self))
		elif symbol in AGENT_MODES:
			for agent in self.agents:
				agent.mode = AGENT_MODES[symbol]
    
		 # New keyboard input for adjusting parameters
		elif symbol == pyglet.window.key.C:
			for agent in self.agents:
				agent.set_steering_parameters(cohesion_weight=1.0, separation_weight=1.5, alignment_weight=1.0, wander_weight=0.5)
			# Create a label to display
			label = pyglet.text.Label('C key pressed', x=10, y=self.cy - 20)
    		# Add the label to the list of labels to display
			self.display_labels.append(label)
		elif symbol == pyglet.window.key.N:
			for agent in self.agents:
				agent.set_neighbour_distance(50.0)
		elif symbol == pyglet.window.key.NUM_1:
			for agent in self.agents:
				agent.set_steering_parameters(cohesion_weight=2.0, separation_weight=1.0, alignment_weight=1.0, wander_weight=0.5)
		elif symbol == pyglet.window.key.NUM_2:
			for agent in self.agents:
				agent.set_neighbour_distance(100.0)
    
	def on_key_press(self, symbol, modifiers):
		if symbol == pyglet.window.key.R:
			for agent in self.agents:
				agent.randomise_path()
    
		if symbol == pyglet.window.key.I:
			self.show_info = not self.show_info

		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
		
  		#If statement for 'C' Key
		if symbol == key.C:
			if self.agents:
				for agent in self.agents:
					#agent.set_steering_parameters(cohesion_weight=1.0, separation_weight=1.5, alignment_weight=1.0, wander_weight=0.5)
					parameters = agent.get_steering_parameters()
					#parameters['cohesion_weight'] += 0.1
					parameters = {'cohesion_weight': agent.get_steering_parameters()['cohesion_weight'] + 0.1}
					agent.set_steering_parameters(**parameters)
				# Update cohesion label
				self.cohesion_label.text = f'Cohesion Weight: {self.agents[0].get_steering_parameters()["cohesion_weight"]}'
				print('\nC key was pressed')
				print(self.cohesion_label.text)
				self.agents[0].display_current_parameters()
				# Display on program window
				self.display_label = pyglet.text.Label(self.cohesion_label.text, x=10, y=self.cy - 20)
		
  		#If statement for 'N' Key
		elif symbol == key.N:
			if self.agents:
				for agent in self.agents:
					agent.set_neighbour_distance(50.0)
				# Update neighbour distance label
				self.neighbour_distance_label.text = f'Neighbour Distance: {self.agents[0].get_neighbour_distance()}'
				print('\nN key was pressed')
				print(self.neighbour_distance_label.text)
				self.agents[0].display_current_parameters()
				# Display on program window
				self.display_label = pyglet.text.Label(self.neighbour_distance_label.text, x=10, y=self.cy - 40)
    
		# Increase separation weight when 'S' is pressed
		elif symbol == key.S:
			if self.agents:
				for agent in self.agents:
					parameters = agent.get_steering_parameters()
					#parameters['separation_weight'] += 0.1
					parameters = {'separation_weight': agent.get_steering_parameters()['separation_weight'] + 0.1}
					agent.set_steering_parameters(**parameters)
				print('\nS key was pressed')
				print(f'Added Separation Weight: {self.agents[0].get_steering_parameters()["separation_weight"]}')
				# Display on program window
				self.display_label = pyglet.text.Label(f'Added Separation Weight: {self.agents[0].get_steering_parameters()["separation_weight"]}', x=10, y=self.cy - 60)


    	# Increase alignment weight when 'A' is pressed
		elif symbol == key.A:
			if self.agents:
				for agent in self.agents:
					parameters = agent.get_steering_parameters()
					#parameters['alignment_weight'] += 0.1
					parameters = {'alignment_weight': agent.get_steering_parameters()['alignment_weight'] + 0.1}
					agent.set_steering_parameters(**parameters)
				print('\nA key was pressed')
				print(f'Added Alignment Weight: {self.agents[0].get_steering_parameters()["alignment_weight"]}')
    			# Display on program window
				self.display_label = pyglet.text.Label(f'Added Alignment Weight: {self.agents[0].get_steering_parameters()["alignment_weight"]}', x=10, y=self.cy - 80)
	
	def draw(self):
        # Draw the labels
		self.cohesion_label.draw()
		self.neighbour_distance_label.draw()
  
	def on_draw(self):
        # Clear the window
		self.clear()
        
        # Draw all agents
		for agent in self.agents:
			agent.draw()
			agent.draw_steering_forces()
			self.display_label.draw()
   
		# Draw the labels
		self.draw()

		self.display_label.draw()
    	
	#window.push_handlers(on_key_press)
cx = 800  
cy = 600 
world = World(cx, cy)        
pyglet.clock.schedule_interval(world.update, 1/60.0)
