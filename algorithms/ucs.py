import tracemalloc
import heapq
from time import time
from copy import deepcopy

def print_results(board, gen, dur, mem_usage):
    print("Algorithm: UCS")
    print("Steps: {}".format(len(board.dir_list)))
    print("Total cost: {}".format(board.cost))
    print("Node: {}".format(gen))
    print("Time: {:.2f} ms".format(dur * 1000))
    print("Memory: {:.2f} MB".format(mem_usage / 1024 / 1024))
    print("Solution: {}".format(''.join(board.dir_list)))

def replay_solution(start_board, end_board):
    replay_board = deepcopy(start_board)
    replay_board.print_board()  # In trạng thái bảng cuối cùng
    for dir in end_board.dir_list:
        # print(dir)
        replay_board.move(dir)
        # replay_board.print_board()  # In trạng thái bảng

def search(board):
    start = time()
    tracemalloc.start()
    nodes_generated = 0
    
    if board.is_win():
        end = time()
        mem_usage = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        replay_solution(board, board)
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
            replay_solution(board, cur_node)
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
