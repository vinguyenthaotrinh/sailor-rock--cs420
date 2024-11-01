# board.py
from copy import deepcopy

dr = [-1, 1, 0, 0]
dc = [0, 0, -1, 1]
char_dir = ['u', 'd', 'l', 'r']

class Board:
    # Singleton attributes cho toàn bộ lớp Board
    rows = 0
    cols = 0
    weights = []
    switches = []
    walls = set()  # set of tuples
    
    def __init__(self):
        self.dir_list = []  # list of char for solution
        self.stones = []
        self.player = None  # tuple
        self.cost = 0  # used for UCS and heuristic searches

    @classmethod
    def configure(cls, weights_list, row_count, col_count, switches_list, walls_set):
        """
        Thiết lập singleton attributes cho toàn bộ instances
        """
        cls.rows = row_count
        cls.cols = col_count
        cls.weights = weights_list
        cls.switches = switches_list
        cls.walls = walls_set
    
    def __eq__(self, other):
        if self.stones == other.stones and self.player == other.player:
            return True
        else:
            return False

    def __hash__(self):
        return hash((tuple(self.stones), self.player))

    def __gt__(self, other):
        if self.cost > other.cost:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.cost < other.cost:
            return True
        else:
            return False

    def set_player(self, x, y):
        self.player = (x, y)        
        
    def add_stone(self, x, y):
        self.stones.append((x, y))
    
    def moves_available(self):
        ''' returns list of possible moves '''
        moves = []
        for index in range(4):
            if (self.player[0] + dr[index], self.player[1] + dc[index]) not in Board.walls:
                if (self.player[0] + dr[index], self.player[1] + dc[index]) in self.stones:
                    pos_behind = (self.player[0] + dr[index] * 2, self.player[1] + dc[index] * 2)
                    if pos_behind not in self.stones and pos_behind not in Board.walls:
                    # what if there's a wall or stone behind it?
                        moves.append(char_dir[index].upper())
                else:
                    moves.append(char_dir[index])
        return moves
    
    def move(self, dir):
        index_dir = char_dir.index(dir.lower())
        
        self.player = (self.player[0] + dr[index_dir], self.player[1] + dc[index_dir])
        self.dir_list.append(dir)
        self.cost += 1

        if self.player in self.stones:
            stone_index = self.stones.index(self.player)
            
            # Tính chi phí đẩy
            self.cost += Board.weights[stone_index]
            self.dir_list[-1] = dir.upper()
            
            # Cập nhật vị trí stone
            self.stones[stone_index] = (self.player[0] + dr[index_dir], self.player[1] + dc[index_dir])
            # self.ucsCost = 2
    
    def clone_with_move(self, move_dir):
        """
        Tạo bản sao trạng thái chỉ với thay đổi từ một bước di chuyển
        """
        index_dir = char_dir.index(move_dir.lower())
        new_board = Board()
        new_board.dir_list = self.dir_list + [move_dir]
        new_board.stones = self.stones.copy()
        new_board.player = (self.player[0] + dr[index_dir], self.player[1] + dc[index_dir])
        new_board.cost = self.cost + 1
        
        # Nếu là di chuyển đẩy stone, cập nhật vị trí stones và chi phí
        if new_board.player in self.stones:
            stone_index = self.stones.index(new_board.player)
            
            # Tính chi phí đẩy
            new_board.cost += Board.weights[stone_index]
            new_board.dir_list[-1] = move_dir.upper()
            
            # Cập nhật vị trí stone
            new_board.stones[stone_index] = (new_board.player[0] + dr[index_dir], new_board.player[1] + dc[index_dir])
            
        return new_board

    def is_win(self):
        if sorted(Board.switches) == sorted(self.stones):
            return True
        else:
            return False
    
    def get_matrix(self):
        matrix = [[' ' for i in range(self.cols)] for j in range(self.rows)]
        for wall in Board.walls:
            matrix[wall[0]][wall[1]] = '#'
        for switch in Board.switches:
            matrix[switch[0]][switch[1]] = '.'
        for stone in self.stones:
            if stone in Board.switches:
                matrix[stone[0]][stone[1]] = '*'
            else:
                matrix[stone[0]][stone[1]] = '$'
        if self.player in Board.switches:
            matrix[self.player[0]][self.player[1]] = '+'
        else:
            matrix[self.player[0]][self.player[1]] = '@'
            
        return matrix
            
    def print_board(self):
        matrix = self.get_matrix()
        for row in matrix:
            print(''.join(row))
        print("_" * 10)
        
    def get_board_as_string(self):
        matrix = self.get_matrix()
        board_str = '\n'.join(''.join(row) for row in matrix)  # Ghép các hàng thành chuỗi
        board_str += '\n' + "_" * 10  # Thêm dòng ngăn cách phía dưới
        return board_str
    
    ''' Check deadlock: stone on the corner of walls or other stones   '''
    def is_deadlock(self):
        mat = self.get_matrix()
        for stone in self.stones:
            x, y = stone
            if mat[x][y] == '*':
                continue
            #corner up-left
            if mat[x - 1][y] in ['#','$','*'] and mat[x][y - 1] in ['#','$','*']:
                if mat[x - 1][y - 1] in ['#','$','*']:
                    return True
                if mat[x - 1][y] == '#' and mat[x][y - 1] =='#':
                    return True
                if mat[x - 1][y] in ['$','*'] and mat[x][y - 1] in ['$','*']:
                    if mat[x - 1][y + 1] == '#' and mat[x + 1][y - 1] == '#':
                        return True
                if mat[x - 1][y] in ['$','*'] and mat[x][y - 1] == '#':
                    if mat[x - 1][y + 1] == '#':
                        return True
                if mat[x - 1][y] == '#' and mat[x][y - 1] in ['$','*']:
                    if mat[x + 1][y - 1] == '#':
                        return True
                    
            # corner up-right
            if mat[x - 1][y] in ['#','$','*'] and mat[x][y + 1] in ['#','$','*']:
                if mat[x - 1][y + 1] in ['#','$','*']:
                    return True
                if mat[x - 1][y] == '#' and mat[x][y + 1] =='#':
                    return True
                if mat[x - 1][y] in ['$','*'] and mat[x][y + 1] in ['$','*']:
                    if mat[x - 1][y - 1] == '#' and mat[x + 1][y + 1] == '#':
                        return True
                if mat[x - 1][y] in ['$','*'] and mat[x][y + 1] == '#':
                    if mat[x - 1][y - 1] == '#':
                        return True
                if mat[x - 1][y] == '#' and mat[x][y + 1] in ['$','*']:
                    if mat[x + 1][y + 1] == '#':
                        return True


            #corner down-left
            elif mat[x + 1][y] in ['#','$','*'] and mat[x][y - 1] in ['#','$','*']:
                if mat[x + 1][y - 1] in ['#','$','*']:
                    return True
                if mat[x + 1][y] == '#' and mat[x][y - 1] =='#':
                    return True
                if mat[x + 1][y] in ['$','*'] and mat[x][y - 1] in ['$','*']:
                    if mat[x - 1][y - 1] == '#' and mat[x + 1][y + 1] == '#':
                        return True
                if mat[x + 1][y] in ['$','*'] and mat[x][y - 1] == '#':
                    if mat[x + 1][y + 1] == '#':
                        return True
                if mat[x + 1][y] == '#' and mat[x][y - 1] in ['$','*']:
                    if mat[x - 1][y - 1] == '#':
                        return True
                    

            #corner down-right
            elif mat[x + 1][y] in ['#','$','*'] and mat[x][y + 1] in ['#','$','*']:
                if mat[x + 1][y + 1] in ['#','$','*']:
                    return True
                if mat[x + 1][y] == '#' and mat[x][y + 1] =='#':
                    return True
                if mat[x + 1][y] in ['$','*'] and mat[x][y + 1] in ['$','*']:
                    if mat[x + 1][y - 1] == '#' and mat[x - 1][y + 1] == '#':
                        return True
                if mat[x + 1][y] in ['$','*'] and mat[x][y + 1] == '#':
                    if mat[x + 1][y - 1] == '#':
                        return True
                if mat[x + 1][y] == '#' and mat[x][y + 1] in ['$','*']:
                    if mat[x - 1][y + 1] == '#':
                        return True
                    
        return False

