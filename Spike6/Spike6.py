import pygame
import heapq
import random

pygame.init()

#The Screen Size
grid_width = 15
grid_height = 10
cell_size = 50
screen_width = grid_width * cell_size
screen_height = grid_height * cell_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Navigation with Graphs")
bg_colour = pygame.Color(130, 140, 133)#grey

clock = pygame.time.Clock()
clock.tick()

#Class for representing each tile
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((cell_size, cell_size))
        self.rect = self.image.get_rect(topleft=(pos[0] * cell_size, pos[1] * cell_size))
        pygame.draw.rect(self.image, pygame.Color('white'), self.image.get_rect(), 1)#White boarder to each cell

#Making the tiles grid
tiles_group = pygame.sprite.Group()
for x in range(grid_width):
    for y in range(grid_height):
        tile = Tile((x, y))
        tiles_group.add(tile)

#Defining the navigation graph in a dictionary
navigation_graph = {}

for tile in tiles_group:
    x, y = tile.rect.topleft
    neigh = []
    #Adding neighbours (up, down, left, right)
    if y > 0:
        neigh.append((x // cell_size, (y - cell_size) // cell_size))
    if y < screen_height - cell_size:
        neigh.append((x // cell_size, (y + cell_size) // cell_size))
    if x > 0:
        neigh.append(((x - cell_size) // cell_size, y // cell_size))
    if x < screen_width - cell_size:
        neigh.append(((x + cell_size) // cell_size, y // cell_size))
    navigation_graph[(x // cell_size, y // cell_size)] = neigh

#Heuristic function for the A*
def heuristic(current, goal):
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

#Function for A*
def astar(graph, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {pos: float('inf') for pos in graph}
    g_score[start] = 0

    while open_set:
        current_cost, current_node = heapq.heappop(open_set)
        if current_node == goal:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            return path[::-1]
        for nei in graph[current_node]:
            tentative_g_score = g_score[current_node] + 1#Each of the edges has a weight of 1
            if tentative_g_score < g_score[nei]:
                came_from[nei] = current_node
                g_score[nei] = tentative_g_score
                f_score = tentative_g_score + heuristic(nei, goal)
                heapq.heappush(open_set, (f_score, nei))

#Function for checking if a position is blocked by another agent
def is_blocked(pos, agents):
    for agent in agents:
        if agent.position == pos:
            return True
    return False

#Class for the Agents
class Agents(pygame.sprite.Sprite):
    def __init__(self, start_pos, colour, speed):
        super().__init__()
        self.image = pygame.Surface((cell_size, cell_size))
        self.image.fill(pygame.Color(colour))#Converting the color string to pygame color
        self.rect = self.image.get_rect(topleft=(start_pos[0] * cell_size, start_pos[1] * cell_size))
        self.position = start_pos
        self.path = []#Storing the paths in a list
        self.speed = speed

    def plan_path(self, goal):
            self.path = astar(navigation_graph, self.position, goal)

    def follow_path(self, agents):
        if not self.path:
            return None #If the path is empty, plan a new path
        #Moving the agent according to its speed
        for _ in range(self.speed):
             if self.path:
                 next_pos = self.path.pop(0)#Get the next position from the path
                 if not is_blocked(next_pos, agents):
                    self.rect.topleft = (next_pos[0] * cell_size, next_pos[1] * cell_size)
                    self.position = next_pos
                 else:
                    break  #Stop moving if the next position is blocked
             
        #Introduce randomness to choose whether to follow the path or move randomly
        if random.random() < 0.7:
            if not is_blocked(next_pos, agents):
                self.rect.topleft = (next_pos[0] * cell_size, next_pos[1] * cell_size)
                self.position = next_pos
                return
        else:
            #If not following the path, choose a random direction
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for direction in directions:
                new_pos = (self.position[0] + direction[0], self.position[1] + direction[1])
                if not is_blocked(new_pos, agents):
                    self.rect.topleft = (new_pos[0] * cell_size, new_pos[1] * cell_size)
                    self.position = new_pos
                    break
              
    #Function for making little circles on the agents destination
    def draw_destination(self, screen, goal):
        x, y = goal
        destination_rect = pygame.Rect(x * cell_size + cell_size // 4, y * cell_size + cell_size // 4, cell_size // 2, cell_size // 2)
        pygame.draw.circle(screen, pygame.Color(self.image.get_at((0, 0))), destination_rect.center, cell_size // 4)
           
#Making the Agents
agent1 = Agents((1, 2), 'blue', speed=1)
agent2 = Agents((1, 4), 'green', speed=2)
agent3 = Agents((1, 6), 'white', speed=1)
agent4 = Agents((1, 8), 'orange', speed=4)

#Setting the path goals for the agents
goal1 = (10, 1)
goal2 = (8, 8)
goal3 = (13, 6)
goal4 = (13, 9)

#Planning the paths for the agents
agent1.plan_path(goal1)
agent2.plan_path(goal2)
agent3.plan_path(goal3)
agent4.plan_path(goal4)

agents = [agent1, agent2, agent3, agent4]

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #Moving agents along their paths
    for agent in agents:
        agent.follow_path(agents)

    #Setting the background screen colour
    screen.fill(bg_colour)
    '''
    #Moving agents along their paths
    agent1.follow_path()
    agent2.follow_path()
    agent3.follow_path()
    agent4.follow_path()
    '''
    #Putting the tiles on the screen
    tiles_group.draw(screen)

    #Having the agents onto the screen
    screen.blit(agent1.image, agent1.rect)
    screen.blit(agent2.image, agent2.rect)
    screen.blit(agent3.image, agent3.rect)
    screen.blit(agent4.image, agent4.rect)

    # Having the little circle goals onto the screen
    for agent, goal in zip(agents, [goal1, goal2, goal3, goal4]):
         agent.draw_destination(screen, goal)
   
    '''
    #Having the little circle goals onto the screen
    agent1.draw_destination(screen, goal1)
    agent2.draw_destination(screen, goal2)
    agent3.draw_destination(screen, goal3)
    agent4.draw_destination(screen, goal4)
    '''
    pygame.display.flip()

    #Cap the frame rate
    clock.tick(60)

pygame.quit()
