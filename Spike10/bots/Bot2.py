from random import choice

class Bot2(object):
    def update(self, gameinfo):
        
        src = max(gameinfo._my_planets().values(), key=lambda p: p.ships)

        #Detect the strongest target planet
        dest = max(gameinfo._not_my_planets().values(), key=lambda p: p.ships)

        #Launch new fleet if there are enough ships
        gameinfo.planet_order(src, dest, int(src.ships * 0.75))