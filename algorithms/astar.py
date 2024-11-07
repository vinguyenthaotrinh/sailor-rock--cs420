import numpy as np
from collections import deque
from scipy.optimize import linear_sum_assignment
import numpy as np
from time import time
from manager.board import Board
from copy import deepcopy
import tracemalloc
import math
import heapq
direct = [(-1, 0), (1, 0), (0, -1), (0, 1)]
directions = [((-1, 0), (1, 0)), ((1, 0), (-1, 0)), ((0, -1), (0, 1)), ((0, 1), (0, -1))]  # trên, dưới, trái, phải


# heuristic: from each position to goals
def bfs(goal_position, board, distance_grid, matrix,num):
    rows, cols = board.rows, board.cols

    queue = deque([goal_position])
    distance_grid[goal_position[0]][goal_position[1]][num] = 0  # init 0

    while queue:
        x, y = queue.popleft()
        current_distance = distance_grid[x][y][num]
        for dx, dy in direct:
            x_box, y_box = x + dx, y + dy
            x_player, y_player = x + 2 * dx, y + 2 * dy

            if 0 <= x_player < rows and 0 <= y_player < cols:
                if distance_grid[x_box][y_box][num] == math.inf:  # not visit
                    if matrix[x_box][y_box] != "#" and matrix[x_player][y_player] != "#":
                        distance_grid[x_box][y_box][num] = current_distance + 1
                        queue.append((x_box, y_box))


# Tiền xử lý để tìm tất cả các vị trí đích và hộp, cũng như đánh dấu các ô bế tắc
def preProcessing(board, matrix):
    num_rock = len(board.weights)
    rows, cols = board.rows, board.cols
    distance_grid = [[[math.inf]*num_rock for i in range(cols)] for j in range(rows)]

    for num, (i, j) in enumerate(board.switches):
        bfs((i, j), board, distance_grid, matrix, num)
    # Đánh dấu các ô bế tắc
    for i in range(rows):
        for j in range(cols):
            if distance_grid[i][j] == [math.inf] * num_rock:
                if matrix[i][j] != "#":
                    matrix[i][j] = "x"  # Đánh dấu ô bế tắc
    return matrix, distance_grid        # deadlock matrix


# Định nghĩa hàm heuristic
def heuristic(rock_weight, distance_grid, box_positions):
    hungarian_array = [
        [distance * rock_weight[i] for distance in distance_grid[box[0]][box[1]]]
        for i, box in enumerate(box_positions)
    ]
    
    cost = np.array(hungarian_array)
    try:
        row_ind, col_ind = linear_sum_assignment(cost)
        return cost[row_ind, col_ind].sum(), True
    except Exception as e:
        return -math.inf, False

def terminal(box_positions, goal_positions):
    for box in box_positions:
        if box not in goal_positions:
            return False
    return True

def getWeight(box, box_cur_posisitons, rock_weight):
    position_to_weight = dict(zip(box_cur_posisitons, rock_weight))
    return position_to_weight.get(box, "Position not found")

def update_position(old_position, new_position, box_positions):
    update_box = []
    for position in box_positions:
        if position == old_position:
            update_box.append(new_position)
        else:
            update_box.append(position)
    return update_box

def playerToBox(player, box_positions):
    min_distance = math.inf
    for box in box_positions:
        dx = abs(box[0] - player[0])
        dy = abs(box[1] - player[1])
        distance = dx + dy
        if distance < min_distance:
            min_distance = distance
    return min_distance 

# check is deadlock
def deadlock(cur_pos,update_boxes, matrix, visited):
    x, y = cur_pos
    if matrix[x][y] == "#":   # là tường thì không đi được
        return True
    if matrix[x][y] != "#" and (x,y) not in update_boxes:
        return False
    if visited == 3:      # đã check thì block
        return True
    if (x, y) in update_boxes:
        if canMoveBox(cur_pos, update_boxes, matrix):
            return False
        else:
            for direction in directions:
                pre, nxt = direction
                x_next, y_next = x + nxt[0], y + nxt[1]
                x_pre, y_pre = x + pre[0], y + pre[1]
                if not deadlock((x_next, y_next),update_boxes, matrix, visited + 1) and not deadlock((x_pre, y_pre),update_boxes, matrix, visited + 1):
                    return False
    return True

# check is box and can move
def canMoveBox(cur_box, update_pos, matrix):
    x, y = cur_box
    for p, n in directions:
        x_next, y_next = x + n[0], y + n[1]
        x_pre, y_pre = x + p[0], y + p[1]

        if matrix[x_next][y_next] != "#" and ((x_next, y_next) not in update_pos):   # đằng trước không trống
            if matrix[x_pre][y_pre] != "#" and ((x_pre, y_pre) not in update_pos): # đằng trước trống -> pre trống
                return True
    return False
        
def a_star(board, matrix, distance_grid):
    weighted = 2
    rows, cols = board.rows, board.cols
    rock_weight = board.weights
    goal_positions = board.switches
    box_pos = board.stones
    
    open_set = []
    came_from = {}
    gen = 1

    start_ver = (board.player, tuple(box_pos))
    h_score_start = heuristic(rock_weight, distance_grid, box_pos)[0]

    g_score = {start_ver: 0}
    h_score = {tuple(box_pos): h_score_start}
    heapq.heappush(open_set, (h_score_start, start_ver))
    visited = {start_ver : h_score_start}

    while open_set:
        f_score, current_ver = heapq.heappop(open_set)
        cur_player, cur_boxes = current_ver

        x, y = cur_player
        if terminal(cur_boxes, goal_positions):
            path, cost = reconstruct_path(came_from, current_ver, start_ver)
            return path, cost, gen

        for dx, dy in direct:
            x_next, y_next = x + dx, y + dy
            x_fur, y_fur = x + 2 * dx, y + 2 * dy
            canGo = False
            if 0 <= x_next < rows and 0 <= y_next < cols:
                g_score_pre = g_score[current_ver]
                g_score_cur = g_score_pre + 1
                gen += 1
                
                if (x_next, y_next) in cur_boxes:       # if box
                    if (x_fur, y_fur) not in cur_boxes and matrix[x_fur][y_fur] != "#" and matrix[x_fur][y_fur] != "x": # if can go
                        update_boxes = update_position((x_next, y_next), (x_fur, y_fur), cur_boxes)
                        successor_ver  = ((x_next, y_next), tuple(update_boxes))
                        if (x_fur, y_fur) in goal_positions or not deadlock((x_fur, y_fur),update_boxes, matrix, 0):    # if not deadlock
                            h_score_cur, canGo = heuristic(rock_weight, distance_grid, update_boxes)   # try here again
                            if canGo:
                                h_score[successor_ver[1]] = h_score_cur
                                h_score_cur += playerToBox((x_next, y_next), update_boxes)
                                g_score_cur += getWeight((x_fur, y_fur), update_boxes, rock_weight)
                elif matrix[x_next][y_next] != "#":     # if space
                    successor_ver, canGo = ((x_next, y_next), tuple(cur_boxes)), True
                    h_score_cur = h_score[successor_ver[1]] + playerToBox((x_next, y_next), cur_boxes)
                    
                if canGo:
                    f_score_cur = g_score_cur + weighted * h_score_cur
                    if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                        visited[successor_ver] = f_score_cur
                        g_score[successor_ver] = g_score_cur
                        heapq.heappush(open_set, (f_score_cur, successor_ver))
                        came_from[successor_ver] = (current_ver, g_score_cur - g_score_pre)
    tracemalloc.stop()
    return None  # Không tìm thấy đường đi


def reconstruct_path(came_from, current, start_ver):
    path = []
    cost = 0
    while current != start_ver:
        path.append(current)
        current, cost_tmp = came_from[current]
        cost += cost_tmp
        
    path.append(start_ver)
    path.reverse()
    return path, cost


def get_directions(coords):
    move = []
    for i in range(1, len(coords)):
        #print(coords)
        prev = coords[i - 1]
        curr = coords[i]

        if curr[0][0] == prev[0][0] - 1 and curr[0][1] == prev[0][1]:
            if curr[1] == prev[1]:
                move.append("u")
            else:
                move.append("U")
        elif curr[0][0] == prev[0][0] + 1 and curr[0][1] == prev[0][1]:
            if curr[1] == prev[1]:
                move.append("d")
            else:
                move.append("D")
        elif curr[0][0] == prev[0][0] and curr[0][1] == prev[0][1] + 1:
            if curr[1] == prev[1]:
                move.append("r")
            else:
                move.append("R")
        elif curr[0][0] == prev[0][0] and curr[0][1] == prev[0][1] - 1:
            if curr[1] == prev[1]:
                move.append("l")
            else:
                move.append("L")
    return ''.join(move)

def print_results(cost, gen, dur, mem_usage, move):
    with open(Board.output_file, "a") as file:
        file.write("\n\n")
        file.write("Algorithm: A*\n")
        file.write("Steps: {}\n".format(len(move)))
        file.write("Total cost: {}\n".format(cost))
        file.write("Node: {}\n".format(gen))
        file.write("Time: {:.2f} ms\n".format(dur * 1000))
        file.write("Memory: {:.2f} MB\n".format(mem_usage / 1024 / 1024))
        file.write("Solution: {}".format(move))

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

    matrix = board.get_matrix()
    # preprocessing
    matrix, distance_grid= preProcessing(board, matrix)
    # a star search
    path, cost, gen = a_star(board, matrix, distance_grid)
    # get dir
    move = get_directions(path)
    
    end = time()
    mem_usage = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    if is_selected:
        replay_solution(board, move)
            
    print_results(cost, gen, end - start, mem_usage, move)
    return
