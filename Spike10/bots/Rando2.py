from random import choice

class Rando2(object):
    def update(self, gameinfo):
        #Only send one fleet at a time (assuming the logic goes here)
        if gameinfo.my_fleets:
            return
    
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)

            #Find a target planet with the minimum number of ships
            dest = min(gameinfo.not_my_planets.values(), key=lambda p: p.num_ships)
        
            #OR (alternatively), use an inverse proportional maximum search. . .
            dest = max(gameinfo.not_my_planets.values(),
                       key=lambda p: 1.0 / (1 + p.num_ships))
                   
    
        
    
 

    
         
   




