import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import *
from os import path

vec = pg.math.Vector2

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

#checks for xy collision in sequence and sets the position based on collision detection

def collide_with_walls(sprite, group, dir):
    #check plane
    if dir == 'x':
        #set hits to Bool based on collide on x axis
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            print("collided with wall from x dir")
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    #check plane
    if dir == 'y':
        #set hits to Bool based on collide on x axis
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            print("collided with wall from y dir")
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.img_dir, "spriteSheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill(WHITE) #Settings - WHITE
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE
        self.hit_rect = PLAYER_HIT_RECT

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
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')

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
        self.hit_rect = MOB_HIT_RECT ###

    def update(self):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        self.hit_rect.centerx = self.pos.x                          ###
        collide_with_walls(self, self.game.all_walls, 'x')          ###
        self.hit_rect.centery = self.pos.y                          ###
        collide_with_walls(self, self.game.all_walls, 'y')          ###

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
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        #self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        #self.image.fill("BLACK")
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE
        self.rect.center = self.pos

    def update(self):
        pass
        #reset wall's position
        #if self.rect.colliderect(self.game.mob.rect):
            #returns True if wall rect detects mob rect in the same position
            #print("Collision detected!" + str(self.pos))



class Coin(Sprite):
    def __init__(self, game, x, y):
        #same init as other sprites
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill("BLACK")
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE
        self.rect.center = self.pos

    def update(self):
        pass