from random import choice

class Rando(object):
    def update(self, gameinfo):
        #pass

        # check if we should attack
        if gameinfo._my_planets() and gameinfo._not_my_planets():
            # select random target and destination
            dest = choice(list(gameinfo._not_my_planets().values()))
            src = choice(list(gameinfo._my_planets().values()))
            # launch new fleet if there's enough ships
            if src.ships > 10:
                gameinfo.planet_order(src, dest, int(src.ships * 0.75))
        
    
 

    
         
   




