# game engine using template from Chris Bradfield's "Making games with Python & Pygames"
# I can push from vs code...

import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from utils import *

"""VERY IMPORTANT note
#Settings variables, i.e. WIDTH, HEIGHT are not working for me
#Switched out for literal value and added comment to notify
# game class instantiated for running

"""

#                                                       UTILS

#Utils import not working, thus implemented here

class Map:
    def __init__(self, filename):
        #creating data for building the map using list
        self.data = []

        #open a specific file and close it with 'with'
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        return image


#creates countdown timer for a cooldown
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        #allows us to set property for time until cooldown
        self.time = time
        #self.current_time = self.time

    def start(self):
        self.start_time = pg.time.get_ticks()

    def ready(self):
        # sets current time to 
        current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if current_time - self.start_time >= self.time:
            return True
        return False
    
#                                                       SPRITES
    
#sprites import not working, thus implemented here
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
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "spriteSheet.png"))
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

    def load_image(self):
        self.standing_frames = [self.spritesheet.get_image(0, 0, TILESIZE, TILESIZE), 
                                self.spritesheet.get_image(TILESIZE, 0, TILESIZE, TILESIZE)]
        
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)

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

#Main.py code
class Game:
    def __init__(self):
        pg.init()
        # create pg screen w/ tuple with W & H
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) #Settings - WIDTH, HEIGHT
        pg.display.set_caption(TITLE) #Settings - TITLE
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True
        self.game_cooldown = Cooldown(30)
        self.game_cooldown.start()
        # self.load_data()

    #method - function tied to Class

    def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        self.wall_img = pg.image.load(path.join(self.img_dir, 'WallResized.png'))
        self.map = Map(path.join(self.game_dir, 'level1.txt'))
        print('data is loaded')

    def new(self):
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        #self.player = Player(self, 15, 15)
        #self.mob = Mob(self, 0, 0)
        #self.wall = Wall(self, 12, 9)
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile =='1':
                    #call class constructor without assigning variable... when
                    Wall(self, col, row)
                if tile.lower() == 'p':
                    self.player = Player(self, col, row)
                if tile.lower() == 'm':
                    Mob(self, col, row)
                if tile.lower() == 'c':
                    Coin(self, col, row)

        self.run()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000

            self.events()

            self.update()
            self.draw()
            
    def events(self):
        #peripherals - keyboard, mouse, audio, camera, touchscreen, controller
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.MOUSEBUTTONUP:
                pass
                #print("I can get mouse input")
                #print(pg.mouse.get_pos())
            if event.type == pg.KEYUP:
                pass
            if event.type == pg.KEYDOWN:
                pass
            #    if event.key == pg.K_w:
            #        self.player.rect.y -= 5
            #    elif event.key == pg.K_a:
            #        self.player.rect.x -= 5
            #    elif event.key == pg.K_s:
            #        self.player.rect.y += 5
            #    elif event.key == pg.K_d:
            #        self.player.rect.x += 5
            #if event.type == pg.MOUSEBUTTONDOWN:
            #    #mouseX, mouseY = pg.mouse.get_pos()
            #    self.player.rect.x, self.player.rect.y = pg.mouse.get_pos()
                

    def quit(self):
        pass

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLUE)
        #self.draw_text("Hello World", 24, WHITE, WIDTH/2, TILESIZE) #32 - TILESIZE
        #self.draw_text(str(self.dt), 24, WHITE, WIDTH/2, HEIGHT/4) #800/2 - WIDTH/2, 600/4 - HEIGHT/4
        #self.draw_text(str(self.game_cooldown.time), 24, WHITE, WIDTH/2, HEIGHT/3) #800/2 - WIDTH/2, 600/3 - HEIGHT/4
        #self.draw_text(str(self.game_cooldown), WHITE, WIDTH/2)
        self.draw_text(str(self.player.pos), 24, WHITE, WIDTH/2, HEIGHT-HEIGHT/4)
        #self.draw_text(f"Collide: {self.wall.rect.colliderect(self.mob.rect)}", 24, WHITE, WIDTH/2, HEIGHT/3)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

#if __name__ == "__main__":
g = Game()

while g.running:
    g.new()

pg.quit()