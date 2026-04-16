import sys                         # imports the sys module (not actively used here but available for exit/error handling)
import pygame as pg                # imports the pygame library and aliases it as 'pg' for convenience
from settings import *             # imports all constants and configuration values (WIDTH, HEIGHT, FPS, etc.)
from sprites import *              # imports all sprite classes (Player, Wall, TransitionOverlay, etc.)
from utils import *                # imports all utility functions (generate_dungeon, build_walls, draw_room, etc.)

vec = pg.math.Vector2              # creates a shorthand alias for pygame's 2D vector class


class Game:
    def __init__(self):
        pg.init()                                                    # initialises all pygame modules (display, sound, input, etc.)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)  # creates a fullscreen window at the monitor's resolution
        pg.display.set_caption(TITLE)                                # sets the window title bar text to the game title from settings
        self.clock = pg.time.Clock()                                 # creates a clock object used to control and measure frame rate
        self.font = pg.font.SysFont(None, 32)                        # loads the default system font at size 32 for UI text rendering
        self.running = True                                          # flag that keeps the outer game loop alive; False exits the program
        self.playing = False                                         # flag that keeps the inner gameplay loop alive; False returns to start screen

    def new(self):
        self.all_sprites = pg.sprite.Group()                         # creates a sprite group that holds every active sprite in the game
        self.wall_sprites = pg.sprite.Group()                        # creates a sprite group specifically for wall sprites (used for drawing)
        self.rooms = generate_dungeon(10)                            # generates a connected dungeon of 10 rooms and stores the room dict
        self.current_id = 0                                          # tracks which room the player is currently in (starts in room 0)
        self._build_walls(self.rooms[0])                             # constructs wall collision rects for the starting room based on its exits

        cx, cy = centre_pos(self.rooms[0])                          # calculates the pixel centre coordinates of the starting room
        self.player = Player(self, cx, cy)                           # spawns the player sprite at the centre of the starting room
        self.player.gamemode = self.rooms[0].gamemode                # assigns the starting room's physics mode (topdown/platformer) to the player

        self.transition = TransitionOverlay()                        # creates the fade-to-black transition overlay object
        self.pending = None                                          # stores the direction the player just exited through (used during transitions)

        self.playing = True                                          # sets the gameplay flag to True so the run loop starts
        self.run()                                                   # begins the main gameplay loop

    def _build_walls(self, room):
        # Clear old wall sprites and create new ones for the current room
        self.wall_sprites.empty()                                    # removes all existing wall sprites from both sprite groups
        rects = build_walls(room)                                    # generates a list of pygame.Rect objects representing wall segments for this room
        self.walls = rects                                           # stores the raw rect list (used for collision detection without sprites)
        for r in rects:                                              # iterates over each wall rect to create a sprite for it
            Wall(self, r)                                            # creates a Wall sprite, which auto-adds itself to all_sprites and wall_sprites

    def run(self):
        while self.playing:                                          # keeps looping as long as the player is in an active game session
            self.dt = self.clock.tick(FPS) / 1000                   # waits to enforce the target FPS and converts elapsed ms to seconds
            self.events()                                            # processes all queued input and window events
            self.update()                                            # updates all game logic and sprite positions
            self.draw()                                              # renders everything to the screen

    def events(self):
        for event in pg.event.get():                                 # iterates over every event pygame has queued since last frame
            if event.type == pg.QUIT:                                # checks if the user closed the window (e.g. clicked the X button)
                self.playing = False                                 # stops the gameplay loop
                self.running = False                                 # stops the outer loop so the program fully exits

    def update(self):
        if self.transition.active:                                   # checks if a room transition fade is currently playing
            self.transition.update()                                 # if so, only advances the transition animation and skips all other updates
            return                                                   # early return prevents player movement during the fade

        self.all_sprites.update()                                    # calls update() on every sprite (player movement, animation, etc.)

        d = touched_exit(self.player.hit_rect, self.rooms[self.current_id])  # checks whether the player's hitbox overlaps a door opening
        if d:                                                        # if a direction string was returned, the player touched an exit
            self.pending = d                                         # stores the exit direction so the callback can use it after the fade
            self.transition.start(callback=lambda: self._travel(self.pending))  # begins the fade and schedules room travel at the halfway point

        # source for transitions
        # https://www.youtube.com/watch?v=m4lOGMMziLE

    def _travel(self, direction):
        next_id = self.rooms[self.current_id].exits[direction]       # looks up which room ID the exit in the given direction leads to
        self.current_id = next_id                                    # updates the current room tracker to the new room
        self._build_walls(self.rooms[next_id])                       # rebuilds wall sprites and rects for the newly entered room
        nx, ny = entry_pos(direction, self.rooms[next_id])           # calculates the spawn position inside the new room (opposite side of entry)
        self.player.pos = vec(nx, ny)                                # moves the player's logical position vector to the entry coordinates
        self.player.hit_rect.center = (nx, ny)                       # syncs the player's collision rect centre to the new position
        self.player.rect.center = (nx, ny)                           # syncs the player's visual sprite rect centre to the new position
        # Switch physics mode to match the new room and reset vertical speed
        self.player.gamemode = self.rooms[next_id].gamemode          # updates the player's physics mode to match the new room (topdown/platformer)
        self.player.vel.y = 0                                        # resets vertical velocity so no carry-over fall speed from previous room
        self.player.grounded = False                                 # resets the grounded flag so the player isn't stuck thinking they're on the floor

    def draw(self):
        self.screen.fill(DARK_GRAY)                                  # clears the entire screen with a dark grey background each frame
        draw_room(self.screen, self.rooms[self.current_id], self.walls, self.font)  # draws the floor tiles, wall rects, door openings, and mode label
        self.wall_sprites.draw(self.screen)                          # draws all wall sprite images on top of the drawn rects
        self.screen.blit(self.player.image, self.player.rect)        # draws the player's current animation frame at its rect position
        self.transition.draw(self.screen)                            # draws the semi-transparent black veil overlay if a transition is active
        pg.display.flip()                                            # swaps the back buffer to the screen, making this frame visible

    # button is just a rect. with a clickable hitbox
    def show_start_screen(self):
        self.screen.fill(BLACK)                                      # fills the screen with solid black for the start screen background
        font_title = pg.font.SysFont(None, 64)                       # creates a larger font (size 64) specifically for the game title text
        title = font_title.render(TITLE, True, WHITE)                # renders the game title string as a white anti-aliased surface
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))  # draws the title centred horizontally, a quarter down the screen

        start_btn_w, start_btn_h = 160, 48                          # defines the pixel width and height of the start button rectangle
        start_btn = pg.Rect(WIDTH // 2 - start_btn_w // 2, HEIGHT // 2 - start_btn_h // 2, start_btn_w, start_btn_h)  # creates the button rect, centred on screen
        pg.draw.rect(self.screen, GRAY, start_btn)                   # draws the button background as a grey filled rectangle
        lbl = self.font.render("Start", True, WHITE)                 # renders the "Start" label text as a white surface
        self.screen.blit(lbl, lbl.get_rect(center=start_btn.center)) # draws the label centred inside the button rectangle
        pg.display.flip()                                            # pushes the start screen to the display

        waiting = True                                               # flag that keeps the start screen event loop running
        while waiting:                                               # loops until the player clicks Start or closes the window
            self.clock.tick(FPS)                                     # limits this loop to FPS ticks per second to avoid busy-waiting
            for event in pg.event.get():                             # processes all pending pygame events
                if event.type == pg.QUIT:                            # checks for window close event
                    self.running = False                             # signals the outer loop to terminate the program
                    waiting = False                                  # breaks out of the start screen loop
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # checks for a left mouse button click
                    if start_btn.collidepoint(event.pos):            # checks if the click coordinates fall inside the start button
                        waiting = False                              # exits the start screen loop to begin a new game


g = Game()                         # creates the single Game instance that owns all game state
while g.running:                   # outer loop: keeps the program alive to support returning to the start screen after a game ends
    g.show_start_screen()          # shows the title / start screen and waits for the player to click Start
    if g.running:                  # only starts a new game if the player didn't quit from the start screen
        g.new()                    # initialises a fresh game session and enters the gameplay loop