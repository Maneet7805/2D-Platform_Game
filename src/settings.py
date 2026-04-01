import pygame
import os
import pathlib

# Get the absolute path to the directory containing src/
ROOT_DIR = pathlib.Path(__file__).parent.parent

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

FPS = 60
ROWS = 16
TILE_SIZE = SCREEN_HEIGHT // ROWS
MAX_COLS = 150
GRAVITY = 0.8
JUMP_STRENGTH = 15
PLAYER_SPEED = 3
MAX_FALL_SPEED = 15

GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
BLUE = (50, 120, 200)
YELLOW = (255, 255, 0)
PURPLE = (138, 43, 226)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
LIGHT_GREEN = (144, 238, 144)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GOLD = (255, 215, 0)

SOLID_TILES = list(range(12))
ENEMY_TILES = [18]
GATE_TILES = [17]

LEVEL_FILES = ['data/level0_data.csv', 'data/level1_data.csv']

def scale_bg(img):
    ratio = img.get_width() / img.get_height()
    new_height = SCREEN_HEIGHT
    new_width = int(new_height * ratio)
    return pygame.transform.scale(img, (new_width, new_height))
