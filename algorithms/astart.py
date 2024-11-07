import numpy as np
from collections import deque
from scipy.optimize import linear_sum_assignment
import math
import heapq
from manager.board import Board
import tracemalloc
from time import time
from copy import deepcopy


# Hàm tính khoảng cách từ một ô mục tiêu tới tất cả các ô khác trong grid
def bfs(goal_position):
    rows, cols = len(array_2d), len(array_2d[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # trên, dưới, trái, phải
    
    queue = deque([goal_position])
    distances = [[math.inf] * cols for _ in range(rows)]
    x, y = goal_position
    distances[x][y] = 0  # Đặt khoảng cách tại mục tiêu là 0

    while queue:
        x, y = queue.popleft()
        current_distance = distances[x][y]
        for dx, dy in directions:
            x_box, y_box = x + dx, y + dy
            x_player, y_player = x + 2 * dx, y + 2 * dy
            
            if 0 <= x_box < rows and 0 <= y_box < cols:
                if 0 <= x_player < rows and 0 <= y_player < cols:
                    if distances[x_box][y_box] == math.inf:  # Chưa ghé thăm
                        if array_2d[x_box][y_box] != "#" and array_2d[x_player][y_player] != "#":
                            distances[x_box][y_box] = current_distance + 1
                            queue.append((x_box, y_box))

    # Cập nhật khoảng cách vào distance_grid
    for i in range(rows):
        for j in range(cols):
            distance_grid[i][j].append(distances[i][j])

# Tiền xử lý để tìm tất cả các vị trí đích và hộp, cũng như đánh dấu các ô bế tắc
def preProcessing(array_2d, distance_grid):
    box_positions = []
    goal_positions = []
    for i in range(len(array_2d)):
        for j in range(len(array_2d[0])):
            if array_2d[i][j] == "." or array_2d[i][j] == "*":  # Đích
                bfs((i, j), (4, 3))


    # Đánh dấu các ô bế tắc
    for i in range(len(array_2d)):
        for j in range(len(array_2d[0])):
            if distance_grid[i][j] == [math.inf] * len(distance_grid[0][0]):
                if array_2d[i][j] != "#":
                    array_2d[i][j] = "x"  # Đánh dấu ô bế tắc

    return array_2d, distance_grid, box_positions, goal_positions


# Định nghĩa hàm heuristic
def heuristic(rock_weight, distance_grid, box_positions):
    # Tạo mảng Hungarian với các trọng số
    hungarian_array = [
        [distance * rock_weight[i] for distance in distance_grid[box[0]][box[1]]]
        for i, box in enumerate(box_positions)
    ]

    cost = np.array(hungarian_array)
    #print("\nHungarian Cost Matrix:\n", hungarian_array)
    try:
        row_ind, col_ind = linear_sum_assignment(cost)
        #print("\nOptimal Assignment for Boxes to Goals:\n", col_ind)
        return cost[row_ind, col_ind].sum(), True
    except Exception as e:
        return -1000000, False

def terminal(box_positions, goal_positions):
    result = True 
    for box in box_positions:
        if box not in goal_positions:
            result = False
            return result
    return result

def getWeight(box, box_cur_posisitons, rock_weight):
    position_to_weight = dict(zip(box_cur_posisitons, rock_weight))
    return position_to_weight.get(box, "Position not found")

def update_position(old_position, new_position, box_positions):
    # Convert the tuple to a list
    box_positions_list = list(box_positions)
    index = box_positions_list.index(old_position)
    box_positions_list[index] = new_position
    # Convert back to a tuple if needed
    return tuple(box_positions_list)

def playerToBox(player, box_positions, goal_positions):
    # Initialize the minimum distance as infinity
    min_distance = float('inf')

    # Find the closest box based on Manhattan distance
    for box in box_positions:
        #if box not in goal_positions:
            # Calculate the Manhattan distance (dx + dy)
        dx = abs(box[0] - player[0])
        dy = abs(box[1] - player[1])
        distance = dx + dy
            
            # Update min_distance if this box is closer
        if distance < min_distance:
            min_distance, x, y = distance, box[0], box[1]

    weight = getWeight((x, y), box_positions, rock_weight)
    return min_distance * weight

def deadlock(cur_pos,update_boxes, movement, visited):
    #print("CHECK")
    #print(cur_pos)
    #print(update_boxes)
    x, y = cur_pos
    if array_2d[x][y] == "#":   # là tường thì không đi được
        return True
    if array_2d[x][y] != "#" and (x,y) not in update_boxes:
        return False
    if visited == 2:      # đã check thì block
        return True

    if (x, y) in update_boxes:
        #print(cur_pos)
        #print(canMoveBox(cur_pos, update_boxes))
        
        if canMoveBox(cur_pos, update_boxes):
            return False
        else:
            directions = [((-1, 0), (1, 0)), ((1, 0), (-1, 0)), ((0, -1), (0, 1)), ((0, 1), (0, -1))]  # trên, dưới, trái, phải
            for direction in directions:
                pre, nxt = direction
                p_x, p_y = pre
                n_x, n_y = nxt
                x_next, y_next = x + p_x, y + p_y
                x_pre, y_pre = x + n_x, y + n_y
                if not deadlock((x_next, y_next),update_boxes, movement, visited + 1) and not deadlock((x_pre, y_pre),update_boxes, movement, visited + 1):
                    return False
    return True

def canMoveBox(cur_box, update_pos):
    x, y = cur_box
    directions = [((-1, 0), (1, 0)), ((1, 0), (-1, 0)), ((0, -1), (0, 1)), ((0, 1), (0, -1))]  # trên, dưới, trái, phải
    for p, n in directions:
        p_x, p_y = p
        n_x, n_y = n
            
        x_next, y_next = x + p_x, y + p_y
        x_pre, y_pre = x + n_x, y + n_y
        if array_2d[x_next][y_next] != "#" and ((x_next, y_next) not in update_pos):   # đằng trước không trống
            if array_2d[x_pre][y_pre] != "#" and ((x_pre, y_pre) not in update_pos): # đằng trước trống -> pre trống
                return True
    return False

def a_star(start, goal_positions, box_positions, distance_grid, rock_weight, n):
    open_set = []
    rows, cols = len(array_2d), len(array_2d[0])
    came_from = {}
    # node <- NODE(STATE=problem.INITIAL)
    start_ver = (start, tuple(box_positions))
    g_score = {start_ver: 0}
    h_score = {tuple(box_positions): heuristic(rock_weight, distance_grid, box_positions)[0]}     # đá không đổi thì heuristic giữ nguyên
    # frontier <- a priority queue ordered by f, with node as an element
    heapq.heappush(open_set, (h_score[tuple(box_positions)], start_ver))# pq.push(rootVertex)
    visited = {start_ver : h_score[tuple(box_positions)]} # set = null
    # reached <- a lookup table, with one entry with key problem.INITIAL and value node
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # trên, dưới, trái, phải
    
    while open_set:
        # node <- pop(frontier)
        f, current_ver = heapq.heappop(open_set)
        cur_player, cur_boxes = current_ver
        x, y = cur_player

        # if problem.IS-GOAL(node.STATE) then return node
        if terminal(cur_boxes, goal_positions):  # Nếu đạt được trạng thái đích
            return reconstruct_path(came_from, current_ver, start, n)

        # for each child in expand
        for dx, dy in directions:
            x_next, y_next = x + dx, y + dy
            x_fur, y_fur = x + 2 * dx, y + 2 * dy
            if 0 <= x_next < rows and 0 <= y_next < cols:
                # if box
                if (x_next, y_next) in cur_boxes: # if box, next not # or $
                    # if box can move
                    if (x_fur, y_fur) not in cur_boxes and array_2d[x_fur][y_fur] != "#" and array_2d[x_fur][y_fur] != "x":
                        update_boxes = update_position((x_next, y_next), (x_fur, y_fur), cur_boxes)
                        successor_ver  = ((x_next, y_next), tuple(update_boxes))
                        if (x_fur, y_fur) in goal_positions or not deadlock((x_fur, y_fur),update_boxes, (dx, dy), 0):
                            h_score_cur = 0
                            try:
                                h_score_cur = h_score[successor_ver[1]] # try here
                                h_score_cur += playerToBox((x_next, y_next), update_boxes, goal_positions)
                                g_score_cur = g_score[current_ver]  + 1 # + getWeight((x_fur, y_fur), update_boxes, rock_weight) 
                                f_score_cur = g_score_cur + h_score_cur
                                if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                    #printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                                    visited[successor_ver] = f_score_cur
                                    g_score[successor_ver] = g_score_cur
                                    heapq.heappush(open_set, (f_score_cur, successor_ver))
                                    came_from[successor_ver] = current_ver
                            except Exception as e:
                                h_score_cur, ok = heuristic(rock_weight, distance_grid, update_boxes)   # try here again
                                if ok:
                                    h_score[successor_ver[1]] = h_score_cur
                                    h_score_cur += playerToBox((x_next, y_next), update_boxes, goal_positions)
                                    g_score_cur = g_score[current_ver] + 1 # + getWeight((x_fur, y_fur), update_boxes, rock_weight)
                                    f_score_cur = g_score_cur + h_score_cur
                                    if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                        #printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                                        visited[successor_ver] = f_score_cur
                                        g_score[successor_ver] = g_score_cur
                                        heapq.heappush(open_set, (f_score_cur, successor_ver))
                                        came_from[successor_ver] = current_ver
                        #else:
                        #    print("deadlock")
                        #    printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                # if space
                elif array_2d[x_next][y_next] != "#": # space, teleport, deadlock
                    successor_ver  = ((x_next, y_next), tuple(cur_boxes))
                    h_score_cur = 0
                    try:
                        
                        h_score_cur = h_score[successor_ver[1]]
                        g_score_cur = g_score[current_ver] + 1
                        h_score_cur += playerToBox((x_next, y_next), cur_boxes, goal_positions)
                        f_score_cur = g_score_cur + h_score_cur
                        if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                            #printDebug(array_2d_debug, cur_boxes, (x_next, y_next))
                            visited[successor_ver] = f_score_cur
                            g_score[successor_ver] = g_score_cur
                            heapq.heappush(open_set, (f_score_cur, successor_ver))
                            came_from[successor_ver] = current_ver

                    except Exception as e:
                        h_score_cur, ok = heuristic(rock_weight, distance_grid, cur_boxes)
                        if ok:
                            h_score[successor_ver[1]] = h_score_cur
                            g_score_cur = g_score[current_ver] + 1
                            h_score_cur += playerToBox((x_next, y_next), cur_boxes, goal_positions)
                            f_score_cur = g_score_cur + h_score_cur
                            if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                #printDebug(array_2d_debug, cur_boxes, (x_next, y_next))
                                visited[successor_ver] = f_score_cur
                                g_score[successor_ver] = g_score_cur
                                heapq.heappush(open_set, (f_score_cur, successor_ver))
                                came_from[successor_ver] = current_ver
    return None  # Không tìm thấy đường đi


def reconstruct_path(came_from, current, start, n):
    path = []
    while current in came_from:
        path.append(current[0])
        current = came_from[current]
        n += 1
    path.append(start)
    path.reverse()
    return path, n


def get_directions(coords):
    directions = []
    for i in range(1, len(coords)):
        prev = coords[i - 1]
        curr = coords[i]
        # Determine the direction
        if curr[0] == prev[0] - 1 and curr[1] == prev[1]:
            if curr[1] == prev[1]:
                directions.append("u")
            else:
                directions.append("U")
        elif curr[0] == prev[0] + 1 and curr[1] == prev[1]:
            if curr[1] == prev[1]:
                directions.append("d")
            else:
                directions.append("D")
        elif curr[0] == prev[0] and curr[1] == prev[1] + 1:
            if curr[1] == prev[1]:
                directions.append("r")
            else:
                directions.append("R")
        elif curr[0] == prev[0] and curr[1] == prev[1] - 1:
            if curr[1] == prev[1]:
                directions.append("l")
            else:
                directions.append("L")
    
    return ''.join(directions)


def search(board):
    start = time()
    tracemalloc.start()  # Bắt đầu theo dõi bộ nhớ
    nodes_generated = 0
    if board.is_win():
        end = time()
        mem_usage = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        replay_solution(board, board)
        print_results(board, 1, 0, 0, 1, end - start, mem_usage)
        return board

    
    array_2d, distance_grid, box_positions, goal_positions = preProcessing(array_2d, distance_grid)
    
    
    node = deepcopy(board)
    nodes_generated += 1
    frontier = collections.deque()
    frontier.append(node)
    reached = set()
    reached.add((tuple(node.stones), node.player))
    
    while len(frontier) > 0:
        cur_node = frontier.popleft()
        moves = cur_node.moves_available()
        
        for m in moves:
            child = cur_node.clone_with_move(m)
            nodes_generated += 1
            
            if child.is_win():
                end = time()
                mem_usage = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                replay_solution(board, child)
                print_results(child, nodes_generated, end - start, mem_usage)
                return child
            if not child.is_deadlock() and (tuple(child.stones), child.player) not in reached:
                frontier.append(child)
                reached.add((tuple(child.stones), child.player))
    
    tracemalloc.stop()
    print("Solution not found")
    return
    
