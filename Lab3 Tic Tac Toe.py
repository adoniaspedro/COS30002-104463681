import random

game_board = ["-","-","-",
              "-","-","-",
              "-","-","-",]

curr_player = "X"
win = None
game_run = True
board_printed = False

# Function for printing out the Game Board
def print_game_board(game_board):
    print(game_board[0] + " | " + game_board[1] + " | " + game_board[2])
    print("---------")
    print(game_board[3] + " | " + game_board[4] + " | " + game_board[5])
    print("---------")
    print(game_board[6] + " | " + game_board[7] + " | " + game_board[8])
#print_game_board(game_board)    

#Player Input
def _input(game_board):
    p_input = int(input("Enter a Number between 1-9: "))
    #If statement for if the player or the bot chooses a number
    #between 1 and 9 and with a available positon ("-") 
    if p_input >= 1 and p_input <= 9 and game_board[p_input-1] == "-":
        game_board[p_input-1] = curr_player
    else:
        print("That Position is already taken")

#Funtion for Checking for Win or Tie (Horizontal)
def horizontal(game_board):
    global win
    if game_board[0] == game_board[1] == game_board[2] and game_board[1] != "-":
        win = game_board[0]
        return True
    elif game_board[3] == game_board[4] == game_board[5] and game_board[3] != "-":
        win = game_board[3]
        return True
    elif game_board[6] == game_board[7] == game_board[8] and game_board[6] != "-":
        win = game_board[3]
        return True

#Funtion for Checking for Win or Tie (Vertical)
def vertical(game_board):
    global win
    if game_board[0] == game_board[3] == game_board[6] and game_board[0] != "-":
        win = game_board[0]
        return True
    elif game_board[1] == game_board[4] == game_board[7] and game_board[1] != "-":
        win = game_board[1]
        return True
    elif game_board[2] == game_board[5] == game_board[8] and game_board[2] != "-":
        win = game_board[2]
        return True

#Funtion for Checking for Win or Tie (Diagonal)
def diagonal(game_board):
    global win
    if game_board[0] == game_board[4] == game_board[8] and game_board[0] != "-":
        win = game_board[0]
        return True
    elif game_board[2] == game_board[4] == game_board[6] and game_board[2] != "-":
        win = game_board[2]
        return True

#Function for checking if theres a tie in the game board
def check_for_tie(game_board):
    global game_run
    if "-" not in game_board:
        print_game_board(game_board)
        print("It's a Tie!")
        print()
        print("Game Over")
        game_run = False

#Function for checking who won the game
def check_for_win():
    global game_run
    if diagonal(game_board) or horizontal(game_board) or vertical(game_board):
        print_game_board(game_board) 
        print("The Winner is " + win)
        print()
        print("Game Over")
        game_run = False

#Function for Switching Players
def switch_player():
    global curr_player
    if curr_player == "X":
        curr_player = "O"
    else:
        curr_player = 'X'

#Function for AI bot to make moves
def ai_move(game_board):
    while curr_player == "O":
        position = random.randint(0, 8)
        #If stament if a spot is already occupied
        if game_board[position] == "-":
            game_board[position] = "O"
            switch_player()


if __name__ == '__main__':
    print("Tic Tac Toe Game")
    print()
    _help = '''
    By making a move enter a number between 0 - 9 and press enter,
    to the number that corresponds to the board position:

	1 | 2 | 3
	---------
	3 | 4 | 6
	---------
	7 | 8 | 9
	'''
    print(_help)
    print()
    while game_run:
        print_game_board(game_board)
        _input(game_board)
        #check_for_win()
        check_for_tie(game_board)
        switch_player()
        #AI Bot
        ai_move(game_board)
        check_for_win()
        check_for_tie(game_board)
        

