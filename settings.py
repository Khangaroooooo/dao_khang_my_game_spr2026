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

#color values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
DARK_GRAY = (30, 30, 30)
FLOOR_COLOR = (50, 50, 50)
WALL_COLOR = (20, 20, 20)
PLAYER_COLOR = (220, 220, 220)

#room values
ROOM_COLS = 40
ROOM_ROWS = 20
WALL_TILES = 1
ROOM_PX_W = (ROOM_COLS + WALL_TILES * 2) * TILESIZE
ROOM_PX_H = (ROOM_ROWS + WALL_TILES * 2) * TILESIZE
ROOM_OX = (WIDTH - ROOM_PX_W) // 2
ROOM_OY = (HEIGHT - ROOM_PX_H) // 2

DOOR_TILES = 3

MOVEMENT_MODES = ["Free Movement", "Platformer", "Turn-Based"]

DIRS = ["north", "south", "east", "west"] #for door positions
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}

TRANSITION_FRAMES = 30  # ~0.5s at 60fps