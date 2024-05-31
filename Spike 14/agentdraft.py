import pyglet
from vector2d import Vector2D, Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path

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
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        'normal': 0.5,
        'fast': 1.0,
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
        self.world = world
        self.mode = mode
        dir = radians(random() * 360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)
        self.force = Vector2D()
        self.accel = Vector2D()
        self.mass = mass

        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-10, 6),
            Point2D(10, 0),
            Point2D(-10, -6)
        ]
        self.vehicle = pyglet.shapes.Triangle(
            self.pos.x + self.vehicle_shape[1].x, self.pos.y + self.vehicle_shape[1].y,
            self.pos.x + self.vehicle_shape[0].x, self.pos.y + self.vehicle_shape[0].y,
            self.pos.x + self.vehicle_shape[2].x, self.pos.y + self.vehicle_shape[2].y,
            color=COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )

        self.info_wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
        self.info_wander_target = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
        self.info_force_vector = ArrowLine(Vector2D(0, 0), Vector2D(0, 0), colour=COLOUR_NAMES['BLUE'], batch=window.get_batch("info"))
        self.info_vel_vector = ArrowLine(Vector2D(0, 0), Vector2D(0, 0), colour=COLOUR_NAMES['AQUA'], batch=window.get_batch("info"))
        self.info_net_vectors = [
            ArrowLine(Vector2D(0, 0), Vector2D(0, 0), colour=COLOUR_NAMES['GREY'], batch=window.get_batch("info")),
            ArrowLine(Vector2D(0, 0), Vector2D(0, 0), colour=COLOUR_NAMES['GREY'], batch=window.get_batch("info")),
        ]

        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 10.0

        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        self.max_speed = 20.0 * scale
        self.max_force = 500.0

        self.show_info = False

    def randomise_path(self):
        cx = self.world.cx
        cy = self.world.cy
        margin = min(cx, cy) * 1 / 6
        self.path.create_random_path(5, margin, margin, cx - margin, cy - margin)

    def follow_path(self):
        WaypointNearDist = 3
        if self.path.is_finished():
            return self.arrive(self.path.end_point)
        else:
            if self.pos.distance(self.path.current_pt()) < WaypointNearDist:
                self.path.add_way_pt(self.path.current_pt())
            if not self.path.is_finished():
                return self.seek(self.path.current_pt())
            else:
                return self.arrive(self.path.end_point)

    def calculate(self, delta):
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
        else:
            force = Vector2D()

        cohesion_force = self.cohesion() * self.world.cohesion_weight
        separation_force = self.separation() * self.world.separation_weight
        alignment_force = self.alignment() * self.world.alignment_weight

        total_force = force + cohesion_force + separation_force + alignment_force
        self.force = total_force.truncate(self.max_force)
        return total_force

    def update(self, delta):
        force = self.calculate(delta)
        force.truncate(self.max_force)
        self.accel = force / self.mass
        self.vel += self.accel * delta
        self.vel.truncate(self.max_speed)
        self.pos += self.vel * delta
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        self.world.wrap_around(self.pos)
        self.vehicle.x = self.pos.x + self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y + self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()

        s = 0.5
        if self.force is None:
           self.force = Vector2D(0, 0)
   
        self.info_force_vector.position = self.pos
        self.info_force_vector.end_pos = self.pos + self.force * s
        self.info_vel_vector.position = self.pos
        self.info_vel_vector.end_pos = self.pos + self.vel * s
        self.info_net_vectors[0].position = self.pos + self.vel * s
        self.info_net_vectors[0].end_pos = self.pos + (self.force + self.vel) * s
        self.info_net_vectors[1].position = self.pos
        self.info_net_vectors[1].end_pos = self.pos + (self.force + self.vel) * s

    def speed(self):
        return self.vel.length()

    def seek(self, target_pos):
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        panic_range_sq = 500
        if self.pos.distanceSq(hunter_pos) > panic_range_sq:
            return Vector2D()
        desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
        return desired_vel - self.vel

    def arrive(self, target_pos, speed):
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            speed = dist / decel_rate
            speed = min(speed, self.max_speed)
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def pursuit(self, evader):
        return Vector2D()

    def wander(self, delta):
        wt = self.wander_target
        jitter_tts = self.wander_jitter * delta
        wt += Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)
        wt.normalise()
        wt *= self.wander_radius
        target = wt + Vector2D(self.wander_dist, 0)
        wld_target = self.world.transform_points(target, self.pos, self.heading, self.side, self.scale)
        return self.seek(wld_target)

    def cohesion(self):
        neighbors = self.world.get_neighbors(self, self.world.neighbor_radius)
        if not neighbors:
            return Vector2D()
        center_mass = Vector2D()
        for neighbor in neighbors:
            center_mass += neighbor.pos
        center_mass /= len(neighbors)
        return self.seek(center_mass)

    def separation(self):
        neighbors = self.world.get_neighbors(self, self.world.neighbor_radius)
        if not neighbors:
            return Vector2D()
        force = Vector2D()
        for neighbor in neighbors:
            to_agent = self.pos - neighbor.pos
            force += to_agent.normalise() / to_agent.length()
        return force

    def alignment(self):
        neighbors = self.world.get_neighbors(self, self.world.neighbor_radius)
        if not neighbors:
            return Vector2D()
        average_heading = Vector2D()
        for neighbor in neighbors:
            average_heading += neighbor.heading
        average_heading /= len(neighbors)
        return (average_heading - self.heading)

class World(object):
    def __init__(self, width, height):
        self.agents = []
        self.cx = width
        self.cy = height
        self.target = Vector2D(width / 2, height / 2)
        self.hunter = None
        self.cohesion_weight = 1.0
        self.separation_weight = 1.0
        self.alignment_weight = 1.0
        self.neighbor_radius = 50.0

    def add_agent(self, agent):
        self.agents.append(agent)

    def wrap_around(self, pos):
        if pos.x > self.cx:
            pos.x = 0
        elif pos.x < 0:
            pos.x = self.cx
        if pos.y > self.cy:
            pos.y = 0
        elif pos.y < 0:
            pos.y = self.cy

    def get_neighbors(self, agent, radius):
        neighbors = []
        for other_agent in self.agents:
            if other_agent != agent and agent.pos.distance(other_agent.pos) < radius:
                neighbors.append(other_agent)
        return neighbors

    def update(self, delta):
        for agent in self.agents:
            agent.update(delta)

    def draw(self):
        for agent in self.agents:
            agent.vehicle.draw()
            
	
def update(dt):
    window.clear()
    world.update(dt)
    world.draw()

'''
width, height = 800, 600
  world = World(width, height)
  for _ in range(10):
        agent = Agent(world, scale=30.0)
        world.add_agent(agent)
'''
