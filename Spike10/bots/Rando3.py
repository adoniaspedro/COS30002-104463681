from random import choice

class Rando3(object):
    def update(self, gameinfo):
        #Only send one fleet at a time (assuming the logic goes here)
        if gameinfo.my_fleets:
            return
    
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)
            
            # Find the strongest planet to attack
            strongest_planet = max(gameinfo.not_my_planets.values(), key=lambda p: p.num_ships)

            # Send all ships from the source planet to the strongest planet
            gameinfo.planet_order(src, strongest_planet, src.num_ships)
            

   




