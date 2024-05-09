from random import choice

class Rando2(object):
    def update(self, gameinfo):
    
        src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)

        #Find a target planet with the minimum number of ships
        dest = min(gameinfo.not_my_planets.values(), key=lambda p: p.num_ships)
        
        gameinfo.planet_order(src, dest, src.num_ships)




                   
    
        
    
 

    
         
   




