import pygame
import sys
import os
import button
import csv
import json

sys.path.append('src')
from tile_config import tile_db, TileCategory
from tile_loader import TileLoader

pygame.init()

clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode(
    (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)
)
pygame.display.set_caption('Level Editor')

ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
BLUE = (50, 120, 200)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
PINK = (255, 192, 203)

font = pygame.font.SysFont('Futura', 30)
small_font = pygame.font.SysFont('Futura', 16)
category_font = pygame.font.SysFont('Futura', 24, bold=True)

def load_tile_database():
    tile_loader = TileLoader()
    tile_db = tile_loader.load_all_tiles(TILE_SIZE)
    
    img_list = []
    tile_info = {}
    
    sorted_tiles = sorted(tile_db.tiles.items())
    
    for tile_id, tile_type in sorted_tiles:
        if tile_id in tile_db.images:
            img_list.append(tile_db.images[tile_id])
            tile_info[tile_id] = {
                'category': tile_type.category.value,
                'name': tile_type.name,
                'properties': tile_type.properties
            }
    
    return img_list, tile_info

img_list, tile_info = load_tile_database()
TILE_TYPES = len(img_list)

def scale_bg(img):
    ratio = img.get_width() / img.get_height()
    new_height = SCREEN_HEIGHT
    new_width = int(new_height * ratio)
    return pygame.transform.scale(img, (new_width, new_height))

try:
    background_img = scale_bg(
        pygame.image.load(os.path.join('assets', 'editor', 'background_default.png')).convert_alpha()
    )
    BG_WIDTH = background_img.get_width()
except:
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill(GREEN)
    BG_WIDTH = SCREEN_WIDTH

try:
    save_img = pygame.image.load(os.path.join('assets', 'editor', 'save_btn.png')).convert_alpha()
except:
    save_img = pygame.Surface((100, 50))
    save_img.fill((0, 150, 0))
    btn_font = pygame.font.SysFont('Futura', 20, bold=True)
    text = btn_font.render('SAVE', True, WHITE)
    text_rect = text.get_rect(center=(50, 25))
    save_img.blit(text, text_rect)
    pygame.draw.rect(save_img, BLACK, save_img.get_rect(), 2)

try:
    load_img = pygame.image.load(os.path.join('assets', 'editor', 'load_btn.png')).convert_alpha()
except:
    load_img = pygame.Surface((100, 50))
    load_img.fill((150, 0, 0))
    btn_font = pygame.font.SysFont('Futura', 20, bold=True)
    text = btn_font.render('LOAD', True, WHITE)
    text_rect = text.get_rect(center=(50, 25))
    load_img.blit(text, text_rect)
    pygame.draw.rect(load_img, BLACK, load_img.get_rect(), 2)

save_button = button.Button(
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT + LOWER_MARGIN - 50,
    save_img,
    1
)
load_button = button.Button(
    SCREEN_WIDTH // 2 + 200,
    SCREEN_HEIGHT + LOWER_MARGIN - 50,
    load_img,
    1
)

categories = [
    {'name': 'all', 'display': 'ALL', 'color': LIGHT_BLUE},
    {'name': 'solid', 'display': 'SOLID', 'color': GRAY},
    {'name': 'decorative', 'display': 'DECOR', 'color': (0, 150, 0)},
    {'name': 'enemy', 'display': 'ENEMY', 'color': RED},
    {'name': 'gate', 'display': 'GATE', 'color': GOLD},
    {'name': 'collectible', 'display': 'ITEM', 'color': YELLOW},
    {'name': 'checkpoint', 'display': 'CHECK', 'color': BLUE},
    {'name': 'hazard', 'display': 'HAZARD', 'color': ORANGE},
    {'name': 'powerup', 'display': 'POWER', 'color': PURPLE},
    {'name': 'moving_platform', 'display': 'MOVING', 'color': (0, 255, 255)},
]

current_category_index = 0
current_category = categories[current_category_index]['name']

nav_button_width = 40
nav_button_height = 40
nav_button_x = SCREEN_WIDTH + 100
nav_button_y = 40

prev_button_rect = pygame.Rect(nav_button_x - 50, nav_button_y, nav_button_width, nav_button_height)
next_button_rect = pygame.Rect(nav_button_x + 90, nav_button_y, nav_button_width, nav_button_height)

world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

def reset_world_data():
    global world_data
    world_data = []
    for row in range(ROWS):
        r = [-1] * MAX_COLS
        world_data.append(r)

def load_level_file(level_num):
    global world_data
    reset_world_data()
    
    filename = f'data/level{level_num}_data.csv'
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    if tile.strip():
                        val = int(tile)
                        if 0 <= val < TILE_TYPES:
                            if y < ROWS and x < MAX_COLS:
                                world_data[y][x] = val
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        return False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(GREEN)
    if background_img:
        bg_width = background_img.get_width()
        
        bg_scroll = scroll * 0.5
        
        max_level_width = MAX_COLS * TILE_SIZE
        tiles_needed = (max_level_width // bg_width) + 3
        
        start_x = -bg_width + (-bg_scroll % bg_width)
        
        for i in range(tiles_needed):
            x_pos = start_x + (i * bg_width)
            if x_pos < SCREEN_WIDTH + bg_width and x_pos > -bg_width:
                screen.blit(background_img, (x_pos, 0))

def draw_grid():
    for c in range(MAX_COLS + 1):
        pygame.draw.line(
            screen, WHITE,
            (c * TILE_SIZE - scroll, 0),
            (c * TILE_SIZE - scroll, SCREEN_HEIGHT), 1
        )
    for c in range(ROWS + 1):
        pygame.draw.line(
            screen, WHITE,
            (0, c * TILE_SIZE),
            (SCREEN_WIDTH, c * TILE_SIZE), 1
        )

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if 0 <= tile < len(img_list):
                screen.blit(
                    img_list[tile],
                    (x * TILE_SIZE - scroll, y * TILE_SIZE)
                )
                
                info = tile_info.get(tile, {})
                category = info.get('category', 'unknown')
                
                if category == 'enemy':
                    pygame.draw.rect(
                        screen, RED,
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("E", True, RED)
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))
                
                elif category == 'gate':
                    pygame.draw.rect(
                        screen, GOLD,
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("G", True, GOLD)
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))
                
                elif category == 'collectible':
                    pygame.draw.rect(
                        screen, YELLOW,
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("C", True, YELLOW)
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))
                
                elif category == 'checkpoint':
                    pygame.draw.rect(
                        screen, BLUE,
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("P", True, BLUE)
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))
                
                elif category == 'hazard':
                    pygame.draw.rect(
                        screen, ORANGE,
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("H", True, ORANGE)
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))
                
                elif category == 'powerup':
                    pygame.draw.rect(
                        screen, PURPLE,
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("U", True, PURPLE)
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))
                
                elif category == 'moving_platform':
                    pygame.draw.rect(
                        screen, (0, 255, 255),
                        (x * TILE_SIZE - scroll, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
                    )
                    text = small_font.render("M", True, (0, 255, 255))
                    screen.blit(text, (x * TILE_SIZE - scroll + 5, y * TILE_SIZE + 5))

def draw_level_end():
    max_col_with_tiles = 0
    for row in world_data:
        for x, tile in enumerate(row):
            if tile >= 0:
                max_col_with_tiles = max(max_col_with_tiles, x)
    
    level_end_x = (max_col_with_tiles + 1) * TILE_SIZE - scroll
    
    if 0 < level_end_x < SCREEN_WIDTH:
        pygame.draw.line(screen, BLUE, (level_end_x, 0), (level_end_x, SCREEN_HEIGHT), 2)
        text = small_font.render("LEVEL ENDS HERE", True, BLUE)
        text_rect = text.get_rect(center=(level_end_x - 50, 50))
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, BLACK, bg_rect)
        pygame.draw.rect(screen, BLUE, bg_rect, 1)
        screen.blit(text, text_rect)

def create_tile_buttons(category='all'):
    button_list = []
    button_col = 0
    button_row = 0
    
    for i, img in enumerate(img_list):
        info = tile_info.get(i, {})
        tile_category = info.get('category', 'unknown')
        
        if category == 'all' or tile_category == category:
            hover_img = img.copy()
            hover_overlay = pygame.Surface(hover_img.get_size())
            hover_overlay.set_alpha(60)
            hover_overlay.fill((255, 255, 255))
            hover_img.blit(hover_overlay, (0, 0))
            
            tile_button = button.Button(
                SCREEN_WIDTH + (75 * button_col) + 50,
                75 * button_row + 120,
                img,
                1,
                hover_image=hover_img
            )
            button_list.append((i, tile_button))
            button_col += 1
            if button_col == 3:
                button_row += 1
                button_col = 0
    
    return button_list

button_list = create_tile_buttons(current_category)

run = True
while run:
    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()
    draw_level_end()

    draw_text(f'Level: {level}', font, WHITE, 10,
              SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level',
              font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    pygame.draw.rect(
        screen, GREEN,
        (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT)
    )
    
    draw_text('CATEGORY:', small_font, WHITE, SCREEN_WIDTH + 10, 25)
    
    current_cat_data = categories[current_category_index]
    
    category_display_rect = pygame.Rect(SCREEN_WIDTH + 80, 40, 120, 40)
    pygame.draw.rect(screen, current_cat_data['color'], category_display_rect)
    pygame.draw.rect(screen, WHITE, category_display_rect, 3)
    
    text_color = BLACK
    if current_cat_data['name'] == 'enemy':
        text_color = WHITE
    elif current_cat_data['name'] == 'hazard':
        text_color = BLACK
    elif current_cat_data['name'] == 'powerup':
        text_color = WHITE
    cat_text = category_font.render(current_cat_data['display'], True, text_color)
    cat_text_rect = cat_text.get_rect(center=category_display_rect.center)
    screen.blit(cat_text, cat_text_rect)
    
    pygame.draw.rect(screen, DARK_GRAY, prev_button_rect)
    pygame.draw.rect(screen, WHITE, prev_button_rect, 2)
    prev_text = category_font.render('<', True, WHITE)
    prev_text_rect = prev_text.get_rect(center=prev_button_rect.center)
    screen.blit(prev_text, prev_text_rect)
    
    pygame.draw.rect(screen, DARK_GRAY, next_button_rect)
    pygame.draw.rect(screen, WHITE, next_button_rect, 2)
    next_text = category_font.render('>', True, WHITE)
    next_text_rect = next_text.get_rect(center=next_button_rect.center)
    screen.blit(next_text, next_text_rect)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    
    if mouse_clicked:
        if prev_button_rect.collidepoint(mouse_pos):
            current_category_index = (current_category_index - 1) % len(categories)
            current_category = categories[current_category_index]['name']
            button_list = create_tile_buttons(current_category)
            pygame.time.wait(200)
        
        elif next_button_rect.collidepoint(mouse_pos):
            current_category_index = (current_category_index + 1) % len(categories)
            current_category = categories[current_category_index]['name']
            button_list = create_tile_buttons(current_category)
            pygame.time.wait(200)
    
    draw_text('TILE PALETTE', small_font, WHITE, SCREEN_WIDTH + 10, 100)

    for tile_id, btn in button_list:
        if btn.draw(screen):
            current_tile = tile_id

    for tile_id, btn in button_list:
        if tile_id == current_tile:
            pygame.draw.rect(screen, RED, btn.rect, 3)
            break

    if current_tile < len(img_list):
        info = tile_info.get(current_tile, {})
        category = info.get('category', 'unknown')
        name = info.get('name', f'Tile {current_tile}')
        
        tile_info_text = f'Selected: {current_tile} - {name}'
        draw_text(tile_info_text, small_font, WHITE, 
                  SCREEN_WIDTH + 10, SCREEN_HEIGHT - 60)
        draw_text(f'Category: {category}', small_font, YELLOW,
                  SCREEN_WIDTH + 10, SCREEN_HEIGHT - 45)
        
        props = info.get('properties', {})
        y_offset = SCREEN_HEIGHT - 30
        for key, value in props.items():
            prop_text = f'  {key}: {value}'
            draw_text(prop_text, small_font, YELLOW,
                     SCREEN_WIDTH + 10, y_offset)
            y_offset -= 15
    
    draw_text(f'Total Tiles: {TILE_TYPES}', small_font, WHITE,
              SCREEN_WIDTH + 10, SCREEN_HEIGHT - 15)

    if save_button.draw(screen):
        with open(f'data/level{level}_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for row in world_data:
                writer.writerow(row)

    if load_button.draw(screen):
        scroll = 0
        load_level_file(level)

    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    if 0 <= x < MAX_COLS and 0 <= y < ROWS:
        if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
            if pygame.mouse.get_pressed()[0]:
                if world_data[y][x] != current_tile:
                    world_data[y][x] = current_tile
            if pygame.mouse.get_pressed()[2]:
                world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
                load_level_file(level)
                
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
                load_level_file(level)
                
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()