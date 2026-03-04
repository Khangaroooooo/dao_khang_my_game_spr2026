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
        self.standing_spritesheet = Spritesheet(path.join(self.game.img_dir, "standing.png"))
        self.walking_spritesheet = Spritesheet(path.join(self.game.img_dir, "walking.png"))
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.hit_rect = PLAYER_HIT_RECT
        self.jumping = False
        self.walking = False
        self.last_update = 0
        self.current_frame = 0

    def get_keys(self):
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

        self.walking = self.vel.length() > 0 #set walking to true based on distance

    def load_images(self):
        self.standing_frames = []
        for i in range(4):  # 18 frames total
            frame = self.standing_spritesheet.get_image(i * 32, 0, 32, 32)
            frame.set_colorkey(BLACK)
            self.standing_frames.append(frame)

        self.walking_frames = []
        for j in range(4):  # 4 rows
            for i in range(4):  # 16 frames total
                frame = self.walking_spritesheet.get_image(i * 32, j * 32, 32, 32)
                frame.set_colorkey(BLACK)
                self.walking_frames.append(frame)
        
        #self.standing_frames = [self.spritesheet.get_image(0, 0, TILESIZE, TILESIZE), 
        #                        self.spritesheet.get_image(TILESIZE, 0, TILESIZE, TILESIZE)]
        #for frame in self.standing_frames:
        #    frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            if now - self.last_update > 175:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.walking:
            if now - self.last_update > 175:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
                bottom = self.rect.bottom
                self.image = self.walking_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom


    def update(self):
        print("player updating")
        self.get_keys()
        self.animate()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        self.rect.center = self.hit_rect.center


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
        # Calculate direction vector from mob to player
        direction = self.game.player.pos - self.pos
        # Normalize and scale by mob speed (only if distance > 0)
        if direction.length() > 0:
            #.normalize returns new unit vector, consistent movement
            direction = direction.normalize() * MOB_SPEED
            self.vel = direction

        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = self.pos.x                          ###
        collide_with_walls(self, self.game.all_walls, 'x')          ###
        self.hit_rect.centery = self.pos.y                          ###
        collide_with_walls(self, self.game.all_walls, 'y')          ###

        self.pos = vec(self.hit_rect.center)  # ← Sync pos BACK from hit_rect
        self.rect.center = self.hit_rect.center  # ← Then sync rect

        #hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        #self.rect.center = self.pos

        #if self.rect.colliderect(self.game.player.hit_rect):
        #    self.game.player.kill()


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
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill("BLACK")
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE #32 - Settings - TILESIZE
        self.rect.center = self.pos

    def update(self):
        # Check if player (not mobs) walks through the coin
        if self.rect.colliderect(self.game.player.hit_rect):
            self.kill()