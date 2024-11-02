# game.py
from manager.board import Board
from algorithms.bfs import search as bfs
from algorithms.dfs import search as dfs
from algorithms.ucs import search as ucs
from algorithms.test import search as test

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
            # make file input...txt -> output...txt
            file_name = "levels/output" + file_name[-7:]
            Board.configure(output_name = file_name, weights_list = weights, row_count = len(lines), col_count =  max([len(line) for line in lines]), switches_list = switches, walls_set = walls)                
            return b

    def doSearches(self, board, option):
        if option == 0:
            test(board)
        if option == 1:
            bfs(board)
        if option == 2:
            dfs(board)
        if option == 3:
            ucs(board)

    def run(self):
        print("Which algorithm?")
        print("0) Test")
        print("1) Breadth first search")
        print("2) Depth first search")
        print("3) Uniform cost search")
        # print("4) A* search")
        option = int(input("Type a number and press enter: "))
        level = int(input("Choose a level (from 1 to 10): "))
        
        file_name = f'levels/input-{level:02}.txt'  # Format level file
        b = self.new_board(file_name)
        print('\nSolving ' + file_name + '...')
        self.doSearches(b, option)
    
