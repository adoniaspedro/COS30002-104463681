from random import choice

class Rando2(object):
    def update(self, gameinfo):
    
        src = max(gameinfo._my_planets().values(), key=lambda p: p.ships)

        #Find a target planet with the minimum number of ships.
        dest = min(gameinfo._not_my_planets().values(), key=lambda p: p.ships)
        #Launch new fleet if there's enough ships
        if src.ships > 10:
                gameinfo.planet_order(src, dest, int(src.ships * 0.75))
        
        #gameinfo.planet_order(src, dest, src.num_ships)




                   
    
        
    
 

    
         
   




