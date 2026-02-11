# game engine using template from Chris Bradfield's "Making games with Python & Pygames"

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
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        if hits:
            print(hits)

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
        self.image = pg.Surface((TILESIZE, TILESIZE)) #Settings - TILESIZE
        self.image.fill("BLACK")
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