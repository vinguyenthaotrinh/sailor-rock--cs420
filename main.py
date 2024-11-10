import pygame
import sys
import time
import os
from manager.game import Game
import threading

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sailor Rock")

# Colors and fonts
PINK = (238, 196, 255)
WHITE = (255, 255, 255)
WHITE = (255, 255, 255)
TEXTCOLOR = WHITE
BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

# Constants
TILE_SIZE = 50
FPS = 30  # frames per second to update the screen
WINWIDTH = 1200  # width of the program's window, in pixels
WINHEIGHT = 600  # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
FPSCLOCK = pygame.time.Clock()
BUTTON_HEIGHT = 40

# Directions
UP, DOWN, LEFT, RIGHT = 'up', 'down', 'left', 'right'
# Stat value
global stepStat
stepStat = 0
global weightStat
weightStat = 0


def load_and_scale_image(path, width, height):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (width, height))

# Load images for buttons
button_images = {
    'BFS': {
        'unselected': load_and_scale_image('assets/button/BFS_un.png',84 ,28),
        'selected': load_and_scale_image('assets/button/BFS.png',84 ,28)
    },
    'DFS': {
        'unselected': load_and_scale_image('assets/button/DFS_un.png',84 ,28),
        'selected': load_and_scale_image('assets/button/DFS.png',84 ,28)
    },
    'A*': {
        'unselected': load_and_scale_image('assets/button/A_un.png',84 ,28),
        'selected': load_and_scale_image('assets/button/A.png',84 ,28)
    },
    'UCS': {
        'unselected': load_and_scale_image('assets/button/UCS_un.png',84 ,28),
        'selected': load_and_scale_image('assets/button/UCS.png',84 ,28)
    },
    'Run': {
        'unselected': load_and_scale_image('assets/button/Run_un.png',84 ,28),
        'selected': load_and_scale_image('assets/button/Run.png',84 ,28)
    },
    'Reset': {
        'unselected': load_and_scale_image('assets/button/Reset_un.png',84 ,28),
        'selected': load_and_scale_image('assets/button/Reset.png',84 ,28)
    }
}

# Define button rectangles and their initial state
buttons = {
    'BFS': pygame.Rect(10, 10, 80, BUTTON_HEIGHT),
    'DFS': pygame.Rect(100, 10, 80, BUTTON_HEIGHT),
    'A*': pygame.Rect(190, 10, 80, BUTTON_HEIGHT),
    'UCS': pygame.Rect(280, 10, 80, BUTTON_HEIGHT),
    'Run': pygame.Rect(370, 10, 80, BUTTON_HEIGHT),
    'Reset': pygame.Rect(460, 10, 80, BUTTON_HEIGHT),
}

button_states = {name: False for name in buttons}  # False for unselected, True for selected

sprites = {
    UP: [pygame.image.load(f'assets/sailor/up_{i}.png') for i in range(1, 6)],
    DOWN: [pygame.image.load(f'assets/sailor/down_{i}.png') for i in range(1, 6)],
    LEFT: [pygame.image.load(f'assets/sailor/left_{i}.png') for i in range(1, 6)],
    RIGHT: [pygame.image.load(f'assets/sailor/right_{i}.png') for i in range(1, 6)],
}

IMAGESDICT = {
    'switch places': pygame.image.load('assets/board/Selector.png'),
    'wall': pygame.image.load('assets/board/Wood_Block_Tall.png'),
    'rock': pygame.image.load('assets/board/Rock.png'),
    'inside floor': pygame.image.load('assets/board/Grass_Block.png')
}

TILEMAPPING = {
    '.': IMAGESDICT['switch places'],
    '#': IMAGESDICT['wall'],
    ' ': IMAGESDICT['inside floor'],
    '$': IMAGESDICT['rock']#,
}

# Thêm vào các thiết lập cho thanh level bar và các nút level
level_bar_image = load_and_scale_image('assets/level/level_bar.png', 166.5, 30)  # Thanh bar cho level
level_buttons = [
    {'rect': pygame.Rect(1 + i * 11, SCREEN_HEIGHT - 583, 840, 20), 
     'selected': True if i == 0 else False,  # Nút đầu tiên sẽ được chọn
     'visible': True if i == 0 else False}   # Nút đầu tiên sẽ được hiển thị
    for i in range(12)
] 

current_level_index = 0  # Chỉ số level hiện tại


class Player:
    def __init__(self):
        self.image = sprites[DOWN][0]  # Initial image facing down
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.direction = DOWN
        self.frame_index = 0
        self.animation_speed = 13  # Speed of animation
        self.target_pos = self.rect.center  # Position to move towards
        self.is_moving = False

    def move(self, direction):
        if not self.is_moving:  # Only start a new move if not already moving
            self.direction = direction
            self.is_moving = True  # Start movement

            if direction == UP:
                self.rect.y -= TILE_SIZE
            elif direction == DOWN:
                self.rect.y += TILE_SIZE
            elif direction == LEFT:
                self.rect.x -= TILE_SIZE
            elif direction == RIGHT:
                self.rect.x += TILE_SIZE
    def update(self):
        # Update sprite for animation
        self.frame_index += 1
        if self.frame_index >= self.animation_speed * len(sprites[self.direction]):
            self.frame_index = 0
            self.is_moving = False  # Stop moving after completing the frame


        # Set the current image based on the frame index
        self.image = sprites[self.direction][self.frame_index // self.animation_speed]


    def draw(self):
        screen.blit(self.image, self.rect)

# Load loading images
loading_images = [pygame.image.load(f'assets/loading/{i}.png') for i in range(1,9)]

def draw_status(level):
    weightSurf = BASICFONT.render(f'Weight: {weightStat}', True, TEXTCOLOR)
    weightRect = weightSurf.get_rect()
    weightRect.bottomleft = (20, WINHEIGHT - 75)

    stepSurf = BASICFONT.render(f'Step: {stepStat}', True, TEXTCOLOR)
    stepRect = stepSurf.get_rect()
    stepRect.bottomleft = (20, WINHEIGHT - 55)

    levelSurf = BASICFONT.render('Level %s of %s' % (level, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)

    screen.blit(levelSurf, levelRect)
    screen.blit(stepSurf, stepRect)
    screen.blit(weightSurf, weightRect)
    pygame.display.flip()

def show_loading_screen():
    """
    Displays a loading screen animation by cycling through loading_images once,
    then returns.
    """
    loading_images = [load_and_scale_image(f'assets/loading/{i}.png', 1000, 600) for i in range(1, 9)]
    
    for image in loading_images:
        # Display the loading image
        screen.fill((0, 0, 0))  # Fill screen with black
        screen.blit(image, (SCREEN_WIDTH // 2 - 500, SCREEN_HEIGHT // 2 - 300))  # Center the image
        pygame.display.flip()
        
        # Control the animation speed
        time.sleep(0.07)  # Adjust to change the animation speed
        
        # Cap the frame rate
        FPSCLOCK.tick(FPS)
    
    # Optionally, you can add a short pause after the loading screen


def draw_level_bar():
    """Vẽ thanh level và các nút level trên đó."""
    level_bar_x = 800
    level_bar_y = SCREEN_HEIGHT - 590

    # Hiển thị thanh level bar
    screen.blit(level_bar_image, (level_bar_x, level_bar_y))
    
    # Tìm vị trí của nút được chọn (nếu có)
    selected_index = None
    for i, button in enumerate(level_buttons):
        if button['selected']:
            selected_index = i
            break

    # Vẽ các nút
    for i, button in enumerate(level_buttons):
        if button['visible']:
            return
        else:
            image = load_and_scale_image('assets/level/level.png', 10, 15)
            screen.blit(image, button['rect'].topright)
    if not level_bar_image:
        print("Level bar image not loaded.")
         

def draw_buttons():
    """Draws all control buttons at the top of the screen."""
    for name, rect in buttons.items():
        image = button_images[name]['selected'] if button_states[name] else button_images[name]['unselected']
        screen.blit(image, rect.topleft)

def start_screen():
    """Displays the start screen with a start button."""
    start_scr = load_and_scale_image('assets/start_scr.png', SCREEN_WIDTH, SCREEN_HEIGHT)
    start_button_image = load_and_scale_image('assets/button/startbtn.png', 100, 50)
    screen.blit(start_scr, (0, 0))

    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 150, 100, 50)
    screen.blit(start_button_image, start_button_rect.topleft)

    # Event loop for the start screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    return  # Return from start screen to start the game
        pygame.display.update()

def draw_map_items(mapObj, max_width, max_height):
    """Draws the map items"""

    map_width = len(mapObj[0]) * TILE_SIZE
    map_height = len(mapObj) * TILE_SIZE
    
    mapSurf = pygame.Surface((map_width, map_height))
    
    mapSurf.fill(PINK)
    mapSurfRect = mapSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))

    for y, row in enumerate(mapObj):
        for x, tile in enumerate(row):
            grass_block = TILEMAPPING[' ']
            mapSurf.blit(grass_block, (x * TILE_SIZE, y * TILE_SIZE))
            if tile == '.':  # Switch place
                switch_tile = TILEMAPPING['.']
                mapSurf.blit(switch_tile, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '#':  # Wall
                wall_tile = TILEMAPPING['#']
                mapSurf.blit(wall_tile, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '$':  # Rock
                rock_tile = TILEMAPPING['$']
                mapSurf.blit(rock_tile, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '*':  # Rock on a switch
                switch_tile, rock_tile = TILEMAPPING['.'], TILEMAPPING['$']
                mapSurf.blit(switch_tile, (x * TILE_SIZE, y * TILE_SIZE))
                mapSurf.blit(rock_tile, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '+':  # Player on a switch
                switch_tile = TILEMAPPING['.']
                mapSurf.blit(switch_tile, (x * TILE_SIZE, y * TILE_SIZE))
    draw_buttons()

    screen.blit(mapSurf, mapSurfRect)

def draw_game(mapObj, max_width, max_height, player, current_level_index):
    """Draws the entire game screen with map items and player."""
    screen.fill(PINK)
    
    draw_map_items(mapObj, max_width, max_height)
    player.draw()  # Draw player on top of the map
    draw_level_bar() 
    draw_buttons()
    draw_status(current_level_index + 1)

    pygame.display.flip()

def load_path_from_file(filename="manager/gui.txt"):
    with open(filename, "r") as file:
        line = file.readline().strip()
        if line.startswith("Path: "):
            path = line.replace("Path: ", "")
        else:
            path = ""
    return path

def load_map_steps(filename="manager/gui.txt", max_width=None, max_height=None):
    with open(filename, "r") as file:
        lines = file.readlines()

    steps = []
    current_map = []
    reading_map = False

    for line in lines:
        line = line.rstrip('\n')
        if line.startswith("Step"):
            if current_map:
                steps.append(current_map)
                current_map = []
            reading_map = True
        elif reading_map and line.startswith("__________"):
            reading_map = False
        elif reading_map:
            if max_width:
                line = line.ljust(max_width)  # Thêm khoảng trắng để đạt chiều rộng
            current_map.append(line)


    if current_map:
        steps.append(current_map)
    if max_height:
        for map_step in steps:
            while len(map_step) < max_height:
                map_step.append(' ' * max_width)  # Thêm dòng trắng nếu thiếu dòng

    
    return steps

def load_map_from_file(level_index):
    filename = f"levels/input-{(level_index + 1):02}.txt"
    mapObj = []
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            for line in lines[1:]:  # Skip the first line if not part of the map
                mapObj.append(list(line.strip('\n')))
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return mapObj

    # Determine the max width based on the longest line
    max_width = max(len(row) for row in mapObj) if mapObj else 0

    # Pad each row to match max_width, aligning to the left
    for i, row in enumerate(mapObj):
        row_length = len(row)
        if row_length < max_width:
            # Add padding spaces only to the right to reach max_width
            mapObj[i] = row + [' '] * (max_width - row_length)

    return mapObj


def load_all_levels():
    levels = []
    for i in range(13):  # Duyệt qua 10 file từ input-01.txt đến input-10.txt
        levelObj = load_map_from_file(i)
        levels.append({'mapObj': levelObj, 'startState': {'player': (1, 1)}})  # Adjust start position as needed
    return levels

# Khởi tạo các level khi bắt đầu game
levels = load_all_levels()


def runLevel(level_index, player):

    #mapObj = load_map_from_file(level_index)
    print (levels[level_index])
    levelObj = levels[level_index]
    mapObj = levelObj['mapObj']  # Retrieve the map object from the level

    player_start_x, player_start_y = levelObj['startState']['player']
    try:
        player_start_x, player_start_y = next(
            (x, y) for y, row in enumerate(mapObj) for x, tile in enumerate(row) if (tile in ['@', '+'])
        )
    except StopIteration:
        print("Error: No starting position ('@') found in the map for the player.")
        return  # or handle the error as needed, such as loading a default position or ending the level

    max_width = max(len(row) for row in mapObj)
    max_height = len(mapObj)
    map_width = len(mapObj[0]) * TILE_SIZE
    map_height = len(mapObj) * TILE_SIZE
    
    mapSurf = pygame.Surface((map_width, map_height))
    mapSurfRect = mapSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))

   
    # Convert tile coordinates to screen pixels
    player.rect.center = (mapSurfRect.left + (player_start_x * TILE_SIZE)+25, mapSurfRect.top + (player_start_y * TILE_SIZE)+25)
    player.image = sprites[DOWN][0]
    player.frame_index = 0  # Reset animation frame index if needed

    print(f"Player start position in tiles: {player_start_x}, {player_start_y}")
    print(f"Player start position in pixels: {player.rect.topleft}")


    clock = pygame.time.Clock()
    last_move_time = pygame.time.get_ticks()  # Track time for step intervals

    levelSurf = BASICFONT.render('Level %s of %s' % (level_index + 1, 10), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    global stepStat
    global weightStat
    stepStat, weightStat = 0, 0
    draw_game(mapObj, max_width, max_height, player, current_level_index)
    return mapObj, max_width, max_height

def run(levels, level_index):
    if level_index >= len(levels):
        return
    levelObj = levels[level_index]
    path = load_path_from_file()
    map_steps = load_map_steps()  # Load các bước map
    current_step = 0
    mapObj = levelObj['mapObj']

    player_start_x, player_start_y = levelObj['startState']['player']
    try:
        player_start_x, player_start_y = next(
            (x, y) for y, row in enumerate(mapObj) for x, tile in enumerate(row) if (tile in ['@', '+'])
        )
    except StopIteration:
        print("Error: No starting position ('@') found in the map for the player.")
        return  # or handle the error as needed, such as loading a default position or ending the level

    max_width = max(len(row) for row in mapObj)
    max_height = len(mapObj)
    map_width = len(mapObj[0]) * TILE_SIZE
    map_height = len(mapObj) * TILE_SIZE
    
    mapSurf = pygame.Surface((map_width, map_height))
    mapSurfRect = mapSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))

    
    player = Player()
    # Convert tile coordinates to screen pixels
    player.rect.center = (mapSurfRect.left + (player_start_x * TILE_SIZE)+25, mapSurfRect.top + (player_start_y * TILE_SIZE)+25)

    print(f"Player start position in tiles: {player_start_x}, {player_start_y}")
    print(f"Player start position in pixels: {player.rect.topleft}")


    clock = pygame.time.Clock()
    last_move_time = pygame.time.get_ticks()  # Track time for step intervals

    levelSurf = BASICFONT.render('Level %s of %s' % (level_index + 1, 10), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    run_clicked = False  # Track if "Run" has been clicked


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
      
        if (current_step >= len(path)):
            button_states["Run"] = not button_states["Run"]
            return mapObj, player

        # Automatically move the player along the path with a 1-second interval between steps
        if current_step < len(path) and not player.is_moving:
            current_time = pygame.time.get_ticks()
            if (current_time - last_move_time) > 50:  
                direction = path[current_step]
                if direction == 'u':
                    player.move(UP)
                elif direction == 'd':
                    player.move(DOWN)
                elif direction == 'l':
                    player.move(LEFT)
                elif direction == 'r':
                    player.move(RIGHT)

                mapObj = map_steps[current_step]
                print (map_steps[current_step])
                last_move_time = current_time  # Cập nhật thời gian di chuyển
                current_step += 1     
        player.update()  # Update player position for smooth animation
 
        draw_game(mapObj, max_width, max_height, player, current_level_index)  # Draw the updated game state

    button_states["Run"] = not button_states["Run"]
    return mapObj, player

def handle_level_selection(event):
    """Xử lý khi nhấn chọn level."""
    global current_level_index, levels, max_width, max_height
    for i, button in enumerate(level_buttons):
        if button['rect'].collidepoint(event.pos):
            # Đặt trạng thái selected cho nút được nhấn
            for btn in level_buttons:
                btn['selected'] = False
                btn['visible'] = False
            button['selected'] = True
            button['visible'] = True
            current_level_index = i  # Cập nhật level hiện tại
            print(f"Selected Level: {current_level_index + 1}")
            return current_level_index

def setButtonState():
    for name in button_states:
        button_states[name] = False
    
def run_algorithm(b, new_game, value):
    # show_loading_screen()  # Show loading screen
    print("Running algorithm...")
    for i in range(1, 5):
        if i == value:
            global stepStat
            global weightStat
            stepStat, weightStat = new_game.doSearches(b, i, True)
        else:
            new_game.doSearches(b, i, False)
    print("Algorithm finished.")

def main():
    backend_running = False
    new_game = Game()
    b = new_game.new_board("levels/input-01.txt")

    start_screen()  # Display the start screen
    global levels
    levels = load_all_levels()

    player = Player()


    #levels, max_width, max_height = readLevelsFile('levels/input-01.txt')  # Đọc file level và lấy kích thước bản đồ
    current_level_index = 0
    runLevel(current_level_index, player)

    total_levels = 12  # Number of levels
    mapObj = load_map_from_file(current_level_index)
    max_width = max(len(row) for row in mapObj)
    max_height = len(mapObj)

    # Main game loop
    running = True
    update_level_index = 0
    canRun =  False

    #moves = []
    algo = ""

    while running:
        if backend_running:
            if backend_thread.is_alive():
                show_loading_screen()  # Show loading screen
            else:
                backend_running = False
                canRun = True
        else:
            screen.fill(PINK)
            
            draw_buttons()
            draw_game(mapObj, max_width, max_height, player, current_level_index)
            #time.sleep(2)
            draw_level_bar()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons['Run'].collidepoint(event.pos):
                    if (canRun):
                        run_clicked = True  # Start automatic movement after "Run" is clicked
                        button_states['Run'] = not button_states['Run']
                        mapObj, player = run(levels, current_level_index)
                    else:
                        continue


                elif buttons['A*'].collidepoint(event.pos):
                    setButtonState()
                    button_states['A*'] = not button_states['A*']
                    algo = "A*"
                    stepStat, weightStat = 0, 0
                    backend_thread = threading.Thread(target=run_algorithm, args=(b, new_game, 4))
                    backend_thread.start()

                    backend_running = True

                elif buttons['BFS'].collidepoint(event.pos):
                    setButtonState()
                    button_states['BFS'] = not button_states['BFS']
                    algo = "BFS"

                    stepStat, weightStat = 0, 0
                    backend_thread = threading.Thread(target=run_algorithm, args=(b, new_game, 1))
                    backend_thread.start()
                    backend_running = True 

                elif buttons['DFS'].collidepoint(event.pos):
                    setButtonState()
                    button_states['DFS'] = not button_states['DFS']
                    algo = "DFS"

                    stepStat, weightStat = 0, 0
                    backend_thread = threading.Thread(target=run_algorithm, args=(b, new_game, 2))
                    backend_thread.start()
                    backend_running = True 

                elif buttons['UCS'].collidepoint(event.pos):
                    setButtonState()
                    button_states['UCS'] = not button_states['UCS']
                    algo = "UCS"

                    stepStat, weightStat = 0, 0
                    backend_thread = threading.Thread(target=run_algorithm, args=(b, new_game, 3))
                    backend_thread.start()
                    backend_running = True 

                elif buttons['Reset'].collidepoint(event.pos):
                    button_states['Reset'] = not button_states['Reset']
                    draw_buttons()
                    mapObj, max_width, max_height = runLevel(current_level_index, player)

                    level = current_level_index + 1
                    file_name = f'levels/input-{level:02}.txt'
                    b = new_game.new_board(file_name)
                    stepStat, weightStat = 0, 0
                    canRun = False
                    button_states['Reset'] = not button_states['Reset']
                    draw_buttons()
    
                else:
                # can not go any function here
                    for name, rect in buttons.items():
                        if rect.collidepoint(event.pos):  # Kiểm tra va chạm bằng rect
                            button_states[name] = False #['unselect']  # Đổi trạng thái nút

                    for button in level_buttons:
                        rect = button['rect']  # Lấy đối tượng rect từ từ điển
                        if rect.collidepoint(event.pos):
                            current_level_index = handle_level_selection(event)
                            mapObj, max_width, max_height = runLevel(current_level_index, player)
                            # load new map:
                            level = current_level_index + 1
                            file_name = f'levels/input-{level:02}.txt'
                            b = new_game.new_board(file_name)
                            canRun = False
                            setButtonState()
                            break
                    draw_level_bar()

        if not backend_running:
            draw_buttons()
        #pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == "__main__":
    main()



