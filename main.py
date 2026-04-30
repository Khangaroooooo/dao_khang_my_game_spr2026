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
        self.clock   = pg.time.Clock()
        self.font    = pg.font.SysFont(None, 32)
        self.running = True
        self.playing = False
        self.difficulty = 'easy'   # NEW: stores the player's chosen difficulty; set by Easy/Medium/Hard buttons on the start screen before Game.new() runs

    def new(self):
        self.all_sprites  = pg.sprite.Group()
        self.wall_sprites = pg.sprite.Group()
        # NEW: generate_dungeon now takes a difficulty string and loads a level file from the matching pool instead of randomly generating room connections
        self.rooms      = generate_dungeon(self.difficulty)   # parses a lvlN.txt from the chosen difficulty pool; each non-'.' cell becomes a room
        self.current_id = 0
        self._build_walls(self.rooms[0])
        cx, cy = centre_pos(self.rooms[0])
        self.player = Player(self, cx, cy)
        self.player.gamemode = self.rooms[0].gamemode
        self.transition = TransitionOverlay()
        self.pending    = None
        self.playing    = True
        self.run()

    def _build_walls(self, room):
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

    def _travel(self, direction):
        next_id = self.rooms[self.current_id].exits[direction]
        self.current_id = next_id
        self._build_walls(self.rooms[next_id])
        nx, ny = entry_pos(direction, self.rooms[next_id])
        self.player.pos = vec(nx, ny)
        self.player.hit_rect.center = (nx, ny)
        self.player.rect.center     = (nx, ny)
        self.player.gamemode  = self.rooms[next_id].gamemode
        self.player.vel.y     = 0
        self.player.grounded  = False

    def draw(self):
        self.screen.fill(DARK_GRAY)
        draw_room(self.screen, self.rooms[self.current_id], self.walls, self.font, self.rooms)
        self.wall_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.transition.draw(self.screen)
        pg.display.flip()

    def show_start_screen(self):
        self.screen.fill(BLACK)
        font_title = pg.font.SysFont(None, 64)
        title = font_title.render(TITLE, True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))

        start_btn = pg.Rect(WIDTH//2 - 80, HEIGHT//2 - 24, 160, 48)
        pg.draw.rect(self.screen, GRAY, start_btn)
        self.screen.blit(self.font.render("Start", True, WHITE),
                         self.font.render("Start", True, WHITE).get_rect(center=start_btn.center))

        # NEW: Easy/Medium/Hard buttons placed below Start — clicking one sets self.difficulty and redraws so the highlight updates to show the active choice
        bw, bh, gap = 120, 40, 20                                         # button width, height, and gap between the three difficulty buttons
        total_w     = bw * 3 + gap * 2                                    # total pixel width of all three buttons combined with their gaps
        by          = start_btn.bottom + 30                               # y position of the difficulty buttons, 30px below the bottom of the Start button
        diff_buttons = [                                                   # list of (rect, label, difficulty_key, base_colour) tuples for unified rendering
            (pg.Rect(WIDTH//2 - total_w//2,              by, bw, bh), "Easy",   'easy',   (30,130,30)),   # Easy button: green, leftmost
            (pg.Rect(WIDTH//2 - total_w//2 + bw+gap,    by, bw, bh), "Medium", 'medium', (160,130,20)),  # Medium button: gold, centre
            (pg.Rect(WIDTH//2 - total_w//2 + (bw+gap)*2,by, bw, bh), "Hard",   'hard',   (150,30,30)),   # Hard button: red, rightmost
        ]
        for btn_rect, lbl, diff, colour in diff_buttons:
            # NEW: brighten the selected difficulty button so the player always has clear visual feedback on which difficulty is currently active
            c = tuple(min(255, v+60) for v in colour) if self.difficulty == diff else colour  # brightens colour components by 60 if this button is selected
            pg.draw.rect(self.screen, c, btn_rect)
            pg.draw.rect(self.screen, WHITE, btn_rect, 2)
            surf = self.font.render(lbl, True, WHITE)
            self.screen.blit(surf, surf.get_rect(center=btn_rect.center))

        sel = self.font.render(f"Selected: {self.difficulty.capitalize()}", True, (180,180,180))
        self.screen.blit(sel, (WIDTH//2 - sel.get_width()//2, by + bh + 12))
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
                    for btn_rect, lbl, diff, colour in diff_buttons:
                        if btn_rect.collidepoint(event.pos):
                            self.difficulty = diff   # NEW: updates difficulty to the clicked button's value then redraws so the highlight reflects the new choice
                            self.show_start_screen()
                            return


g = Game()
while g.running:
    g.show_start_screen()
    if g.running:
        g.new()