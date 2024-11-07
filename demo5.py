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
    '$': IMAGESDICT['rock']
}

class Player:
    def __init__(self):
        self.image = sprites[DOWN][0]  # Initial image facing down
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.direction = DOWN
        self.frame_index = 0
        self.animation_speed = 10  # Speed of animation
        self.target_pos = self.rect.topleft  # Position to move towards
        self.is_moving = False

    def move(self, direction):
        if not self.is_moving:  # Only start a new move if not already moving
            self.direction = direction
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

        # Set the current image based on the frame index
        self.image = sprites[self.direction][self.frame_index // self.animation_speed]


    def draw(self):
        screen.blit(self.image, self.rect)


def draw_buttons():
    """Draws all control buttons at the top of the screen."""
    for name, rect in buttons.items():
        #pygame.draw.rect(screen, WHITE, rect, border_radius=5)
        #label = button_font.render(name, True, PINK)
        #screen.blit(label, (rect.x + 15, rect.y + 10))
        image = button_images[name]['selected'] if button_states[name] else button_images[name]['unselected']
        screen.blit(image, rect.topleft)

def start_screen():
    """Displays the start screen with a start button."""
    #screen.fill(PINK)
    #title = BASICFONT.render("Ares's Adventure", True, TEXTCOLOR)
    #title_rect = title.get_rect(center=(HALF_WINWIDTH, SCREEN_HEIGHT // 2 - 100))
    start_scr = load_and_scale_image('start_scr.png', SCREEN_WIDTH, SCREEN_HEIGHT)
    start_button_image = load_and_scale_image('startbtn.png', 100, 50)
    screen.blit(start_scr, (0, 0))


    #screen.blit(title, title_rect)

    # Team Information
    #intro_text = [
    #    'Course: CS420 – Artificial Intelligence',
    #    'Class 22TT – Term I/2024-2025',
    #    'Group 01',
    #    'Trịnh Nguyễn Thảo Vi - 22125120',
    #    'Nguyễn Kim Khanh - 22125036',
    #    'Đỗ Huỳnh Diễm Uyên - 22125117'
    #]
    #y = SCREEN_HEIGHT // 2 - 50
    #for line in intro_text:
    #    text_surf = BASICFONT.render(line, True, TEXTCOLOR)
    #    text_rect = text_surf.get_rect(center=(HALF_WINWIDTH, y))
    #    screen.blit(text_surf, text_rect)
    #    y += 20

    # Start button setup
    #start_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50, 100, 50)
    #pygame.draw.rect(screen, WHITE, start_button, border_radius=5)
    #start_text = BASICFONT.render("Start", True, PINK)
    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50, 100, 50)

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
                    print("Start button clicked!")  # Debug line

                    return  # Return from start screen to start the game
        pygame.display.update()

def draw_map_items(mapObj):
    """Draws the map items"""
    #mapSurf = pygame.Surface((len(mapObj[0]) * TILE_SIZE, len(mapObj) * TILE_SIZE))
    map_width = len(mapObj[0]) * TILE_SIZE
    map_height = len(mapObj) * TILE_SIZE
    mapSurf = pygame.Surface((map_width, map_height))
    
    mapSurf.fill(PINK)
    mapSurfRect = mapSurf.get_rect()
    mapSurfRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
    print(f"MapObj size: {len(mapObj[0])} x {len(mapObj)}")
    print(f"Map surface size: {mapSurf.get_width()} x {mapSurf.get_height()}")


    for y, row in enumerate(mapObj):
        for x, tile in enumerate(row):
            grass_block = TILEMAPPING[' ']
            mapSurf.blit(grass_block, (x * TILE_SIZE, y * TILE_SIZE))
            if tile in TILEMAPPING:
                tile_image = TILEMAPPING[tile]
                mapSurf.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))

    #mapSurfRect = mapSurf.get_rect()
    #mapSurfRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
    print

    screen.blit(mapSurf, mapSurfRect)

def draw_game(game_state, player, mapObj):
    """Draws the entire game screen with map items and player."""
    screen.fill(PINK)
    draw_buttons()
    draw_map_items(mapObj)
    player.draw()  # Draw player on top of the map

    pygame.display.flip()

def load_path_from_file(filename="outputgui.txt"):
    with open(filename, "r") as file:
        line = file.readline().strip()
        if line.startswith("Path: "):
            path = line.replace("Path: ", "")
        else:
            path = ""
    return path

def load_map_steps(filename="outputgui.txt"):
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
            current_map.append(line)

    if current_map:
        steps.append(current_map)
    
    return steps


def runLevel(levels, level_index):
    if level_index >= len(levels):
        return
    levelObj = levels[level_index]

    player_start_x, player_start_y = levelObj['startState']['player']
    player = Player()
    # Convert tile coordinates to screen pixels
    player.rect.center = ((player_start_x-1) * TILE_SIZE, (player_start_y+1) * TILE_SIZE)
    print(f"Player start position in tiles: {player_start_x}, {player_start_y}")
    print(f"Player start position in pixels: {player.rect.topleft}")



    path = load_path_from_file()
    map_steps = load_map_steps()  # Load các bước map

    current_step = 0

    #game_state = {'player': (levelObj['startState']['player'][0], levelObj['startState']['player'][1])}
    mapObj = levelObj['mapObj']

    clock = pygame.time.Clock()
    last_move_time = pygame.time.get_ticks()  # Track time for step intervals

    levelSurf = BASICFONT.render('Level %s of %s' % (level_index + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)

    run_clicked = False  # Track if "Run" has been clicked


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons['Run'].collidepoint(event.pos):
                    run_clicked = True  # Start automatic movement after "Run" is clicked
                    button_states['Run'] = not button_states['Run']


        # Automatically move the player along the path with a 1-second interval between steps
        if run_clicked and current_step < len(path) and not player.is_moving:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > 500:  
                direction = path[current_step]
                if direction == 'u':
                    player.move(UP)
                elif direction == 'd':
                    player.move(DOWN)
                elif direction == 'l':
                    player.move(LEFT)
                elif direction == 'r':
                    player.move(RIGHT)

                mapObj = map_steps[current_step]  # Lấy map của bước hiện tại
                last_move_time = current_time  # Cập nhật thời gian di chuyển
                current_step += 1        
        player.update()  # Update player position for smooth animation
        draw_game(levelObj, player, mapObj)  # Draw the updated game state

        #draw_game(game_state, player, mapObj)  # Draw the updated game state
        clock.tick(FPS)

def readLevelsFile(filename):
    assert os.path.exists(filename), f'Cannot find the level file: {filename}'
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = []
    mapTextLines = []
    for line in content:
        line = line.rstrip('\r\n')
        if ';' in line:
            line = line[:line.find(';')]
        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            maxWidth = max(len(line) for line in mapTextLines)
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            mapObj = [list(row) for row in mapTextLines]
            startx = starty = None
            for y, row in enumerate(mapObj):
                for x, tile in enumerate(row):
                    if tile == '@':
                        startx, starty = x, y
                        mapObj[y][x] = ' '

            levels.append({'mapObj': mapObj, 'startState': {'player': (startx, starty)}})
            mapTextLines = []

    return levels

def main():
    start_screen()  # Display the start screen
    levels = readLevelsFile('levels.txt')  # Đọc file level
    current_level_index = 0

    runLevel(levels, current_level_index)  # Chạy level đầu tiên

    # Initialize the game state
    game_state = {'player': (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)}

    # Main game loop
    running = True
    #moves = []
    while running:
        screen.fill(PINK)

        draw_buttons()
        draw_game(game_state, sprites[DOWN][0], levels[0]['mapObj'])  # Pass level map

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        # Toggle button state on click
                        button_states[name] = not button_states[name]
        
            #elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check which button is clicked
                #for name, rect in buttons.items():
                    #if rect.collidepoint(event.pos):
                        #if name == 'Run':
                            #moves = load_moves_from_file("outputgui.txt")
                            #run_moves(game_state, moves)
                        #elif name == 'Reset':
                            #game_state = {'player': (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)}
                        # Additional buttons (BFS, DFS, A*, UCS) can be handled here

        pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == "__main__":
    main()

