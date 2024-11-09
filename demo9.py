import pygame
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sailor Rock")

# Colors and fonts
PINK = (238, 196, 255)
WHITE = (255, 255, 255)
TEXTCOLOR = WHITE
BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

# Constants
TILE_SIZE = 50
FPS = 30  # frames per second to update the screen
WINWIDTH = 800  # width of the program's window, in pixels
WINHEIGHT = 600  # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
FPSCLOCK = pygame.time.Clock()
BUTTON_HEIGHT = 40

# Directions
UP, DOWN, LEFT, RIGHT = 'up', 'down', 'left', 'right'

def load_and_scale_image(path, width, height):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (width, height))

# Load images for buttons
button_images = {
    'BFS': {
        'unselected': load_and_scale_image('BFS_un.png',84 ,28),
        'selected': load_and_scale_image('BFS.png',84 ,28)
    },
    'DFS': {
        'unselected': load_and_scale_image('DFS_un.png',84 ,28),
        'selected': load_and_scale_image('DFS.png',84 ,28)
    },
    'A*': {
        'unselected': load_and_scale_image('A_un.png',84 ,28),
        'selected': load_and_scale_image('A.png',84 ,28)
    },
    'UCS': {
        'unselected': load_and_scale_image('UCS_un.png',84 ,28),
        'selected': load_and_scale_image('UCS.png',84 ,28)
    },
    'Run': {
        'unselected': load_and_scale_image('Run_un.png',84 ,28),
        'selected': load_and_scale_image('Run.png',84 ,28)
    },
    'Reset': {
        'unselected': load_and_scale_image('Reset_un.png',84 ,28),
        'selected': load_and_scale_image('Reset.png',84 ,28)
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
    UP: [pygame.image.load(f'up_{i}.png') for i in range(1, 6)],
    #DOWN: [pygame.image.load('Rock.png')],
    DOWN: [pygame.image.load(f'down_{i}.png') for i in range(1, 6)],
    LEFT: [pygame.image.load(f'left_{i}.png') for i in range(1, 6)],
    RIGHT: [pygame.image.load(f'right_{i}.png') for i in range(1, 6)],
}

IMAGESDICT = {
    'switch places': pygame.image.load('Selector.png'),
    'wall': pygame.image.load('Wood_Block_Tall.png'),
    'rock': pygame.image.load('Rock.png'),
    'inside floor': pygame.image.load('Grass_Block.png')
}

TILEMAPPING = {
    '.': IMAGESDICT['switch places'],
    '#': IMAGESDICT['wall'],
    ' ': IMAGESDICT['inside floor'],
    '$': IMAGESDICT['rock']#,
    #'*': ('switch places', 'rock'),   
    #'+': ('switch places')
}

# Thêm vào các thiết lập cho thanh level bar và các nút level
level_bar_image = load_and_scale_image('ele_level/level_bar.png', 146.5, 30)  # Thanh bar cho level
level_buttons = [
    {'rect': pygame.Rect(5 + i * 11, SCREEN_HEIGHT - 582, 666.9, 20), 'selected': False} for i in range(9)
] 

current_level_index = 0  # Chỉ số level hiện tại


class Player:
    def __init__(self):
        self.image = sprites[DOWN][0]  # Initial image facing down
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.direction = DOWN
        self.frame_index = 0
        self.animation_speed = 10  # Speed of animation
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


def draw_level_bar():
    """Vẽ thanh level và các nút level trên đó."""
    level_bar_x = level_bar_x = 630
    level_bar_y = SCREEN_HEIGHT - 590

    # Hiển thị thanh level bar
    screen.blit(level_bar_image, (level_bar_x, level_bar_y))
    
    # Hiển thị các nút level
    for i, button in enumerate(level_buttons):
        image = load_and_scale_image('ele_level/level_bar.png', 10, 10) if button['selected'] else load_and_scale_image('ele_level/level.png', 10, 15)
        screen.blit(image, button['rect'].topright)

        if pygame.mouse.get_pressed()[0]:  # Left mouse button is clicked
            if button['rect'].collidepoint(pygame.mouse.get_pos()):
                # Update selected level
                for btn in level_buttons:
                    btn['selected'] = False
                button['selected'] = True
                global current_level_index
                current_level_index = i  # Set the current level index to the selected button
    if not level_bar_image:
        print("Level bar image not loaded.")

         

def draw_buttons():
    """Draws all control buttons at the top of the screen."""
    for name, rect in buttons.items():
        image = button_images[name]['selected'] if button_states[name] else button_images[name]['unselected']
        screen.blit(image, rect.topleft)

def start_screen():
    """Displays the start screen with a start button."""
    start_scr = load_and_scale_image('start_scr.png', SCREEN_WIDTH, SCREEN_HEIGHT)
    start_button_image = load_and_scale_image('startbtn.png', 100, 50)
    screen.blit(start_scr, (0, 0))

    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 150, 100, 50)

    #screen.blit(start_button_image, (start_button_rect.x + 15, start_button_rect.y + 90))
    screen.blit(start_button_image, start_button_rect.topleft)


    #pygame.display.flip()

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
    #mapSurf = pygame.Surface((max_width * TILE_SIZE, max_height * TILE_SIZE))
    #mapSurf.fill(PINK)
    mapSurfRect = mapSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))
    #print(f"Map surface size: {mapSurf.get_width()} x {mapSurf.get_height()}")

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
            #if tile in TILEMAPPING:
            #    tile_image = TILEMAPPING[tile]
            #    mapSurf.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))
    draw_buttons()

    screen.blit(mapSurf, mapSurfRect)

def draw_game(mapObj, max_width, max_height, player):
    """Draws the entire game screen with map items and player."""
    screen.fill(PINK)
    
    draw_map_items(mapObj, max_width, max_height)
    player.draw()  # Draw player on top of the map
    draw_level_bar() 
    draw_buttons()


    pygame.display.flip()

def load_path_from_file(filename="manager/gui.txt"):
    with open(filename, "r") as file:
        line = file.readline().strip()
        if line.startswith("Path: "):
            path = line.replace("Path: ", "")
        else:
            path = ""
    return path

def show_loading_screen():
    """Displays a loading screen with a rotating animation or message."""
    loading_text = BASICFONT.render("Loading...", True, TEXTCOLOR)
    loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    angle = 0
    while not os.path.exists("manager/gui.txt"):
        # Clear the screen
        screen.fill(PINK)
        
        # Rotate the text to simulate a loading animation
        rotated_text = pygame.transform.rotate(loading_text, angle)
        rotated_rect = rotated_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Display rotated loading message
        screen.blit(rotated_text, rotated_rect.topleft)
        pygame.display.flip()
        
        # Rotate slightly for each frame
        angle += 5
        if angle >= 360:
            angle = 0

        # Control the loading animation speed
        FPSCLOCK.tick(15)
        
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


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
    filename = f"levels/input-{(level_index +1):02}.txt"
    mapObj = []
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            for line in lines[1:]:  # Skip the first line if not part of the map
                mapObj.append(list(line.strip()))
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    return mapObj

def load_all_levels():
    levels = []
    for i in range(10):  # Duyệt qua 10 file từ input-01.txt đến input-10.txt
        levelObj = load_map_from_file(i)
        levels.append({'mapObj': levelObj, 'startState': {'player': (1, 1)}})  # Adjust start position as needed
    return levels

# Khởi tạo các level khi bắt đầu game
levels = load_all_levels()


#def runLevel(levels, level_index, max_width, max_height):
def runLevel(levels, level_index, player):
    if level_index >= len(levels):
        return
    levelObj = levels[level_index]
    #mapObj = load_map_from_file(level_index)
    #max_width = max(len(row) for row in mapObj)
    #max_height = len(mapObj)

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

    #mapObj[player_start_x][player_start_y] = ' '  # Clear the starting position on the map
    max_width = max(len(row) for row in mapObj)
    max_height = len(mapObj)
    map_width = len(mapObj[0]) * TILE_SIZE
    map_height = len(mapObj) * TILE_SIZE
    
    mapSurf = pygame.Surface((map_width, map_height))
    mapSurfRect = mapSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))

   
    # Convert tile coordinates to screen pixels
    #player.rect.center = ((player_start_x - 1) * TILE_SIZE, (player_start_y + 1) * TILE_SIZE)
    player.rect.center = (mapSurfRect.left + (player_start_x * TILE_SIZE)+25, mapSurfRect.top + (player_start_y * TILE_SIZE)+25)
    print(f"Player start position in tiles: {player_start_x}, {player_start_y}")
    print(f"Player start position in pixels: {player.rect.topleft}")

    #game_state = {'player': (levelObj['startState']['player'][0], levelObj['startState']['player'][1])}

    clock = pygame.time.Clock()
    last_move_time = pygame.time.get_ticks()  # Track time for step intervals

    levelSurf = BASICFONT.render('Level %s of %s' % (level_index + 1, 10), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    run_clicked = False  # Track if "Run" has been clicked

    #draw_game(game_state, player, mapObj)  # Draw the updated game state
    return max_width, max_height, level_index

def run(levels, level_index):
    if level_index >= len(levels):
        return
    levelObj = levels[level_index]
    #mapObj = load_map_from_file(level_index)
    #max_width = max(len(row) for row in mapObj)
    #max_height = len(mapObj)

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

    #mapObj[player_start_x][player_start_y] = ' '  # Clear the starting position on the map
    max_width = max(len(row) for row in mapObj)
    max_height = len(mapObj)
    map_width = len(mapObj[0]) * TILE_SIZE
    map_height = len(mapObj) * TILE_SIZE
    
    mapSurf = pygame.Surface((map_width, map_height))
    mapSurfRect = mapSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))

    
    player = Player()
    # Convert tile coordinates to screen pixels
    #player.rect.center = ((player_start_x - 1) * TILE_SIZE, (player_start_y + 1) * TILE_SIZE)
    player.rect.center = (mapSurfRect.left + (player_start_x * TILE_SIZE)+25, mapSurfRect.top + (player_start_y * TILE_SIZE)+25)
    print(f"Player start position in tiles: {player_start_x}, {player_start_y}")
    print(f"Player start position in pixels: {player.rect.topleft}")

    #game_state = {'player': (levelObj['startState']['player'][0], levelObj['startState']['player'][1])}

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
            return

        # Automatically move the player along the path with a 1-second interval between steps
        if current_step < len(path) and not player.is_moving:
            current_time = pygame.time.get_ticks()
            if (current_time - last_move_time) > 500:  
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
        #draw_game(levelObj, player, mapObj, max_width, max_height)
        #draw_game(mapObj, max_width, max_height)
        draw_game(mapObj, max_width, max_height, player)  # Draw the updated game state

        #draw_game(game_state, player, mapObj)  # Draw the updated game state
    return max_width, max_height, level_index

def readLevelsFile(filename):
    assert os.path.exists(filename), f'Cannot find the level file: {filename}'
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    mapTextLines = []
    max_width = 0
    max_height = 0
    for line in content:
        line = line.rstrip('\r\n')
        if ';' in line:
            line = line[:line.find(';')]
        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            max_width = max(len(line) for line in mapTextLines)
            max_height = len(mapTextLines)
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (max_width - len(mapTextLines[i]))

            mapObj = [list(row) for row in mapTextLines]
            startx = starty = None
            for y, row in enumerate(mapObj):
                for x, tile in enumerate(row):
                    if tile == '@' or tile =='+':
                        startx, starty = x, y
                        mapObj[x][y] = ' '

            levels.append({'mapObj': mapObj, 'startState': {'player': (startx, starty)}})
            mapTextLines = []

    return levels, max_width, max_height  # Ensure all three values are returned

def handle_level_selection(event):
    """Xử lý khi nhấn chọn level."""
    global current_level_index, levels, max_width, max_height
    for i, button in enumerate(level_buttons):
        if button['rect'].collidepoint(event.pos):
            # Đặt trạng thái selected cho nút được nhấn
            for btn in level_buttons:
                btn['selected'] = False
            button['selected'] = True
            current_level_index = i  # Cập nhật level hiện tại
            print(f"Selected Level: {current_level_index + 1}")
            runLevel(levels, current_level_index)
            return current_level_index


def main():
    start_screen()  # Display the start screen
    show_loading_screen()
    global levels
    levels = load_all_levels()

    player = Player()


    #levels, max_width, max_height = readLevelsFile('levels/input-01.txt')  # Đọc file level và lấy kích thước bản đồ
    current_level_index = 0
    runLevel(levels, current_level_index, player)

    total_levels = 10  # Number of levels
    mapObj = load_map_from_file(current_level_index)
    max_width = max(len(row) for row in mapObj)
    max_height = len(mapObj)



    #runLevel(levels, current_level_index, max_width, max_height)  # Pass max_width and max_height here

    # Initialize the game state
    #game_state = {'player': (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)}

    # Main game loop
    running = True
    update_level_index = 0
    update =  False

    #moves = []
    while running:
        screen.fill(PINK)
   
        draw_buttons()
        if update:
            runLevel(levels, current_level_index)
            update = False

        draw_game(mapObj, max_width, max_height, player)
        time.sleep(2)
        draw_level_bar()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons['Run'].collidepoint(event.pos):
                    run_clicked = True  # Start automatic movement after "Run" is clicked
                    button_states['Run'] = not button_states['Run']
                    run(levels, current_level_index)
    
                for name, rect in buttons.items():
                    if buttons[name].collidepoint(event.pos):
                        button_states[name] = not button_states[name]
                    elif rect.collidepoint(event.pos):
                        current_level_index = handle_level_selection(event)
                        update = True

        for i, button in enumerate(level_buttons):
            pygame.draw.rect(screen, PINK, button['rect'])
            text = BASICFONT.render(f"Level {i + 1}", True, (255, 255, 255))
            screen.blit(text, (button['rect'].x + 5, button['rect'].y + 5))
    
        #while current_level_index < total_levels:
             #runLevel(levels, current_level_index)
             #current_level_index +=1


        
        # After the level completes, move to the next level
        #current_level_index += 1
     
        #player.update()

        #draw_game(game_state, sprites[DOWN][0], levels[0]['mapObj'])       
        draw_level_bar()
        draw_buttons()
        #pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == "__main__":
    main()


