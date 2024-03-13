import random

game_board = ["-","-","-",
              "-","-","-",
              "-","-","-",]

curr_player = "X"
win = None
game_run = True
board_printed = False

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
                break  # Break the loop only when a valid move is entered
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
        position = random.randint(0, 8)
        #If stament if a spot is already occupied
        if game_board[position] == "-":
            game_board[position] = "O"
            switch_player()

#Function for AI 2 to make moves
def ai_move2(game_board):
    while curr_player == "O":
        #Horizontal 1
        if game_board[0] == 'X' and game_board[1] == 'X':
            if game_board[2] == "-":
                game_board[2] = 'O'
                switch_player()
                return None  # Return None to exit the function
        #Horizontal 2
        if game_board[3] == 'X' and game_board[4] == 'X':
            if game_board[5] == "-":
                game_board[5] = 'O'
                switch_player()
                return None
        #Horizontal 3
        if game_board[6] == 'X' and game_board[7] == 'X':
            if game_board[8] == "-":
                game_board[8] = 'O'
                switch_player()
                return None
        #Vertical 1
        if game_board[0] == 'X' and game_board[3] == 'X':
            if game_board[6] == "-":
                game_board[6] = 'O'
                switch_player()
                return None
        #Vertical 2
        if game_board[1] == 'X' and game_board[4] == 'X':
            if game_board[7] == "-":
                game_board[7] = 'O'
                switch_player()
                return None
        #Vertical 3
        if game_board[2] == 'X' and game_board[5] == 'X':
            if game_board[8] == "-":
                game_board[8] = 'O'
                switch_player()
                return None
        #Diagonal 1
        if game_board[0] == 'X' and game_board[4] == 'X':
            if game_board[8] == "-":
                game_board[8] = 'O'
                switch_player()
                return None
        #Diagonal 2
        if game_board[2] == 'X' and game_board[4] == 'X':
            if game_board[6] == "-":
                game_board[6] = 'O'
                switch_player()
                return None

        # If the above condition is not met, make a random move
        position = random.randint(0, 8)
        if game_board[position] == "-":
            game_board[position] = "O"
            switch_player()
            return None  # Return None to exit the function

if __name__ == '__main__':
    print("Tic Tac Toe Game")
    print()
    _help = '''
    By making a move enter a number between 0 - 9 and press enter,
    to the number that corresponds to the board position:

	1 | 2 | 3
	---------
	4 | 5 | 6
	---------
	7 | 8 | 9
	'''
    print(_help)
    print()
    pp_input = int(input("Enter 1 or 2 to Pick an AI Bot\nAI Bot 1 (Easy)\nAI Bot 2 (Hard)"))
    #While loop for game to run
    while game_run:
        print_game_board(game_board)
        _input(game_board)
        check_for_win()
        check_for_tie(game_board)
        switch_player()

        # AI Bots
        if pp_input == 1:
            ai_move(game_board)
        elif pp_input == 2:
            ai_move2(game_board)
        check_for_win()
        check_for_tie(game_board)
