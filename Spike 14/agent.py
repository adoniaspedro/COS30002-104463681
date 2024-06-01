import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
import numpy as np
from math import sin, cos, radians, sin
from random import random, randrange, uniform
from path import Path
from pyglet.shapes import Circle

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

        self.cohesion_weight = 1.0
        self.separation_weight = 1.5
        self.alignment_weight = 1.0
        self.wander_weight = 0.5

        self.neighbour_distance = 50.0

        self.max_speed = 20.0 * scale

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
                self.path.next_waypoint()
            if not self.path.is_finished():
                return self.seek(self.path.current_pt())
            else:
                return self.arrive(self.path.end_point)
            

    def calculate(self, delta):
        force = Vector2D()
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

        force += self.cohesion() * self.cohesion_weight
        force += self.separation() * self.separation_weight
        force += self.alignment() * self.alignment_weight

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
        self.vehicle.x = self.pos.x + self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y + self.vehicle_shape[0].y
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
        # Calculate the average heading and center position of the neighbours
        #average_heading, center_position = self.calculate_neighbour_data(agents, radius)

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

    def cohesion(self):
        neighbors = self.world.get_neighbours(self, self.neighbour_distance)
        center_mass = Vector2D()
        steering_force = Vector2D()
        neighbor_count = 0

        for neighbor in neighbors:
            if neighbor != self and (neighbor.pos - self.pos).length() < self.neighbour_distance:
                center_mass += neighbor.pos
                neighbor_count += 1

        if neighbor_count > 0:
            center_mass /= neighbor_count
            steering_force = self.seek(center_mass)
        return steering_force

    def separation(self):
        neighbors = self.world.get_neighbours(self, self.neighbour_distance)
        steering_force = Vector2D()

        for neighbor in neighbors:
            if neighbor != self and (neighbor.pos - self.pos).length() < self.neighbour_distance:
                away = self.pos - neighbor.pos
                steering_force += away.normalise() / away.length()
        return steering_force

    def alignment(self):
        neighbors = self.world.get_neighbours(self, self.neighbour_distance)
        average_heading = Vector2D()
        neighbor_count = 0

        for neighbor in neighbors:
            if neighbor != self and (neighbor.pos - self.pos).length() < self.neighbour_distance:
                average_heading += neighbor.heading
                neighbor_count += 1

        if neighbor_count > 0:
            average_heading /= neighbor_count
            average_heading -= self.heading
        return average_heading
    
    def set_neighbour_distance(self, distance):
        self.neighbour_distance = distance
        self.update_neighbourhood()
        
    def get_neighbour_distance(self):
        return self.neighbour_distance
        
    def update_neighbourhood(self):
        self.neighbours = []
        for agent in self.world.agents:
            if agent != self and (agent.pos - self.pos).length() < self.neighbour_distance:
                self.neighbours.append(agent)
                
    def set_steering_parameters(self, **kwargs):
        if 'cohesion_weight' in kwargs:
            self.cohesion_weight = kwargs['cohesion_weight']
        if 'separation_weight' in kwargs:
            self.separation_weight = kwargs['separation_weight']
        if 'alignment_weight' in kwargs:
            self.alignment_weight = kwargs['alignment_weight']
        if 'wander_weight' in kwargs:
            self.wander_weight = kwargs['wander_weight']
        
    def get_steering_parameters(self):
        return {
            'cohesion_weight': self.cohesion_weight,
            'separation_weight': self.separation_weight,
            'alignment_weight': self.alignment_weight,
            'wander_weight': self.wander_weight,
            'neighbour_distance': self.neighbour_distance
        }
        
    def display_current_parameters(self):
        print(f"Cohesion weight: {self.cohesion_weight}")
        print(f"Separation weight: {self.separation_weight}")
        print(f"Alignment weight: {self.alignment_weight}")
        print(f"Wander weight: {self.wander_weight}")
        print(f"Neighbour distance: {self.neighbour_distance}")
        
    def calculate_color_based_on_cohesion(self, cohesion_weight):
        # Map the cohesion weight to a color gradient from red (low cohesion) to green (high cohesion)
        return (255 * (1 - cohesion_weight), 255 * cohesion_weight, 0)

    def calculate_size_based_on_distance(self, neighbour_distance):
        # Map the neighbour distance to a size, with a minimum size of 10 and a maximum size of 50
        return max(10, min(neighbour_distance / 2, 50))

    def draw_agent_with_color_and_size(self, pos, color, size):
        #circle = Circle(pos[0], pos[1], size, color=color)
        #size = int(round(size))
        #print(type(pos.x), type(pos.y), type(size))
        circle = Circle(pos.x, pos.y, size, color=color)

        # Draw the circle
        circle.draw()
        pass    
    
    def draw(self, agents, radius):
        #Calculate color based on cohesion parameters
        cohesion_color = self.calculate_color_based_on_cohesion(self.get_steering_parameters()["cohesion_weight"])
            
        #Calculate size based on neighbour distance
        neighbour_size = self.calculate_size_based_on_distance(self.get_neighbour_distance())
            
        #Draw the agent with the calculated color and size
        self.draw_agent_with_color_and_size(self.pos, cohesion_color, neighbour_size)
        
        # Draw the neighbours
        for neighbour in self.get_neighbours(agents, radius):
            # Draw a line from this agent to the neighbour
            pyglet.shapes.Line(self.pos.x, self.pos.y, neighbour.pos.x, neighbour.pos.y, color=(255, 0, 0)).draw()

        # Calculate the average heading and center position
        average_heading, center_position = self.calculate_neighbour_data(agents, radius)

        # Draw the average heading and center position
        if average_heading is not None and center_position is not None:
            # Draw a line in the direction of the average heading
            end_pos = self.pos + Vector2D(cos(average_heading), sin(average_heading)) * 50
            pyglet.shapes.Line(self.pos.x, self.pos.y, end_pos.x, end_pos.y, color=(0, 255, 0)).draw()

            # Draw a circle at the center position
            pyglet.shapes.Circle(center_position.x, center_position.y, 10, color=(0, 0, 255)).draw()
        # Draw a circle around the agent with the given radius
        circle = pyglet.shapes.Circle(self.pos.x, self.pos.y, radius, color=(255, 255, 255))
        circle.opacity = 500  # Make the circle semi-transparent
        circle.draw()   
        # Draw the agent with the calculated color and size
        self.draw_agent_with_color_and_size(self.pos, cohesion_color, neighbour_size)
        #print(self.pos.x, self.pos.y)
        

    def calculate_cohesion(self):
        # Calculate the average position of the neighbors
        average_position = sum((neighbor.pos for neighbor in self.neighbors), Vector2D()) / len(self.neighbors)
        
        # Calculate the steering force towards the average position
        return self.steer_towards(average_position)

    def calculate_separation(self):
        # Calculate the repulsion force away from the neighbors
        repulsion_force = sum((self.pos - neighbor.pos for neighbor in self.neighbors), Vector2D())
        
        # Calculate the steering force in the opposite direction
        return self.steer_away(repulsion_force)

    def calculate_alignment(self):
        # Calculate the average direction of the neighbors
        average_direction = sum((neighbor.velocity for neighbor in self.neighbors), Vector2D()) / len(self.neighbors)
    
        # Calculate the steering force to match the average direction
        return self.steer_towards(average_direction)
    
    def calculate_steering_force(self):
        # Calculate the steering forces for each behavior
        cohesion_force = self.calculate_cohesion()
        separation_force = self.calculate_separation()
        alignment_force = self.calculate_alignment()

        # Get the weights for each behavior
        weights = self.get_steering_parameters()

        # Calculate the weighted sum of the steering forces
        steering_force = (weights['cohesion_weight'] * cohesion_force +
                        weights['separation_weight'] * separation_force +
                        weights['alignment_weight'] * alignment_force)
        return steering_force
    
    def draw_steering_forces(self):
        # Calculate the steering forces
        steering_force = self.calculate_steering_force()
        
        # Draw an arrow representing the steering force
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                            ('v2f', (self.pos[0], self.pos[1], 
                                    self.pos[0] + steering_force.x, self.pos[1] + steering_force.y)),
                            ('c3B', (255, 0, 0,  # Color of the line
                                    255, 0, 0)))
    '''
    def on_draw(self):
        # Clear the window
        self.clear()
        
        # Draw all agents
        for agent in self.agents:
            agent.draw()
            agent.draw_steering_forces()
            self.display_label.draw()
    '''
    #Method to update the agents based on the steering forces
    def get_neighbours(self, agents, radius):
        neighbours = []
        for agent in agents:
            if agent is not self and np.linalg.norm(agent.pos - self.pos) <= radius:
                neighbours.append(agent)
        return neighbours
    
    #Method to calculate the average heading and center position of the neighbours
    def calculate_neighbour_data(self, agents, radius):
        neighbours = self.get_neighbours(agents, radius)

        if not neighbours:
            return None, None

        average_heading = sum(agent.direction for agent in neighbours) / len(neighbours)
        center_position = sum(agent.pos for agent in neighbours) / len(neighbours)
        
        return average_heading, center_position
    
    #Method to update the agent's position and direction based on the neighbours
    def update_(self, agents, radius):
        # Calculate the average heading and center position of the neighbours
        average_heading, center_position = self.calculate_neighbour_data(agents, radius)

        # If there are no neighbours, don't do anything
        if average_heading is None and center_position is None:
            return

        # Adjust the agent's direction and position gradually
        self.direction += (average_heading - self.direction) * 0.01
        self.pos += (center_position - self.pos) * 0.01
    