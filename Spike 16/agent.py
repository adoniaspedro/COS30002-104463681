'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by 
	Clinton Woodward <cwoodward@swin.edu.au>
	James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''
import cgi
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path

'''AGENT_MODES = {
	pyglet.window.key._1: 'seek',
	pyglet.window.key._2: 'arrive_slow',
	pyglet.window.key._3: 'arrive_normal',
	pyglet.window.key._4: 'arrive_fast',
	pyglet.window.key._5: 'flee',
	pyglet.window.key._6: 'pursuit',
	pyglet.window.key._7: 'follow_path',
	pyglet.window.key._8: 'wander',
}'''zz

class Agent(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
		'slow': 3,
		'normal': 1.5,
		'fast': 0.1
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
  
		self.path = Path()
		self.randomise_path()
		self.waypoint_threshold = 50

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
  
		self.flee_goal = pyglet.shapes.Star(0, 0, 10, 5, 4, 0, color=COLOUR_NAMES['YELLOW'], batch=window.get_batch('main'))
  
		# NEW WANDER INFO
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
    # Force and speed limiting code
		self.max_speed = 10.0 * scale
		self.max_force = 500.0
		## max_force ??

		# debug draw info?
		self.show_info = False

		 # draw wander info?
		if self.mode == 'wander':
		# calculate the center of the wander circle in front of the agent
			wnd_pos = Vector2D(self.wander_dist, 0)
			wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side) # draw the wander circle
		# draw the wander target (little circle on the big circle)
			wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
			wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)

		### path to follow?
		# self.path = ??

		### wander details
		# self.wander_?? ...

		
  
	def randomise_path(self):
		cx = self.world.cx
		cy = self.world.cy
		margin = min(cx, cy) * 1/6
		self.path.create_random_path(5, 0, 0, cx, cy)

	def calculate(self, delta):
		# calculate the current steering force
		to_target = self.world.hunter.pos - self.pos
		dist = to_target.length()
		if dist <= 600 and dist > 200:
			mode = 'hide'
		elif dist <= 200:
			mode = 'flee'
		else: mode = 'wander'

		if mode != 'hide':
			self.flee_goal.x = 0
			self.flee_goal.y = 0
		
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
			force = self.flee()
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
		## force = self.calculate()
		force = self.calculate(delta)  # <-- delta needed for wander
		force.truncate(self.max_force)
		## limit force? <-- for wander
		# ...
		# determin the new acceleration
		self.accel = force / self.mass  # not needed if mass = 1.0
		# new velocity
		self.vel += self.accel * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
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

	def flee(self):
		print('flee')
		hunter_pos = self.world.hunter.pos
		desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

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
		print('wander')
		''' random wandering using a projected jitter circle '''
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
		wld_target = self.world.transform_point(target, self.pos, self.heading, self.side) # and steer towards it
		return self.seek(wld_target)

	def follow_path(self):
		''' Follow a list of point2d which create a path. '''
		if self.path.is_finished():
			return self.arrive(self.path.current_pt(), 'slow')
		else:
			target_pos = self.path.current_pt()
			to_target = target_pos - self.pos
			dist = to_target.length()
			if dist < self.waypoint_threshold:
				self.path.inc_current_pt()
			return self.seek(self.path.current_pt())

	def GetHidingPosition(self, hunter, obj):
		DistFromBoundary = 30.0
		DistAway = obj.radius + DistFromBoundary

		ToObj = (obj.pos - hunter.pos).normalise()

		return (ToObj*DistAway)+obj.pos

	def VecDistanceSq(self, vec1, vec2):
		distance_sq = (vec1.x - vec2.x) ** 2 + (vec1.y - vec2.y) ** 2
		return distance_sq

	def hide(self):
		print('hide')
		DistToClosest = 1000000000
		BestHidingSpot = None

		for obj in self.world.objects:
			HidingSpot = self.GetHidingPosition(self.world.hunter ,obj)
			HidingDist = self.VecDistanceSq(HidingSpot, self.pos)
			if HidingDist < DistToClosest:
				DistToClosest = HidingDist
				BestHidingSpot = HidingSpot

		if BestHidingSpot:
			self.flee_goal.x = BestHidingSpot.x
			self.flee_goal.y = BestHidingSpot.y
			return self.arrive(BestHidingSpot, 'fast')

		print('flee from')
		return self.flee()
				
class Hunter(Agent):
	def __init__(self, world=None, scale=50.0, mass=3.0, mode='wander'):
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
		self.color = 'GREEN'
		self.vehicle_shape = [
			Point2D(-40,  24),
			Point2D( 20,  0),
			Point2D(-40, -24)
		]
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

		self.flee_rad = pyglet.shapes.Arc(
			self.pos.x, self.pos.y, 200, segments=30,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)
  
		self.hide_rad = pyglet.shapes.Arc(
			self.pos.x, self.pos.y, 600, segments=30,
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

		# NEW WANDER INFO
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
    # Force and speed limiting code
		self.max_speed = 2.5 * scale
		self.max_force = 500.0
		## max_force ??

		# debug draw info?
		self.show_info = False
  
		 # draw wander info?
		if self.mode == 'wander':
		# calculate the center of the wander circle in front of the agent
			wnd_pos = Vector2D(self.wander_dist, 0)
			wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side) # draw the wander circle
			#cgi.green_pen()
			#cgi.circle(wld_pos, self.wander_radius)
		# draw the wander target (little circle on the big circle)
			#cgi.red_pen()
			wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
			wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
			#cgi.circle(wld_pos, 3)

		### path to follow?
		# self.path = ??

		### wander details
		# self.wander_?? ...

		

	def calculate(self, delta):
		force = self.wander(delta)
		return force

	def update(self, delta):
		''' update vehicle position and orientation '''
		# calculate and set self.force to be applied
		## force = self.calculate()
		force = self.calculate(delta)  # <-- delta needed for wander
		force.truncate(self.max_force)
		## limit force? <-- for wander
		# ...
		# determin the new acceleration
		self.accel = force / self.mass  # not needed if mass = 1.0
		# new velocity
		self.vel += self.accel * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
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
  
		self.flee_rad.x = self.pos.x
		self.flee_rad.y = self.pos.y
		self.hide_rad.x = self.pos.x
		self.hide_rad.y = self.pos.y


	def speed(self):
		return self.vel.length()
    
	def wander(self, delta):
		''' random wandering using a projected jitter circle '''
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
		wld_target = self.world.transform_point(target, self.pos, self.heading, self.side) # and steer towards it
		return self.seek(wld_target)