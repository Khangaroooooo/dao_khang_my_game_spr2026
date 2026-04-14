import sys
import pygame as pg
from settings import *
from sprites import *
from utils import *

vec = pg.math.Vector2


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 32)
        self.running = True
        self.playing = False

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.wall_sprites = pg.sprite.Group()
        self.rooms = generate_dungeon(10) # amt of rooms; maybe change it to random based on a set difficulty?
        self.current_id = 0
        self._build_walls(self.rooms[0]) # builds it depending on the amt of exits in room i

        cx, cy = centre_pos(self.rooms[0]) # uses method created in utils
        self.player = Player(self, cx, cy) # creates a player at cx, cy
        self.player.gamemode = self.rooms[0].gamemode  # set physics for the starting room

        self.transition = TransitionOverlay()
        self.pending = None

        self.playing = True
        self.run()

    def _build_walls(self, room):
        # Clear old wall sprites and create new ones for the current room
        self.wall_sprites.empty()
        rects = build_walls(room)
        self.walls = rects
        for r in rects:
            Wall(self, r)

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        if self.transition.active:
            self.transition.update()
            return

        self.all_sprites.update()

        d = touched_exit(self.player.hit_rect, self.rooms[self.current_id])
        if d:
            self.pending = d
            self.transition.start(callback=lambda: self._travel(self.pending))

        # source for transitions
        # https://www.youtube.com/watch?v=m4lOGMMziLE

    def _travel(self, direction):
        next_id = self.rooms[self.current_id].exits[direction]
        self.current_id = next_id
        self._build_walls(self.rooms[next_id])
        nx, ny = entry_pos(direction, self.rooms[next_id])
        self.player.pos = vec(nx, ny)
        self.player.hit_rect.center = (nx, ny)
        self.player.rect.center = (nx, ny)
        # Switch physics mode to match the new room and reset vertical speed
        self.player.gamemode = self.rooms[next_id].gamemode
        self.player.vel.y = 0
        self.player.grounded = False

    def draw(self):
        self.screen.fill(DARK_GRAY)
        draw_room(self.screen, self.rooms[self.current_id], self.walls, self.font)
        self.wall_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.transition.draw(self.screen)
        pg.display.flip()

    # button is just a rect. with a clickable hitbox
    def show_start_screen(self):
        self.screen.fill(BLACK)
        font_title = pg.font.SysFont(None, 64)
        title = font_title.render(TITLE, True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        start_btn_w, start_btn_h = 160, 48
        start_btn = pg.Rect(WIDTH // 2 - start_btn_w // 2, HEIGHT // 2 - start_btn_h // 2, start_btn_w, start_btn_h)
        pg.draw.rect(self.screen, GRAY, start_btn) 
        lbl = self.font.render("Start", True, WHITE)
        self.screen.blit(lbl, lbl.get_rect(center=start_btn.center))
        pg.display.flip()

        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if start_btn.collidepoint(event.pos):
                        waiting = False


g = Game()
while g.running:
    g.show_start_screen()
    if g.running:
        g.new()