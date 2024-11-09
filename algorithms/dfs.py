# dfs.py
from manager.board import Board
import tracemalloc
from time import time
from copy import deepcopy

def print_results(board, gen, dur, mem_usage):
    with open(Board.output_file, "a") as file:
        file.write("\n\nAlgorithm: DFS\n")
        file.write("Steps: {}\n".format(len(board.dir_list)))
        file.write("Total cost: {}\n".format(board.cost))
        file.write("Node: {}\n".format(gen))
        file.write("Time: {:.2f} ms\n".format(dur * 1000))
        file.write("Memory: {:.2f} MB\n".format(mem_usage / 1024 / 1024))
        file.write("Solution: {}".format(''.join(board.dir_list)))
    
def replay_solution(start_board, dir_list):
    replay_board = deepcopy(start_board)
    
    with open("manager/gui.txt", "w") as file:
        file.write("Path: " + (''.join(dir_list)).lower() + "\n")
                
        cnt = 0
        for dir in dir_list:
            cnt += 1
            file.write(f"Step {cnt}: {dir}\n")
            replay_board.move(dir)
            file.write(replay_board.get_board_as_string() + "\n")   

def search(board, is_selected, is_printed):
    start = time()
    tracemalloc.start()  # Bắt đầu theo dõi bộ nhớ
    nodes_generated = 0
    
    if board.is_win():
        end = time()
        mem_usage = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        if is_selected:
            replay_solution(board, board.dir_list)
        if is_printed:
            print_results(board, 1, end - start, mem_usage)
        return board
    
    node = deepcopy(board)
    nodes_generated += 1
    frontier = []
    frontier.append(node)
    reached = set()
    reached.add((tuple(node.stones), node.player))
    
    while len(frontier) > 0:
        cur_node = frontier.pop()
        moves = cur_node.moves_available()
        
        for m in moves:
            child = cur_node.clone_with_move(m)
            nodes_generated += 1
            if child.is_win():
                end = time()
                mem_usage = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                if is_selected:
                    replay_solution(board, child.dir_list)
                if is_printed:
                    print_results(child, nodes_generated, end - start, mem_usage)
                return child
            if not child.is_deadlock() and (tuple(child.stones), child.player) not in reached:
                frontier.append(child)
                reached.add((tuple(child.stones), child.player))
    
    tracemalloc.stop()
    print("Solution not found")
    return
