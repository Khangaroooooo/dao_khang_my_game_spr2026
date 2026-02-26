import pygame as pg

WIDTH = 800
HEIGHT = 600
TITLE = "The Game"
FPS = 60
TILESIZE = 32


#player values
PLAYER_SPEED = 280
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)

#mob values
MOB_SPEED = 120
MOB_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)
#color values

#tuple storying RGB values
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)