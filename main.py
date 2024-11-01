import os
from game import Game

'''
Tests search algos
Handles command line and user input
'''


def runSearch(s, filename, option):
    ''' Runs the search based on filename and option selected '''
    b = s.new_board(filename)
    print('\nSolving ' + filename + '...')
    s.doSearches(b, option)

new_game = Game()

print("Which algorithm?")
print("0) Test")
print("1) Breadth first search")
print("2) Depth first search")
print("3) Uniform cost search")
# print("4) A* search")
# print("5) all")
p = input("Type a number and press enter: ")
option = int(p)

# gets file from args and plays that puzzle

for i in range(2, 3):  # Chạy từ 1 đến 10
    file_name = f'levels/input-{i:02}.txt'  # Định dạng tên file, đảm bảo có hai chữ số
    runSearch(new_game, file_name, option)

# Lấy danh sách tất cả các tệp trong thư mục 'puzzles'
# puzzles_folder = 'testcase'
# file_names = [f for f in os.listdir(puzzles_folder) if os.path.isfile(os.path.join(puzzles_folder, f))]

# # Chạy hàm runSearch cho mỗi tệp
# for file_name in file_names:
#     runSearch(new_game, os.path.join(puzzles_folder, file_name), option)
