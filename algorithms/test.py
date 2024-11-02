# test.py
from manager.board import Board
from copy import deepcopy
    
def replay_solution(start_board, end_board, steps):
    replay_board = deepcopy(start_board)
    
    with open("manager/gui.txt", "w") as file:
        file.write(str(Board.rows) + " " + str(Board.cols) + "\n")
        file.write(replay_board.get_board_as_string() + "\n")  
                
        end_board.dir_list = []
        
        for ch in steps:
            end_board.dir_list.append(ch)
            
        for dir in end_board.dir_list:
            file.write(f"Move: {dir}\n")
            replay_board.move(dir)
            file.write(replay_board.get_board_as_string() + "\n")  
         
def search(board, steps):
    replay_solution(board, board, steps)
    return
