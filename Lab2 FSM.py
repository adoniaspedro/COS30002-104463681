#variables
fuel = 0
tires = 0

#State
states = ['on', 'pit stop', 'racing']
curr_state = 'racing'

#Causing a state change
driving = True
working = True
max = 150
time = 0

#Main While loop
while working and driving:
    time = time + 1
    
    #On State
    if curr_state =='on':
        print("The Engine is On")
        fuel -= 1
        if fuel < 2 or tires < 4:
            curr_state == 'pit stop'
    
    #Pit Stop State
    elif curr_state == 'pit stop':
        print("Fixing the Car")
        fuel += 1
        tires += 1
        if fuel > 2 and tires >= 4:
            curr_state == 'racing'
                 
    #Racing State
    elif curr_state == 'racing':
        print("Vrrrooooooooommmmmmmmmmmmmmmm")
        fuel -= 1
        tires -= 1
        if fuel >= 1:
            curr_state = 'on'
            
    else:
        print("You're not racing it was a dream! :(")
        
    if fuel <= 0:
        driving = False
        
    if time > max:
        working = False

print("It's Done")
