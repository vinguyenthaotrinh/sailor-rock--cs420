# bfs.py
import tracemalloc
import collections
from time import time
from copy import deepcopy

def print_results(board, gen, dur, mem_usage):
    print("Algorithm: BFS")
    print("Steps: {}".format(len(board.dir_list)))
    print("Total cost {}: ".format(board.cost))
    print("Node: {}".format(gen))
    print("Time: {:.2f} ms".format(dur * 1000))
    print("Memory: {:.2f} MB".format(mem_usage / 1024 / 1024))
    print("Solution: {}".format(''.join(board.dir_list)))
    
def replay_solution(start_board, end_board):
    replay_board = deepcopy(start_board)
    replay_board.print_board()  # In trạng thái bảng cuối cùng
    end_board.dir_list = []
    st = "rruuuuruulldrurdldddddlluurlddrruuuurrrurddullluulldrurdldddlldrdruuuurrrurdllluulldrurdldrrr"
    for i in range(len(st)):
        end_board.dir_list.append(st[i])
    for dir in end_board.dir_list:
        print(dir)
        replay_board.move(dir)
        replay_board.print_board()  # In trạng thái bảng

def search(board):
    replay_solution(board, board)
    # start = time()
    # tracemalloc.start()  # Bắt đầu theo dõi bộ nhớ
    # nodes_generated = 0
    
    # if board.is_win():
    #     end = time()
    #     mem_usage = tracemalloc.get_traced_memory()[1]
    #     tracemalloc.stop()
    #     replay_solution(board, board)
    #     print_results(board, 1, end - start, mem_usage)
    #     return board
    
    # node = deepcopy(board)
    # nodes_generated += 1
    # frontier = collections.deque()
    # frontier.append(node)
    # reached = set()
    # reached.add(node)
    
    # while len(frontier) > 0:
    #     cur_node = frontier.popleft()
    #     moves = cur_node.moves_available()
        
    #     for m in moves:
    #         child = cur_node.clone_with_move(m)
    #         nodes_generated += 1
    #         child.move(m)
    #         if child.is_win():
    #             end = time()
    #             mem_usage = tracemalloc.get_traced_memory()[1]
    #             tracemalloc.stop()
    #             replay_solution(board, child)
    #             print_results(child, nodes_generated, end - start, mem_usage)
    #             return child
    #         if child not in reached:
    #             frontier.append(child)
    #             reached.add(child)
    
    # tracemalloc.stop()
    # print("Solution not found")
    return
