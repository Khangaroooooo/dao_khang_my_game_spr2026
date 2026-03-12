import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import *

vec = pg.math.Vector2


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


class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.hit_rect = PLAYER_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]: self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]: self.vel.x = PLAYER_SPEED
        if keys[pg.K_w]: self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]: self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def update(self):
        self.get_keys()
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