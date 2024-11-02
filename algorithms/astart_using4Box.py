import numpy as np
from collections import deque
from scipy.optimize import linear_sum_assignment
import numpy as np
import math
import heapq

rock_weight = [12, 11, 10, 11, 21, 31]
#rock_weight = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#line0 = " #####   "
import numpy as np
import math
from collections import deque
from scipy.optimize import linear_sum_assignment

# Input lines of Sokoban map
lines = [
    "    #####          ",
    "    #   #          ",
    "    #$  #          ",
    "  ###  $##         ",
    "  #  $ $ #         ",
    "### # ## #   ######",
    "#   # ## #####  ..#",
    "# $  $          ..#",
    "##### ### #@##  ..#",
    "    #     #########",
    "    #######        "
]

# Chuyển đổi từng dòng thành mảng 2 chiều
array_2d = [list(line) for line in lines]

cleaned_lines = [line.replace('$', ' ').replace('@', ' ') for line in lines]
array_2d_debug = [list(line) for line in cleaned_lines]


# Khởi tạo distance_grid với các khoảng cách ban đầu là inf
distance_grid = [[[] for _ in row] for row in array_2d]

# Hàm tính khoảng cách từ một ô mục tiêu tới tất cả các ô khác trong grid
def bfs(goal_position, player_position):
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

def printDebug(array_2d_debug, box_positions, player_position):
    copy_lines = [row.copy() for row in array_2d_debug]
    for x, y in box_positions:
        copy_lines[x][y] = '$'
    px, py = player_position
    copy_lines[px][py] = '@'
    for line in copy_lines:
        print("".join(line))

# Tiền xử lý để tìm tất cả các vị trí đích và hộp, cũng như đánh dấu các ô bế tắc
def preProcessing(array_2d, distance_grid):
    box_positions = []
    goal_positions = []
    for i in range(len(array_2d)):
        for j in range(len(array_2d[0])):
            if array_2d[i][j] == ".":  # Đích
                bfs((i, j), (4, 3))
                goal_positions.append((i, j))
            if array_2d[i][j] == "$":  # Hộp
                box_positions.append((i, j))

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
    
    try:
        # Find the index of the old position
        index = box_positions_list.index(old_position)
        # Update the position
        box_positions_list[index] = new_position
        #print(f"Updated box_positions: {box_positions_list}")
    except ValueError:
        #print("Position not found in box_positions.")
        return
    
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

def is4Box(cur_box, update_pos, movement):
    x, y = cur_box
    dx, dy = movement
    tmpx, tmpy = dx + x, dy + y

    if array_2d[x][y] == ".":
        return False
    

    if dx == -1 and dy == 0:        # trên đụng
        if array_2d[tmpx][tmpy] == "#" or (tmpx,tmpy) in update_pos:    # trên đụng
            if array_2d[x][y - 1] == "#" or (x,y - 1) in update_pos:  # trái đụng
                if array_2d[tmpx][tmpy - 1] == "#" or (tmpx, tmpy - 1) in update_pos:    # trái trên dụng
                    #print("TRUE1")
                    return True

            elif (array_2d[x][y + 1] == "#" or (x,y + 1) in update_pos):  # phải đụng
                if array_2d[tmpx][tmpy + 1] == "#" or (tmpx,tmpy + 1) in update_pos:  # phải trên đụng
                    #print("TRUE3!")
                    return True

    elif dx == 1 and dy == 0:       # dưới đụng
        if array_2d[tmpx][tmpy] == "#" or (tmpx,tmpy) in update_pos:    # dưới đụng
            if array_2d[x][y - 1] == "#" or (x,y - 1) in update_pos:  # trái đụng
                if array_2d[tmpx][tmpy - 1] == "#" or (tmpx,tmpy - 1) in update_pos:    # trái dưới dụng
                    #print("TRUE2!")
                    return True

            elif (array_2d[x][y + 1] == "#" or (x,y + 1) in update_pos):  # phải đụng
                if array_2d[tmpx][tmpy + 1] == "#" or (tmpx,tmpy + 1) in update_pos:  # phải dưới đụng
                    #print("TRUE4!")
                    return True
            

    elif dx == 0 and dy == -1:      # trái đụng
        if array_2d[tmpx][tmpy] == "#" or (tmpx,tmpy) in update_pos:    # trái đụng
            if array_2d[x - 1][y] == "#" or (x - 1,y) in update_pos:  # trên đụng
                if array_2d[tmpx - 1][tmpy] == "#" or (tmpx - 1,tmpy) in update_pos:    # trái trên dụng
                    #print("TRUE5!")
                    return True

            elif array_2d[x + 1][y] == "#" or (x + 1,y) in update_pos:  # dưới đụng
                if array_2d[tmpx + 1][tmpy] == "#" or (tmpx + 1,tmpy) in update_pos:  # trái dưới đụng
                    #print("TRUE6!")
                    return True


    elif dx == 0 and dy == 1:       # phải đụng
        if array_2d[tmpx][tmpy] == "#" or (tmpx,tmpy) in update_pos:    # phải đụng
            if array_2d[x - 1][y] == "#" or (x - 1,y) in update_pos:  # trên đụng
                if array_2d[tmpx - 1][tmpy] == "#" or (tmpx - 1,tmpy) in update_pos:    # phải trên dụng
                    #print("TRUE7!")
                    return True

            elif array_2d[x + 1][y] == "#" or (x + 1,y) in update_pos:  # dưới đụng
                if array_2d[tmpx + 1][tmpy] == "#" or (tmpx + 1,tmpy) in update_pos:  # phải dưới đụng
                    #print("TRUE8!")
                    return True
    return False

def a_star(start, goal_positions, box_positions, distance_grid, rock_weight):
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
    #visited.add(start_ver : h_score[start_ver])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # trên, dưới, trái, phải
    
    while open_set:
        # node <- pop(frontier)
        f, current_ver = heapq.heappop(open_set)
        cur_player, cur_boxes = current_ver
        x, y = cur_player
        #printDebug(array_2d_debug, cur_boxes, cur_player)
        #print(f)

        # if problem.IS-GOAL(node.STATE) then return node
        if terminal(cur_boxes, goal_positions):  # Nếu đạt được trạng thái đích
            return reconstruct_path(came_from, current_ver, start)

        # for each child in expand
        for dx, dy in directions:
            x_next, y_next = x + dx, y + dy
            x_fur, y_fur = x + 2 * dx, y + 2 * dy
           # printDebug(array_2d_debug, cur_boxes, cur_player)
            if 0 <= x_next < rows and 0 <= y_next < cols:
                # if box
                #print("ALID")
                if (x_next, y_next) in cur_boxes: # if box, next not # or $
                    # if box can move
                    if (x_fur, y_fur) not in cur_boxes and array_2d[x_fur][y_fur] != "#" and array_2d[x_fur][y_fur] != "x":
                        update_boxes = update_position((x_next, y_next), (x_fur, y_fur), cur_boxes)
                        successor_ver  = ((x_next, y_next), tuple(update_boxes))
                        if (not is4Box((x_fur, y_fur),update_boxes, (dx, dy))):
                            h_score_cur = 0
                            try:
                                h_score_cur = h_score[successor_ver[1]] # try here
                                h_score_cur += playerToBox((x_next, y_next), update_boxes, goal_positions)
                                g_score_cur = g_score[current_ver]  + 1 # + getWeight((x_fur, y_fur), update_boxes, rock_weight) 
                                f_score_cur = g_score_cur + h_score_cur
                                #print(visited)
                                if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                    #printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                                    #print(f_score_cur)
                                    visited[successor_ver] = f_score_cur
                                    g_score[successor_ver] = g_score_cur
                                    heapq.heappush(open_set, (f_score_cur, successor_ver))
                                    came_from[successor_ver] = current_ver
                                    #print("ADD")
                            except Exception as e:
                                h_score_cur, ok = heuristic(rock_weight, distance_grid, update_boxes)   # try here again
                                if ok:
                                    h_score[successor_ver[1]] = h_score_cur
                                    h_score_cur += playerToBox((x_next, y_next), update_boxes, goal_positions)
                                    g_score_cur = g_score[current_ver] + 1 # + getWeight((x_fur, y_fur), update_boxes, rock_weight)
                                    f_score_cur = g_score_cur + h_score_cur
                                    #print(visited)
                                    if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                        #printDebug(array_2d_debug, update_boxes, (x_next, y_next))
                                        #print(f_score_cur)
                                        visited[successor_ver] = f_score_cur
                                        g_score[successor_ver] = g_score_cur
                                        heapq.heappush(open_set, (f_score_cur, successor_ver))
                                        came_from[successor_ver] = current_ver
                                        #print("ADD")
                # if space
                elif array_2d[x_next][y_next] != "#": # space, teleport, deadlock
                    successor_ver  = ((x_next, y_next), tuple(cur_boxes))
                    h_score_cur = 0
                    try:
                        
                        h_score_cur = h_score[successor_ver[1]]
                        g_score_cur = g_score[current_ver] + 1
                        h_score_cur += playerToBox((x_next, y_next), cur_boxes, goal_positions)
                        f_score_cur = g_score_cur + h_score_cur
                        #print(visited)
                        if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                            #print(f_score_cur)
                            #printDebug(array_2d_debug, cur_boxes, (x_next, y_next))
                            visited[successor_ver] = f_score_cur
                            g_score[successor_ver] = g_score_cur
                            heapq.heappush(open_set, (f_score_cur, successor_ver))
                            came_from[successor_ver] = current_ver
                            #print("ADD")

                    except Exception as e:
                        h_score_cur, ok = heuristic(rock_weight, distance_grid, cur_boxes)
                        if ok:
                            h_score[successor_ver[1]] = h_score_cur
                            g_score_cur = g_score[current_ver] + 1
                            h_score_cur += playerToBox((x_next, y_next), cur_boxes, goal_positions)
                            f_score_cur = g_score_cur + h_score_cur
                            #print(visited)
                            if (successor_ver not in visited) or (f_score_cur < (visited[successor_ver])):
                                #print(f_score_cur)
                                #printDebug(array_2d_debug, cur_boxes, (x_next, y_next))
                                visited[successor_ver] = f_score_cur
                                g_score[successor_ver] = g_score_cur
                                heapq.heappush(open_set, (f_score_cur, successor_ver))
                                came_from[successor_ver] = current_ver
                                #print("ADD")
                        
                        
    return None  # Không tìm thấy đường đi

def reconstruct_path(came_from, current, start):
    path = []
    while current in came_from:
        path.append(current[0])
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

# Hàm lấy các ô lân cận của một ô

# Thực hiện tìm kiếm từ vị trí bắt đầu
#start_position = (8, 11)  # Vị trí của người chơi
start_position = (8, 11)
array_2d, distance_grid, box_positions, goal_positions = preProcessing(array_2d, distance_grid)

path = a_star(start_position, goal_positions, box_positions, distance_grid, rock_weight)
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

# Get directions based on coordinates
#print(path)
directions = get_directions(path)
print(directions)
