#ucs.py
from manager.board import Board
import tracemalloc
import heapq
from time import time
from copy import deepcopy

def print_results(board, gen, dur, mem_usage):
    with open(Board.output_file, "a") as file:
        file.write("\n\nAlgorithm: UCS\n")
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

def search(board, is_selected):
    start = time()
    tracemalloc.start()
    nodes_generated = 0
    
    if board.is_win():
        end = time()
        mem_usage = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        if is_selected:
            replay_solution(board, board.dir_list)
        print_results(board, 1, 0, 0, 1, end - start, mem_usage)
        return board
    
    node = deepcopy(board)
    nodes_generated += 1
    frontier = []
    heapq.heappush(frontier, (node.cost, node))
    reached = dict()
    reached[(tuple(node.stones), node.player)] = node.cost
    
    while len(frontier) > 0:
        _, cur_node = heapq.heappop(frontier)
        
        if cur_node.is_win():
            end = time()
            mem_usage = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            if is_selected:
                replay_solution(board, cur_node.dir_list)
            print_results(cur_node, nodes_generated, end - start, mem_usage)
            return cur_node
                
        moves = cur_node.moves_available()
        for m in moves:
            child = cur_node.clone_with_move(m)
            nodes_generated += 1
            
            if not child.is_deadlock() and ((tuple(child.stones), child.player) not in reached or child.cost < reached[(tuple(child.stones), child.player)]):
                reached[(tuple(child.stones), child.player)] = child.cost
                heapq.heappush(frontier, (child.cost, child))
                
    tracemalloc.stop()
    print("Solution not found")
    return
