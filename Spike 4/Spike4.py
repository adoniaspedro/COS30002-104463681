import random
import copy

game_board = ["X","-","O",
              "-","-","-",
              "-","-","-",]

curr_player = "X"
win = None
game_run = True
board_printed = False
moves = []

#Function for printing out the Game Board
def print_game_board(game_board):
    print(game_board[0] + " | " + game_board[1] + " | " + game_board[2])
    print("---------")
    print(game_board[3] + " | " + game_board[4] + " | " + game_board[5])
    print("---------")
    print(game_board[6] + " | " + game_board[7] + " | " + game_board[8])   

#Function for Player Input
def _input(game_board):
    while True:
        try:
            p_input = int(input("Enter a Number between 1-9: "))
            if p_input < 1 or p_input > 9:
                print("That Position does not exist")
            elif game_board[p_input-1] != "-":
                print("That Position is already taken")
            else:
                game_board[p_input-1] = curr_player
                moves.append(copy.deepcopy(game_board))#Save the current state of the board
                break#Break the loop only when a valid move is entered
        except ValueError:
            print("Please enter a valid number between 1 and 9.")

#Function for Checking for Win or Tie (Horizontal)
def horizontal(game_board):
    global win
    if game_board[0] == game_board[1] == game_board[2] and game_board[1] != "-":
        win = game_board[0]
        return True
    elif game_board[3] == game_board[4] == game_board[5] and game_board[3] != "-":
        win = game_board[3]
        return True
    elif game_board[6] == game_board[7] == game_board[8] and game_board[6] != "-":
        win = game_board[6]
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
    if game_run and "-" not in game_board:
        print_game_board(game_board)
        print("It's a Tie!")
        print()
        print("Game Over")
        game_run = False

#Function for checking who won the game
def check_for_win():
    global game_run
    if game_run and (diagonal(game_board) or horizontal(game_board) or vertical(game_board)):
        print_game_board(game_board) 
        print("The Winner is " + win)
        print()
        print("Game Over")
        game_run = False
        return game_board#If result in a win then return the game board

#Function for Switching Players
def switch_player():
    global curr_player
    if curr_player == "X":
        curr_player = "O"
    else:
        curr_player = 'X'

#Function for AI to make moves
def ai_move(game_board):
    while curr_player == "O":
        #List of main positions to improve the efficiency of a basic random search
        main_positions = [0, 2, 6, 8]
        #Seeing what positions are empty to improve the effectiveness
        #of a basic random search
        empty_positions = [i for i in main_positions if game_board[i] == "-"]
        #If there are empty positions available
        if empty_positions:
            position = random.choice(empty_positions)
        else:
            position = random.choice([i for i in range(9) if game_board[i] == "-"])#Choose any position thats empty
        copy_board = copy.deepcopy(game_board)#Make a copy of the game board
        #If stament if a spot is already occupied
        if copy_board[position] == "-":
            copy_board[position] = "O"
            game_board[:] = copy_board[:]#Update/Search the original game board
            moves.append(copy.deepcopy(game_board))
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
    #While loop for game to run
    while game_run:
        print_game_board(game_board)
        _input(game_board)
        check_for_win()
        check_for_tie(game_board)
        switch_player()
        #AI Bot
        ai_move(game_board)
        check_for_win()
        check_for_tie(game_board)
