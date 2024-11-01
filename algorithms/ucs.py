from time import time
from copy import deepcopy
import heapq
import tracemalloc

def print_results(board, gen, dur, mem_usage):
    print("Algorithm: UCS")
    print("Steps: {}".format(len(board.dir_list)))
    print("Total cost {}: ".format(board.cost))
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
    frontier_set = set()
    heapq.heappush(frontier, (node.cost, node))
    frontier_set.add(node)
    
    explored = set()
    
    while frontier:
        # Pop the node with the lowest cost
        _, cur_node = heapq.heappop(frontier)
        frontier_set.remove(cur_node)
        
        if cur_node.is_win():
            end = time()
            mem_usage = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            print_results(cur_node, nodes_generated, end - start, mem_usage)
            return cur_node
        
        explored.add(cur_node)
        
        for move in cur_node.moves_available():
            child = deepcopy(cur_node)
            child.move(move)
            nodes_generated += 1
            
            if child not in explored and child not in frontier_set:
                heapq.heappush(frontier, (child.cost, child))
                frontier_set.add(child)
            elif child in frontier_set:
                # Check if there's a node with higher cost and replace it
                existing_child = next(n for cost, n in frontier if n == child)
                if child.cost < existing_child.cost:
                    frontier.remove((existing_child.cost, existing_child))
                    heapq.heappush(frontier, (child.cost, child))
                    frontier_set.add(child)
    
    tracemalloc.stop()
    print("Solution not found")
    return
