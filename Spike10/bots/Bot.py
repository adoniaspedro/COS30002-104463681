from random import choice

class Bot(object):
    def update(self, gameinfo):
    
    
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)
            
            #Find the nearest planet to attack
            nearest_planet = min(gameinfo.not_my_planets.values(), key=lambda p: gameinfo.distance(src, p))

            #Sending all ships from the source planet to the nearest planet
            gameinfo.planet_order(src, nearest_planet, src.num_ships)
            
           
            

   




