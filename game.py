from board import Board
import algorithms.bfs as bfs
import algorithms.dfs as dfs
import algorithms.ucs as ucs
import algorithms.test as test

class Game:
    def new_board(self, file_name):
        e = []  # empty solution list
        b = Board()
        with open(file_name, 'r') as f: 
            read_data = f.read()
            lines = read_data.split('\n')
            
            weights = list(map(int, lines.pop(0).split()))
            switches = []
            walls = set()
            
            x = 0
            y = 0
            for line in lines:
                for char in line:
                    if char == '#':
                        walls.add((x, y))
                    elif char == '.':
                        switches.append((x, y))
                    elif char == '@':
                        b.set_player(x, y)
                    elif char == '+':
                        b.set_player(x, y)
                        switches.append((x, y))
                    elif char == '$':
                        b.add_stone(x, y)
                    elif char == '*':
                        b.add_stone(x, y)
                        switches.append((x, y))
                    y += 1
                x += 1
                y = 0
                
            Board.configure(weights_list = weights, row_count = len(lines), col_count =  max([len(line) for line in lines]), switches_list = switches, walls_set = walls)                
            return b

    def doSearches(self, board, option):
        if option == 0:
            test.search(board)
        if option == 1:
            bfs.search(board)
        if option == 2:
            dfs.search(board)
        if option == 3:
            ucs.search(board)
        # if option == 4:
        #     ass.search(board)
        if option == 5:  # all get executed
            bfs.search(board)
            # dfs.search(board)
            # ucs.search(board)
            # ass.search(board)
