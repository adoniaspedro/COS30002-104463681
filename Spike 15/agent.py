import pyglet
from vector2d import Vector2D
from vector2d import Point2D
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

class Projectile:
    def __init__(self, speed, accuracy, position, direction):
        self.speed = speed
        self.accuracy = accuracy
        self.position = position
        self.direction = direction
        self.shape = pyglet.shapes.Circle(position.x, position.y, 5, color=(255, 0, 0))
        
    def update(self, delta):
        self.position += self.direction * self.speed * delta
        self.shape.x = self.position.x
        self.shape.y = self.position.y

    def draw(self):
        self.shape.draw()

class Weapon:
    def __init__(self, type):
        self.type = type

    def fire(self, position, direction):
        if self.type == 'rifle':
            return Projectile(speed=100, accuracy=0.9, position=position, direction=direction)
        elif self.type == 'rocket':
            return Projectile(speed=50, accuracy=0.9, position=position, direction=direction)
        elif self.type == 'handgun':
            return Projectile(speed=100, accuracy=0.5, position=position, direction=direction)
        elif self.type == 'grenade':
            return Projectile(speed=50, accuracy=0.5, position=position, direction=direction)

class Agent(object):
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        'normal': 0.5,
        'fast': 1.0,
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek', weapon=None):
        self.world = world
        self.mode = mode
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)
        self.force = Vector2D()
        self.accel = Vector2D()
        self.mass = mass
        self.weapon = Weapon(weapon) if weapon else Weapon('rifle')
        self.projectiles = []

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
            color=COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )

        self.info_wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
        self.info_wander_target = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
        self.info_force_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['BLUE'], batch=window.get_batch("info"))
        self.info_vel_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['AQUA'], batch=window.get_batch("info"))
        self.info_net_vectors = [
            ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['GREY'], batch=window.get_batch("info")),
            ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['GREY'], batch=window.get_batch("info")),
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

        self.max_speed = 20.0 * scale
        self.show_info = False
  
    def attack(self, target_pos):
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed * 2
        return (desired_vel - self.vel)  

    def fire_weapon(self, direction):
        projectile = self.weapon.fire(self.pos, direction)
        self.projectiles.append(projectile)
        return projectile
    
    def randomise_path(self):
        cx = self.world.cx
        cy = self.world.cy
        margin = min(cx, cy) * 1/6
        self.path.create_random_path(5, margin, margin, cx-margin, cy-margin)

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
        elif mode == 'attack':
            force = self.attack(target_pos)
        else:
            force = Vector2D()
        self.force = force
        return force

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
        self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()

        s = 0.5
        self.info_force_vector.position = self.pos
        self.info_force_vector.end_pos = self.pos + self.force * s
        self.info_vel_vector.position = self.pos
        self.info_vel_vector.end_pos = self.pos + self.vel * s
        self.info_net_vectors[0].position = self.pos + self.vel * s
        self.info_net_vectors[0].end_pos = self.pos + (self.force + self.vel) * s
        self.info_net_vectors[1].position = self.pos
        self.info_net_vectors[1].end_pos = self.pos + (self.force + self.vel) * s

        for projectile in self.projectiles:
            projectile.update(delta)

    def draw(self):
        self.vehicle.draw()
        for projectile in self.projectiles:
            projectile.draw()

        if self.mode == 'wander':
            wander_target_world = Vector2D(self.wander_target.x, self.wander_target.y)
            self.info_wander_circle.x = self.pos.x + self.heading.x * self.wander_dist
            self.info_wander_circle.y = self.pos.y + self.heading.y * self.wander_dist
            self.info_wander_circle.radius = self.wander_radius
            self.info_wander_target.x = wander_target_world.x
            self.info_wander_target.y = wander_target_world.y
            if self.show_info:
                self.info_wander_circle.draw()
                self.info_wander_target.draw()

        if self.show_info:
            self.info_force_vector.draw()
            self.info_vel_vector.draw()
            for net in self.info_net_vectors:
                net.draw()

    def seek(self, target_pos):
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        panic_distance = 100.0
        to_hunter = self.pos - hunter_pos
        if to_hunter.lengthSq() > panic_distance ** 2:
            return Vector2D(0, 0)
        desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def arrive(self, target_pos, speed):
        deceleration = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            deceleration_tweaker = 10.0
            speed = dist / (deceleration * deceleration_tweaker)
            speed = min(speed, self.max_speed)
            desired_vel = to_target * speed / dist
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def pursuit(self, evader):
        to_evader = evader.pos - self.pos
        relative_heading = self.heading.dot(evader.heading)
        if (to_evader.dot(self.heading) > 0) and (relative_heading < -0.95):
            return self.seek(evader.pos)
        look_ahead_time = to_evader.length() / (self.max_speed + evader.vel.length())
        return self.seek(evader.pos + evader.vel * look_ahead_time)

    def wander(self, delta):
        jitter_tts = self.wander_jitter * delta
        self.wander_target += Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)
        self.wander_target = self.wander_target.normalise()
        self.wander_target *= self.wander_radius
        target_local = self.wander_target + Vector2D(self.wander_dist, 0)
        target_world = PointToWorldSpace(target_local, self.heading, self.side, self.pos)
        return target_world - self.pos
