import pygame as pg                         # imports the pygame library aliased as 'pg'
from pygame.sprite import Sprite            # imports the base Sprite class that all game objects inherit from
import os                                   # imports os for building file paths in a cross-platform way
from settings import *                      # imports all constants (TILESIZE, PLAYER_SPEED, GRAVITY, etc.)
from utils import *                         # imports utility functions and the img_folder path


vec = pg.math.Vector2                       # aliases pygame's 2D vector class for convenient use throughout the file
WALL_IMG = pg.image.load(os.path.join(img_folder, 'WallResized.png'))  # loads the wall tile image once at module level so it's shared by all Wall instances


class Wall(Sprite):
    def __init__(self, game, rect):
        self.groups = game.all_sprites, game.wall_sprites                       # stores the sprite groups this wall belongs to
        Sprite.__init__(self, self.groups)                                      # registers this sprite with both groups via the pygame Sprite initialiser
        self.game = game                                                        # stores a reference to the Game object for later access if needed
        self.rect = rect.copy()                                                 # copies the provided rect so changes to the original don't affect this sprite
        self.image = pg.Surface((rect.width, rect.height))                      # creates a blank surface matching the wall rect's pixel dimensions
        for y in range(0, rect.height, TILESIZE):                               # iterates over the surface vertically in TILESIZE-sized steps
            for x in range(0, rect.width, TILESIZE):                            # iterates over the surface horizontally in TILESIZE-sized steps
                self.image.blit(WALL_IMG, (x, y))                               # tiles the wall image across the surface so large walls are textured uniformly


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)   # returns True if sprite 'one's hit_rect overlaps sprite 'two's rect (used for precise hitbox collision)


def collide_with_walls(sprite, walls, dir):
    if dir == 'x':                                                              # handles horizontal collision resolution
        hits = [w for w in walls if sprite.hit_rect.colliderect(w)]             # finds all wall rects that currently overlap the sprite's hit_rect
        if hits:                                                                # only resolves if at least one collision was detected
            if hits[0].centerx > sprite.hit_rect.centerx:                       # if the wall is to the right of the sprite
                sprite.pos.x = hits[0].left - sprite.hit_rect.width / 2         # pushes the sprite's position to the left edge of the wall
            if hits[0].centerx < sprite.hit_rect.centerx:                       # if the wall is to the left of the sprite
                sprite.pos.x = hits[0].right + sprite.hit_rect.width / 2        # pushes the sprite's position to the right edge of the wall
            sprite.vel.x = 0                                                    # zeroes horizontal velocity to prevent the sprite from moving into the wall
            sprite.hit_rect.centerx = sprite.pos.x                              # syncs the hit_rect's x centre to the corrected position
    if dir == 'y':                                                              # handles vertical collision resolution
        hits = [w for w in walls if sprite.hit_rect.colliderect(w)]             # finds all wall rects overlapping vertically
        if hits:                                                                # only resolves if at least one collision was detected
            if hits[0].centery > sprite.hit_rect.centery:                       # if the wall is below the sprite (floor)
                sprite.pos.y = hits[0].top - sprite.hit_rect.height / 2         # pushes the sprite up to sit on top of the wall
            if hits[0].centery < sprite.hit_rect.centery:                       # if the wall is above the sprite (ceiling)
                sprite.pos.y = hits[0].bottom + sprite.hit_rect.height / 2      # pushes the sprite down below the wall
            sprite.vel.y = 0                                                    # zeroes vertical velocity (stops falling or upward movement on contact)
            sprite.hit_rect.centery = sprite.pos.y                              # syncs the hit_rect's y centre to the corrected position

# created off of chart made by Claude
class StateMachine:
    def __init__(self):
        self.state = None               # holds the current state string; None until start() is called

    def start(self, initial_state):
        self.state = initial_state      # sets the initial state when the state machine is first activated

    def transition(self, new_state):
        if self.state != new_state:     # only transitions if the new state is actually different from the current one
            self.state = new_state      # updates the state to the new value


class Player(Sprite):
    IDLE_COLS, IDLE_ROWS = 2, 4         # the idle spritesheet has 2 columns and 4 rows of 32×32 frames
    WALK_COLS, WALK_ROWS = 4, 5         # the walk spritesheet has 4 columns and 5 rows of 32×32 frames
    ANIM_SPEED_MS        = 240          # milliseconds between each animation frame advance

    def __init__(self, game, x, y):
        self.groups = game.all_sprites              # the player belongs only to the all_sprites group (not wall_sprites)
        Sprite.__init__(self, self.groups)          # registers the player sprite with its group via pygame's Sprite base class
        self.game = game                            # stores a reference to the Game object for accessing walls, dt, etc.

        self.vel = vec(0, 0)                        # initialises the player's velocity vector to zero (no movement at start)
        self.pos = vec(x, y)                        # sets the player's initial pixel position using the provided x, y coordinates

        self.hit_rect = PLAYER_HIT_RECT.copy()      # copies the global 32×32 collision rect so each player has its own independent copy

        self.gamemode = "topdown"                   # default physics mode; overwritten by the room's gamemode when the game starts
        self.grounded = False                       # tracks whether the player is standing on solid ground (only relevant in platformer mode)

        # State machine
        self.state_machine = StateMachine()         # creates the finite state machine that tracks idle vs. moving states
        self.state_machine.start("idle")            # sets the initial animation state to idle

        self.moving = False                         # boolean flag mirroring state_machine.state for quick animation checks

        # Current direction — controls which walk frame set is shown.
        # Change this to "Up", "Down", "Left", or "Right" at any time.
        self.dir = "Down"                           # initial facing direction; determines which walk animation row is played

        # Animation state
        self.last_update   = 0                      # timestamp (ms) of the last animation frame advance
        self.current_frame = 0                      # index of the current frame within the active animation sequence

        # Load frames
        self._load_images()                         # slices all animation frames from the spritesheets and stores them in dicts/lists

        # Set initial image
        self.image = self.idle_frames[0]            # sets the first idle frame as the starting visible image
        self.rect  = self.image.get_rect()          # creates a pygame.Rect matching the image dimensions for rendering
        self.hit_rect.center = self.rect.center     # aligns the collision rect's centre to the visual rect's centre

    def _slice_row(self, sheet, row, cols):
        """Return a list of 32×32 surfaces from a single row of a sheet."""
        frames = []                                             # empty list to collect the sliced frame surfaces
        for col in range(cols):                                 # iterates over each column index in the specified row
            surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)  # creates a transparent 32×32 surface for this frame
            surf.blit(sheet, (0, 0), (col * TILESIZE, row * TILESIZE, TILESIZE, TILESIZE))  # copies the tile region from the sheet onto the surface
            frames.append(surf)                                 # adds the extracted frame surface to the list
        return frames                                           # returns all frames from that row as a list

    def _slice_sheet(self, path, cols, rows):
        """Return a flat list of all 32×32 surfaces from a sheet (row-major)."""
        sheet = pg.image.load(path).convert_alpha()            # loads the spritesheet image with per-pixel alpha support
        frames = []                                            # empty list to collect every frame across all rows
        for row in range(rows):                                # iterates over each row from top to bottom
            for col in range(cols):                            # iterates over each column left to right within the row
                surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)  # creates a transparent 32×32 surface for this cell
                surf.blit(sheet, (0, 0), (col * TILESIZE, row * TILESIZE, TILESIZE, TILESIZE))  # blits the tile region from the sheet
                frames.append(surf)                            # appends the frame to the flat list
        return frames                                          # returns all frames in row-major order

    def _load_images(self):
        idle_path = os.path.join(img_folder, 'Idle.png')       # builds the full file path for the idle spritesheet
        walk_path = os.path.join(img_folder, 'Walk.png')       # builds the full file path for the walk spritesheet

        self.idle_frames = self._slice_sheet(idle_path, self.IDLE_COLS, self.IDLE_ROWS)  # slices all idle frames into a flat list

        walk_sheet = pg.image.load(walk_path).convert_alpha()  # loads the walk spritesheet with alpha support for reuse across multiple rows

        # Each key matches a possible value of self.dir.
        # Rows are sliced in the order they appear in Walk.png top-to-bottom.
        # "Left" reuses "Right" frames flipped horizontally — no separate row needed.
        self.walk_frames = {
            "Down":  self._slice_row(walk_sheet, 0, self.WALK_COLS),  # front-facing walk frames from the first row of the walk sheet
            "Up":    self._slice_row(walk_sheet, 4, self.WALK_COLS),  # back-facing walk frames from the last row of the walk sheet
            "Right": self._slice_row(walk_sheet, 2, self.WALK_COLS),  # right-facing walk frames from the middle row of the walk sheet
            "Left":  [pg.transform.flip(f, True, False)               # left-facing frames are the right-facing frames mirrored horizontally
                      for f in self._slice_row(walk_sheet, 2, self.WALK_COLS)],
        }

    def get_keys(self):
        keys = pg.key.get_pressed()            # reads the current state of every keyboard key as a boolean array

        if self.gamemode == "topdown":         # free 8-direction movement; gravity is disabled
            self.vel = vec(0, 0)               # resets velocity to zero before applying key input each frame
            if keys[pg.K_a]: self.vel.x = -PLAYER_SPEED                 # moves left if A is held
            if keys[pg.K_d]: self.vel.x =  PLAYER_SPEED                 # moves right if D is held
            if keys[pg.K_w]: self.vel.y = -PLAYER_SPEED                 # moves up if W is held (negative y = up in pygame)
            if keys[pg.K_s]: self.vel.y =  PLAYER_SPEED                 # moves down if S is held
            if self.vel.x != 0 and self.vel.y != 0:                     # checks if the player is moving diagonally
                self.vel *= 0.7071                                      # normalises diagonal speed (≈ 1/√2) so it matches straight movement magnitude

        elif self.gamemode == "platformer":    # horizontal movement only; gravity is applied by update()
            self.vel.x = 0                     # resets horizontal velocity before reading input (vertical is preserved for gravity)
            if keys[pg.K_a]: self.vel.x = -PLAYER_SPEED                 # moves left if A is held
            if keys[pg.K_d]: self.vel.x =  PLAYER_SPEED                 # moves right if D is held
            if (keys[pg.K_w] or keys[pg.K_SPACE]) and self.grounded:    # allows jump only if W or Space is held AND the player is on the ground
                self.vel.y = JUMP_SPEED                                 # sets a strong upward velocity to initiate the jump
                self.grounded = False                                   # immediately marks the player as airborne to prevent double-jumping

    def state_check(self):
        # in platformer mode, falling doesn't count as "moving" for animation
        if self.vel.x != 0 or (self.vel.y != 0 and self.gamemode == "topdown"):  # considers the player moving if there's horizontal velocity, or vertical velocity in topdown mode
            self.state_machine.transition("move")  # transitions the state machine to the moving state
            self.moving = True                      # sets the shorthand moving flag for animation checks
            if self.vel.x > 0: self.dir = "Right"  # facing right when moving right
            elif self.vel.x < 0: self.dir = "Left" # facing left when moving left
            elif self.vel.y < 0: self.dir = "Up"   # facing up when moving up (topdown only)
            elif self.vel.y > 0: self.dir = "Down"  # facing down when moving down (topdown only)
        else:
            self.state_machine.transition("idle")  # transitions to idle if there's no relevant movement
            self.moving = False                    # clears the moving flag so the idle animation plays

    def animate(self):
        now = pg.time.get_ticks()                                       # gets the current time in milliseconds since pygame was initialised
        if now - self.last_update < self.ANIM_SPEED_MS:                 # checks whether enough time has passed to advance to the next frame
            return                                                      # exits early if the animation timer hasn't elapsed yet

        self.last_update = now                                          # records this moment as the last frame advance time
        bottom = self.rect.bottom                                       # saves the current bottom y-coordinate before resizing the rect

        if not self.moving:                                    # plays the idle animation when the player is stationary
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)  # advances frame index, wrapping back to 0 at the end
            self.image = self.idle_frames[self.current_frame]  # updates the visible image to the new idle frame
        else:                                                  # plays the directional walk animation when the player is moving
            frames = self.walk_frames[self.dir]                # selects the correct walk frame list for the current facing direction
            self.current_frame = (self.current_frame + 1) % len(frames)  # advances frame index within the walk sequence, wrapping at the end
            self.image = frames[self.current_frame]            # updates the visible image to the new walk frame

        self.rect = self.image.get_rect()                      # recreates the rect to match any size change in the new frame's image
        self.rect.bottom = bottom                             # restores the saved bottom y so the sprite doesn't float up when the rect is recreated


    def update(self):
        self.get_keys()                                 # reads keyboard input and updates the velocity vector accordingly
        self.state_check()                              # determines the current animation state (idle/move) and facing direction
        self.animate()                                  # advances the animation frame if enough time has passed

        if self.gamemode == "platformer":
            self.vel.y += GRAVITY * self.game.dt        # applies gravity by increasing downward velocity proportional to elapsed time

        self.pos.x += self.vel.x * self.game.dt         # moves the logical x position by the horizontal velocity scaled to delta time
        self.hit_rect.centerx = self.pos.x              # syncs the collision rect's x centre to the updated logical x position
        collide_with_walls(self, self.game.walls, 'x')  # resolves any horizontal collisions with wall rects and corrects position

        self.pos.y += self.vel.y * self.game.dt         # moves the logical y position by the vertical velocity scaled to delta time
        self.hit_rect.centery = self.pos.y              # syncs the collision rect's y centre to the updated logical y position
        collide_with_walls(self, self.game.walls, 'y')  # resolves any vertical collisions with wall rects and corrects position

        if self.gamemode == "platformer":
            self.grounded = self.vel.y == 0             # if vertical velocity was zeroed by wall collision, the player is on the ground

        self.rect.center = self.hit_rect.center         # syncs the visual sprite rect's centre to the collision rect's (possibly corrected) centre
        self.pos = vec(self.hit_rect.center)            # re-derives the logical position vector from the final corrected hit_rect centre


# source: https://www.youtube.com/watch?time_continue=93&v=H2r2N7D56Uw&embeds_referring_euri=https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dclass%2BTransitionOverlay%253A%2Bdef%2B__init__(self)%253A%2Bself.active%2B%253D%2BFalse%2Bself.frame%2B%253D%2B0%2Bself.cal&source_ve_path=MjM4NTE
class TransitionOverlay:
    def __init__(self):
        self.active = False       # flag indicating whether a transition is currently playing
        self.frame = 0            # counts how many frames have elapsed since the transition started
        self.callback = None      # optional function to call at the midpoint of the transition (e.g. switching rooms)

    def start(self, callback=None):
        self.active = True        # activates the transition so update() and draw() start processing it
        self.frame = 0            # resets the frame counter to the beginning of the animation
        self.callback = callback  # stores the midpoint callback (room travel function) for later invocation

    def update(self):
        if not self.active:       # exits immediately if no transition is currently running
            return
        self.frame += 1           # advances the transition by one frame each game update
        half = TRANSITION_FRAMES // 2                   # calculates the halfway point (where the screen is fully black)
        if self.frame == half and self.callback:        # checks if the midpoint has been reached and a callback is registered
            self.callback()                             # calls the callback (e.g. _travel) at peak blackness to swap rooms invisibly
        if self.frame >= TRANSITION_FRAMES:             # checks if the full transition animation has completed
            self.active = False                         # deactivates the transition so normal gameplay resumes

    # transition between doors and rooms
    # fades to black then back
    def draw(self, surface):
        if not self.active:       # skips drawing entirely if no transition is active
            return
        half = TRANSITION_FRAMES // 2                                           # midpoint frame index (full opacity)
        if self.frame <= half:                                                  # first half: fading in (transparent → opaque)
            alpha = int(255 * self.frame / half)                                # linearly increases alpha from 0 to 255 as frames progress to the midpoint
        else:                                                                   # second half: fading out (opaque → transparent)
            alpha = int(255 * (TRANSITION_FRAMES - self.frame) / half)          # linearly decreases alpha from 255 back to 0 as frames progress to the end
        veil = pg.Surface((WIDTH, HEIGHT))                                      # creates a full-screen black surface to use as the fade overlay
        veil.fill(BLACK)                                                        # fills the overlay surface with solid black
        veil.set_alpha(max(0, min(255, alpha)))                                 # applies the calculated alpha (clamped to 0–255) to control transparency
        surface.blit(veil, (0, 0))                                              # draws the semi-transparent black veil over the entire game screen