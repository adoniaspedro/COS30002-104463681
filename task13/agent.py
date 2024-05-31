import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path
#from random import uniform

AGENT_MODES = {
	pyglet.window.key._1: 'seek',
	pyglet.window.key._2: 'arrive_slow',
	pyglet.window.key._3: 'arrive_normal',
	pyglet.window.key._4: 'arrive_fast',
	pyglet.window.key._5: 'flee',
	pyglet.window.key._6: 'pursuit',
	pyglet.window.key._7: 'follow_path',
	pyglet.window.key._8: 'wander',
}

class Agent(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
		'slow': 0.9,
		### ADD 'normal' and 'fast' speeds here
		'normal': 0.5,
  		'fast': 1.0,	
	}

	def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
		# keep a reference to the world object
		self.world = world
		self.mode = mode
		# where am i and where am i going? random start pos
		dir = radians(random()*360)
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.force = Vector2D()  # current steering force
		self.accel = Vector2D() # current acceleration due to force
		self.mass = mass

		# data for drawing this agent
		self.color = 'ORANGE'
		self.vehicle_shape = [
			Point2D(-10,  6),
			Point2D( 10,  0),
			Point2D(-10, -6)
		]
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

		# wander info render objects
		self.info_wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
		self.info_wander_target = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
		# add some handy debug drawing info lines - force and velocity
		self.info_force_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['BLUE'], batch=window.get_batch("info"))
		self.info_vel_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['AQUA'], batch=window.get_batch("info"))
		self.info_net_vectors = [
			ArrowLine(
				Vector2D(0,0), 
				Vector2D(0,0), 
				colour=COLOUR_NAMES['GREY'], 
				batch=window.get_batch("info")
			),
			ArrowLine(
				Vector2D(0,0), 
				Vector2D(0,0), 
				colour=COLOUR_NAMES['GREY'], 
				batch=window.get_batch("info")
			),
		]

		### path to follow?
		self.path = Path()
		self.randomise_path()
		self.waypoint_threshold = 10.0

		### wander details
		# NEW WANDER INFO
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
		# Force and speed limiting code
		self.max_speed = 20.0 * scale
		self.max_force = 500.0

		# limits?
		self.max_speed = 20.0 * scale
		## max_force ??

		# debug draw info?
		self.show_info = False
	def randomise_path(self):
		cx = self.world.cx  #width
		cy = self.world.cy  #height
		margin = min(cx, cy) * 1/6  #Used for padding
		#self.path.create_random_path(5, 0, 0, cx, cy)
		self.path.create_random_path(5, margin, margin, cx-margin, cy-margin)
	
       
	def follow_path(self):
		WaypointNearDist = 3 #System setting
		
  		#If heading to final point, return a slow down force vector (Arrive)
		if self.path.is_finished():				
			return self.arrive(self.path.end_point)
		else:
			#If within threshold distance of current way point, move to the next
			if self.pos.distance(self.path.current_pt()) < WaypointNearDist:
					#self.path.next_waypoint()
					self.path.add_way_pt(self.path.current_pt())

			#If not at the end of the path, return a force vector to head to 
   			#current point at full speed (Seek)
			if not self.path.is_finished():
					return self.seek(self.path.current_pt())
			else:
				#return a slow down force vector
				return self.arrive(self.path.end_point)
	

	def calculate(self, delta):
		# calculate the current steering force
		mode = self.mode
		target_pos = Vector2D(self.world.target.x, self.world.target.y)
		if mode == 'seek':
			force = self.seek(target_pos)
		elif mode == 'arrive_slow':
			force = self.arrive(target_pos, 'slow')
		elif mode == 'arrive_normal':
			force = self.arrive(target_pos, 'normal')
		elif mode == 'arrive_fast':
			force = self.arrive(target_pos, 'fast')
		elif mode == 'flee':
			force = self.flee(target_pos)
		elif mode == 'pursuit':
			force = self.pursuit(self.world.hunter)
		elif mode == 'wander':
			force = self.wander(delta)
		elif mode == 'follow_path':
			force = self.follow_path()
		elif mode == 'hide':
			force = self.hide()
		else:
			force = Vector2D()
		self.force = force
		return force

	def update(self, delta):
		''' update vehicle position and orientation '''
		# calculate and set self.force to be applied
		force = self.calculate(delta)  # <-- delta needed for wander
		# limit force for wander
		force.truncate(self.max_force) 
		# determine the new acceleration
		self.accel = force / self.mass  # not needed if mass = 1.0
		# new velocity
		self.vel += self.accel * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading if non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
		self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
		self.vehicle.rotation = -self.heading.angle_degrees()

		s = 0.5 # <-- scaling factor
		# force
		self.info_force_vector.position = self.pos
		self.info_force_vector.end_pos = self.pos + self.force * s
		# velocity
		self.info_vel_vector.position = self.pos
		self.info_vel_vector.end_pos = self.pos + self.vel * s
		# net (desired) change
		self.info_net_vectors[0].position = self.pos+self.vel * s
		self.info_net_vectors[0].end_pos = self.pos + (self.force+self.vel) * s
		self.info_net_vectors[1].position = self.pos
		self.info_net_vectors[1].end_pos = self.pos + (self.force+self.vel) * s

	def speed(self):
		return self.vel.length()

	#--------------------------------------------------------------------------

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

	def flee(self, hunter_pos):
		''' move away from hunter position '''
		panic_distance = 100  # panic distance adjust as needed

        # Calculate the vector from the hunter to the agent
		to_hunter = self.pos - hunter_pos

        # Check if the agent is within the panic distance
		if to_hunter.length() < panic_distance:
            # Calculate the desired velocity to move away from the hunter
			desired_vel = to_hunter.normalise() * self.max_speed
			return (desired_vel - self.vel)
        
        # If the agent is not within the panic distance, do not change velocity
		return Vector2D()
	
	def arrive(self, target_pos, speed):
		''' this behaviour is similar to seek() but it attempts to arrive at
			the target position with a zero velocity'''
		decel_rate = self.DECELERATION_SPEEDS[speed]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

	def pursuit(self, evader):
		''' this behaviour predicts where an agent will be in time T and seeks
			towards that point to intercept it. '''
		## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
		return Vector2D()

	def wander(self, delta):
		''' Random wandering using a projected jitter circle. '''
		wt = self.wander_target
		# this behaviour is dependent on the update rate, so this line must
		# be included when using time independent framerate.
		jitter_tts = self.wander_jitter * delta # this time slice
		# first, add a small random vector to the target's position
		wt += Vector2D(uniform(-1,1) * jitter_tts, uniform(-1,1) * jitter_tts)
		# re-project this new vector back on to a unit circle
		wt.normalise()
		# increase the length of the vector to the same as the radius
		# of the wander circle
		wt *= self.wander_radius
		# move the target into a position WanderDist in front of the agent
		target = wt + Vector2D(self.wander_dist, 0)
		# project the target into world space
		wld_target = self.world.transform_points(target, self.pos, self.heading, self.side, self.scale)
		# and steer towards it
		return self.seek(wld_target) 

	def find_hiding_spots(self):
		hiding_spots = []
		for obj in self.world.objects:
			if obj != self and obj != self.world.hunter and obj.pos is not None and self.world.hunter is not None and self.world.hunter.pos is not None:
				# Calculate the hiding spot behind the object
				hiding_spot = obj.pos + (obj.pos - self.world.hunter.pos).normalise() * (obj.radius + self.bRadius + 10)
				hiding_spots.append(hiding_spot)
		return hiding_spots	

	def evaluate_hiding_spots(self, hiding_spots):
		best_spot = None
		best_distance = float('inf')
		for spot in hiding_spots:
			distance = spot.distance(self.pos)
			if distance < best_distance:
				best_distance = distance
				best_spot = spot
		return best_spot

	def hide(self):
		hiding_spots = self.find_hiding_spots()
		target_pos = self.evaluate_hiding_spots(hiding_spots)
		if target_pos is not None:
			return self.seek(target_pos)
		else:
			return Vector2D()