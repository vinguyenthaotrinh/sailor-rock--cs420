import numpy as np
from collections import deque
from scipy.optimize import linear_sum_assignment
import numpy as np
from time import time
from manager.board import Board
import tracemalloc
import math
import heapq
direct = [(-1, 0), (1, 0), (0, -1), (0, 1)]
directions = [((-1, 0), (1, 0)), ((1, 0), (-1, 0)), ((0, -1), (0, 1)), ((0, 1), (0, -1))]  # trên, dưới, trái, phải
    

array_2d_debug = [[' ' for i in range(10)] for j in range(10)]

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

            if 0 <= x_box < rows and 0 <= y_box < cols:
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
    print(hungarian_array)
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
    if visited == 2:      # đã check thì block
        return True
    if (x, y) in update_boxes:
        if canMoveBox(cur_pos, update_boxes, matrix):
            return False
        else:
            for direction in directions:
                pre, nxt = direction
                p_x, p_y = pre
                n_x, n_y = nxt
                x_next, y_next = x + p_x, y + p_y
                x_pre, y_pre = x + n_x, y + n_y
                #x_next, y_next = x + nxt[0], y + nxt[1]
                #x_pre, y_pre = x + pre[0], y + pre[1]
                if not deadlock((x_next, y_next),update_boxes, matrix, visited + 1) and not deadlock((x_pre, y_pre),update_boxes, matrix, visited + 1):
                    return False
    return True

# check is box and can move
def canMoveBox(cur_box, update_pos, matrix):
    x, y = cur_box
    for p, n in directions:
        #x_next, y_next = x + n[0], y + n[1]
        #x_pre, y_pre = x + p[0], y + p[1]
        p_x, p_y = p
        n_x, n_y = n
            
        x_next, y_next = x + p_x, y + p_y
        x_pre, y_pre = x + n_x, y + n_y
        if matrix[x_next][y_next] != "#" and ((x_next, y_next) not in update_pos):   # đằng trước không trống
            if matrix[x_pre][y_pre] != "#" and ((x_pre, y_pre) not in update_pos): # đằng trước trống -> pre trống
                return True
    return False


def printDebug(array_2d_debug, box_positions, player_position):
    copy_lines = [row.copy() for row in array_2d_debug]
    for x, y in box_positions:
        copy_lines[x][y] = '$'
    px, py = player_position
    copy_lines[px][py] = '@'
    for line in copy_lines:
        print("".join(line))
        
def a_star(board, matrix, distance_grid):

    rows, cols = board.rows, board.cols
    rock_weight = board.weights
    goal_positions = board.switches
    box_pos = board.stones
    
    open_set = []
    came_from = {}

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
            return reconstruct_path(came_from, current_ver, board.player)

        for dx, dy in direct:
            x_next, y_next = x + dx, y + dy
            x_fur, y_fur = x + 2 * dx, y + 2 * dy
            if 0 <= x_next < rows and 0 <= y_next < cols:
                # if box
                if (x_next, y_next) in cur_boxes: # if box, next not # or $
                    #print("BOX")
                    # if box can move
                    if (x_fur, y_fur) not in cur_boxes and matrix[x_fur][y_fur] != "#" and matrix[x_fur][y_fur] != "x":
                        update_boxes = update_position((x_next, y_next), (x_fur, y_fur), cur_boxes)
                        successor_ver  = ((x_next, y_next), tuple(update_boxes))
                        if (x_fur, y_fur) in goal_positions or not deadlock((x_fur, y_fur),update_boxes, matrix, 0):
                            h_score_cur = 0
                            try:
                                h_score_cur = h_score[successor_ver[1]] # try here
                                h_score_cur += playerToBox((x_next, y_next), update_boxes)
                                g_score_cur = g_score[current_ver]  + 1 + getWeight((x_fur, y_fur), update_boxes, rock_weight) 
                                f_score_cur = g_score_cur + 2 * h_score_cur
                                if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                    #printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                                    visited[successor_ver] = f_score_cur
                                    g_score[successor_ver] = g_score_cur
                                    #print(h_score_cur)
                                    heapq.heappush(open_set, (f_score_cur, successor_ver))
                                    came_from[successor_ver] = current_ver
                                    #print(f_score_cur)
                            except Exception as e:
                                h_score_cur, ok = heuristic(rock_weight, distance_grid, update_boxes)   # try here again
                                if ok:
                                    h_score[successor_ver[1]] = h_score_cur
                                    h_score_cur += playerToBox((x_next, y_next), update_boxes)
                                    #print(h_score_cur)
                                    g_score_cur = g_score[current_ver] + 1 + getWeight((x_fur, y_fur), update_boxes, rock_weight)
                                    f_score_cur = g_score_cur +2 * h_score_cur
                                    if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                        #printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                                        visited[successor_ver] = f_score_cur
                                        g_score[successor_ver] = g_score_cur
                                        heapq.heappush(open_set, (f_score_cur, successor_ver))
                                        came_from[successor_ver] = current_ver
                                        #print(f_score_cur)
                        #else:
                        #    print("deadlock")
                        #    printDebug(array_2d_debug, update_boxes, (x_next, y_next))

                # if space
                elif matrix[x_next][y_next] != "#": # space, teleport, deadlock
                    #print("SPACE")
                    successor_ver  = ((x_next, y_next), tuple(cur_boxes))
                    h_score_cur = 0
                    try:
                        h_score_cur = h_score[successor_ver[1]]
                        g_score_cur = g_score[current_ver] + 1
                        h_score_cur += playerToBox((x_next, y_next), cur_boxes)
                        f_score_cur = g_score_cur + 2 * h_score_cur
                        if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                            #printDebug(array_2d_debug, cur_boxes, (x_next, y_next))

                            visited[successor_ver] = f_score_cur
                            g_score[successor_ver] = g_score_cur
                            heapq.heappush(open_set, (f_score_cur, successor_ver))
                            came_from[successor_ver] = current_ver
                            #print(f_score_cur)

                    except Exception as e:
                        h_score_cur, ok = heuristic(rock_weight, distance_grid, cur_boxes)
                        if ok:
                            h_score[successor_ver[1]] = h_score_cur
                            g_score_cur = g_score[current_ver] + 1
                            h_score_cur += playerToBox((x_next, y_next), cur_boxes)
                            f_score_cur = g_score_cur + 2 * h_score_cur
                            if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                
                                #printDebug(array_2d_debug, cur_boxes, (x_next, y_next))
                                visited[successor_ver] = f_score_cur
                                g_score[successor_ver] = g_score_cur
                                heapq.heappush(open_set, (f_score_cur, successor_ver))
                                came_from[successor_ver] = current_ver

    print("NO ANSWR")
    return
'''
        # for each child in expand
        for dx, dy in direct:
            x_next, y_next = x + dx, y + dy
            x_fur, y_fur = x + 2 * dx, y + 2 * dy
            successor_ver = ()
            canGo = False
            if (x_next, y_next) in cur_boxes:   # if box
                if (x_fur, y_fur) not in cur_boxes and matrix[x_fur][y_fur] != "#" and matrix[x_fur][y_fur] != "x":# if box can move
                    update_boxes = update_position((x_next, y_next), (x_fur, y_fur), cur_boxes)
                    successor_ver  = ((x_next, y_next), tuple(update_boxes))
                    if (x_fur, y_fur) in goal_positions or not deadlock((x_fur, y_fur),update_boxes, matrix, 0):
                        h_score_cur, canGo = heuristic(rock_weight, distance_grid, update_boxes)   # try here again
                        if canGo:
                            h_score[successor_ver[1]] = h_score_cur
                            h_score_cur += playerToBox((x_next, y_next), update_boxes)
                            g_score_cur = g_score[current_ver] + 1 + getWeight((x_fur, y_fur), update_boxes, rock_weight)

            elif matrix[x_next][y_next] != "#": # if space
                successor_ver  = ((x_next, y_next), tuple(cur_boxes))
                g_score_cur = g_score[current_ver] + 1
                h_score_cur = h_score[successor_ver[1]] + playerToBox((x_next, y_next), cur_boxes)
                canGo = True
                
            if canGo:
                f_score_cur = g_score_cur + 2 * h_score_cur
                if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                    visited[successor_ver] = f_score_cur
                    g_score[successor_ver] = g_score_cur
                    heapq.heappush(open_set, (f_score_cur, successor_ver))
                    came_from[successor_ver] = current_ver
'''
  #  return None  # Không tìm thấy đường đi


def reconstruct_path(came_from, current, start):
    n = 0
    path = []
    while current in came_from:
        path.append(current[0])
        current = came_from[current]
        n += 1
    path.append(start)
    path.reverse()
    return path, n


def get_directions(coords):
    move = []
    for i in range(1, len(coords)):
        prev = coords[i - 1]
        curr = coords[i]
        if curr[0] == prev[0] - 1 and curr[1] == prev[1]:
            if curr[1] == prev[1]:
                move.append("u")
            else:
                move.append("U")
        elif curr[0] == prev[0] + 1 and curr[1] == prev[1]:
            if curr[1] == prev[1]:
                move.append("d")
            else:
                move.append("D")
        elif curr[0] == prev[0] and curr[1] == prev[1] + 1:
            if curr[1] == prev[1]:
                move.append("r")
            else:
                move.append("R")
        elif curr[0] == prev[0] and curr[1] == prev[1] - 1:
            if curr[1] == prev[1]:
                move.append("l")
            else:
                move.append("L")
    return ''.join(move)



def search(board):
    start = time()
    tracemalloc.start()
    nodes_generated = 0

    matrix = board.get_matrix()

    matrix, distance_grid= preProcessing(board, matrix)
    for m in matrix:
        print(m)
    #print(distance_grid
    #print("preprocessing")

    n = 0
    path, n = a_star(board, matrix, distance_grid)

    move = get_directions(path)
    print(move)
    print(len(move))

                
    #tracemalloc.stop()
    return
