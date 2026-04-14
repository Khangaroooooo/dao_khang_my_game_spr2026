import pygame as pg

pg.init()
_info = pg.display.Info()
WIDTH = _info.current_w
HEIGHT = _info.current_h
TITLE = "Amaze"
FPS = 60
TILESIZE = 32

#player values
PLAYER_SPEED = 280
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)

# platformer physics
# JUMP_SPEED is tuned so the player can reach the north door at the top of the room:
# room interior height = ROOM_ROWS * TILESIZE = 640px; h = v²/(2g) => v = sqrt(2*1800*680) ≈ 1564
GRAVITY    = 1800   # px/s²  — downward acceleration
JUMP_SPEED = -1600  # px/s   — initial upward velocity on jump

#color values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
DARK_GRAY = (30, 30, 30)
FLOOR_COLOR = (50, 50, 50)
WALL_COLOR = (20, 20, 20)
PLAYER_COLOR = (220, 220, 220)

#room values
WALL_TILES = 1
ROOM_COLS_MIN, ROOM_COLS_MAX = 20, 50 # range for random room width in tiles
ROOM_ROWS_MIN, ROOM_ROWS_MAX = 10, 25 # range for random room height in tiles

DOOR_TILES = 3

GAMEMODES = ["topdown", "platformer"]

DIRS = ["north", "south", "east", "west"] #for door positions
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}

TRANSITION_FRAMES = 30  # ~0.5s at 60fps