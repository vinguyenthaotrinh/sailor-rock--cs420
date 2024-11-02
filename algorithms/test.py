# test.py
from manager.board import Board
from copy import deepcopy
    
def replay_solution(start_board, end_board):
    replay_board = deepcopy(start_board)
    
    with open("manager/gui.txt", "w") as file:
        file.write(str(Board.rows) + " " + str(Board.cols) + "\n")
        file.write(replay_board.get_board_as_string() + "\n")  
                
        end_board.dir_list = []
        st = "ullluuululldduuruurdldldlldddrrrrrrrrrrrrllllllluuulullddduuurrdluldduuruuldrurddldllldddrrrrrrrrrrrdrururdlllurldlllllluuulllddduuuruuldddurrrdddllllluuurrdduuurrdlulddulldddrrrrrrrrrrrrurdlllllllllllllulldrrrrrrrrrrrrrrrlllllllluuullldduulldddrrrrrrrrrrrrllllllddlllluulluuurrdduulldddrrrrrrrrrrrdrulur"
        
        for i in range(len(st)):
            end_board.dir_list.append(st[i])
            
        for dir in end_board.dir_list:
            file.write(f"Move: {dir}\n")
            replay_board.move(dir)
            file.write(replay_board.get_board_as_string() + "\n")  
         
def search(board):
    replay_solution(board, board)
    return
