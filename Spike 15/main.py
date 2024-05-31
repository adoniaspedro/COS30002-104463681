import pyglet
#importing graphics for side-effects - it creates the egi and window module objects. 
#This is the closest python has to a global variable and it's completely gross
import graphics
#game has to take another approach to exporting a global variable
#the game object is importable, but only contains the game object if it's being imported after the game object has been created below
import game 
from agent import Agent, Weapon

my_world = game.Game(800, 600)  # for a game world of size 800x600

# Create a weapon
rifle = Weapon('rifle')

# Create an agent with the rifle
#agent = Agent(world=my_world, scale=30, mass=1, mode='seek', weapon=rifle)

if __name__ == '__main__':  
  #window = MyWindow()
  #window.push_handlers(window.world.keys)  
  #window = pyglet.window.Window(800, 600)
  game.game = game.Game(800, 600)
  #window.on_draw = game.game.draw
  pyglet.clock.schedule_interval(game.game.update, 1/60.)
  pyglet.app.run()
  