import pygame as pg
from pygame.sprite import Sprite
import os
from settings import *
from utils import *


vec = pg.math.Vector2
WALL_IMG = pg.image.load(os.path.join(img_folder, 'WallResized.png'))


class Wall(Sprite):
    def __init__(self, game, rect):
        self.groups = game.all_sprites, game.wall_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = rect.copy()
        self.image = pg.Surface((rect.width, rect.height))
        for y in range(0, rect.height, TILESIZE):
            for x in range(0, rect.width, TILESIZE):
                self.image.blit(WALL_IMG, (x, y))


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


def collide_with_walls(sprite, walls, dir):
    if dir == 'x':
        hits = [w for w in walls if sprite.hit_rect.colliderect(w)]
        if hits:
            if hits[0].centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].left - sprite.hit_rect.width / 2
            if hits[0].centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = [w for w in walls if sprite.hit_rect.colliderect(w)]
        if hits:
            if hits[0].centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].top - sprite.hit_rect.height / 2
            if hits[0].centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

# created off of chart made by Claude
class StateMachine:
    def __init__(self):
        self.state = None          # current state string: "idle" or "move"

    def start(self, initial_state):
        self.state = initial_state

    def transition(self, new_state):
        if self.state != new_state:
            self.state = new_state


class Player(Sprite):
    IDLE_COLS, IDLE_ROWS = 2, 4
    WALK_COLS, WALK_ROWS = 4, 5
    ANIM_SPEED_MS        = 120   # milliseconds per frame

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game

        self.vel = vec(0, 0)
        self.pos = vec(x, y)

        self.hit_rect = PLAYER_HIT_RECT.copy()

        # State machine
        self.state_machine = StateMachine()
        self.state_machine.start("idle")
        self.moving = False

        # Current direction — controls which walk frame set is shown.
        # Change this to "Up", "Down", "Left", or "Right" at any time.
        self.dir = "Down"

        # Animation state
        self.last_update   = 0
        self.current_frame = 0

        # Load frames
        self._load_images()

        # Set initial image
        self.image = self.idle_frames[0]
        self.rect  = self.image.get_rect()
        self.hit_rect.center = self.rect.center

    def _slice_row(self, sheet, row, cols):
        """Return a list of 32×32 surfaces from a single row of a sheet."""
        frames = []
        for col in range(cols):
            surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
            surf.blit(sheet, (0, 0), (col * TILESIZE, row * TILESIZE, TILESIZE, TILESIZE))
            frames.append(surf)
        return frames

    def _slice_sheet(self, path, cols, rows):
        """Return a flat list of all 32×32 surfaces from a sheet (row-major)."""
        sheet = pg.image.load(path).convert_alpha()
        frames = []
        for row in range(rows):
            for col in range(cols):
                surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
                surf.blit(sheet, (0, 0), (col * TILESIZE, row * TILESIZE, TILESIZE, TILESIZE))
                frames.append(surf)
        return frames

    def _load_images(self):
        idle_path = os.path.join(img_folder, 'Idle.png')
        walk_path = os.path.join(img_folder, 'Walk.png')

        self.idle_frames = self._slice_sheet(idle_path, self.IDLE_COLS, self.IDLE_ROWS)

        walk_sheet = pg.image.load(walk_path).convert_alpha()

        # Each key matches a possible value of self.dir.
        # Rows are sliced in the order they appear in Walk.png top-to-bottom.
        # "Left" reuses "Right" frames flipped horizontally — no separate row needed.
        self.walk_frames = {
            "Down":  self._slice_row(walk_sheet, 0, self.WALK_COLS),  # front (first row)
            "Up":    self._slice_row(walk_sheet, 4, self.WALK_COLS),  # back (last row)
            "Right": self._slice_row(walk_sheet, 2, self.WALK_COLS),
            "Left":  [pg.transform.flip(f, True, False)
                      for f in self._slice_row(walk_sheet, 2, self.WALK_COLS)],
        }

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]: self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]: self.vel.x =  PLAYER_SPEED
        if keys[pg.K_w]: self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]: self.vel.y =  PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def state_check(self):
        if self.vel != vec(0, 0):
            self.state_machine.transition("move")
            self.moving = True
            # Update self.dir — horizontal takes priority on diagonals
            if self.vel.x > 0:
                self.dir = "Right"
            elif self.vel.x < 0:
                self.dir = "Left"
            elif self.vel.y < 0:
                self.dir = "Up"
            elif self.vel.y > 0:
                self.dir = "Down"
        else:
            self.state_machine.transition("idle")
            self.moving = False

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update < self.ANIM_SPEED_MS:
            return

        self.last_update = now
        bottom = self.rect.bottom

        if not self.moving:
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.current_frame]
        else:
            frames = self.walk_frames[self.dir]
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]

        self.rect = self.image.get_rect()
        self.rect.bottom = bottom


    def update(self):
        self.get_keys()
        self.state_check()
        self.animate()

        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        self.pos = vec(self.hit_rect.center)


# source: https://www.youtube.com/watch?time_continue=93&v=H2r2N7D56Uw&embeds_referring_euri=https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dclass%2BTransitionOverlay%253A%2Bdef%2B__init__(self)%253A%2Bself.active%2B%253D%2BFalse%2Bself.frame%2B%253D%2B0%2Bself.cal&source_ve_path=MjM4NTE
class TransitionOverlay:
    def __init__(self):
        self.active = False
        self.frame = 0
        self.callback = None

    def start(self, callback=None):
        self.active = True
        self.frame = 0
        self.callback = callback

    def update(self):
        if not self.active:
            return
        self.frame += 1
        half = TRANSITION_FRAMES // 2
        if self.frame == half and self.callback:
            self.callback()
        if self.frame >= TRANSITION_FRAMES:
            self.active = False

    # transition between doors and rooms
    # fades to black then back
    def draw(self, surface):
        if not self.active:
            return
        half = TRANSITION_FRAMES // 2
        if self.frame <= half:
            alpha = int(255 * self.frame / half)
        else:
            alpha = int(255 * (TRANSITION_FRAMES - self.frame) / half)
        veil = pg.Surface((WIDTH, HEIGHT))
        veil.fill(BLACK)
        veil.set_alpha(max(0, min(255, alpha)))
        surface.blit(veil, (0, 0))