import pygame as pg
from pygame.sprite import Sprite
from settings import *

vec = pg.math.Vector2

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill(WHITE) #Settings - WHITE
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel.x = - PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = + PLAYER_SPEED
        if keys[pg.K_w]:
            self.vel.y = - PLAYER_SPEED
        if keys[pg.K_s]:
            self.vel.y = + PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def update(self):
        self.get_keys()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill(RED) #Settings - WHITE
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE

    def update(self):
        # Calculate direction vector from mob to player
        direction = self.game.player.pos - self.pos
        # Normalize and scale by mob speed (only if distance > 0)
        if direction.length() > 0:
            #.normalize returns new unit vector, consistent movement
            direction = direction.normalize() * MOB_SPEED
            self.vel = direction
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

class Wall(Sprite):
    def __init__(self, game, x, y):
        #same init as other sprites
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill("BLACK")
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE

    def update(self):
        self.rect.center = self.pos
        #reset wall's position
        if self.rect.colliderect(self.game.mob.rect):
            #returns True if wall rect detects mob rect in the same position
            print("Collision detected!")
