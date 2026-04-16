import pygame as pg                         # imports pygame so display info can be queried at module load time

pg.init()                                  # initialises pygame before querying display properties
_info = pg.display.Info()                  # retrieves the current monitor's display information object
WIDTH = _info.current_w                    # reads the monitor's full pixel width to use as the game window width
HEIGHT = _info.current_h                   # reads the monitor's full pixel height to use as the game window height
TITLE = "Amaze"                            # the string shown in the window title bar and on the start screen
FPS = 60                                   # target frames per second; the clock will try to maintain this rate
TILESIZE = 32                              # the side length in pixels of one grid tile; used for all spatial measurements

#player values
PLAYER_SPEED = 280                         # the player's movement speed in pixels per second in both axes
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)  # the base collision rectangle for the player (32×32 pixels, positioned at origin)

# platformer physics
# JUMP_SPEED is tuned so the player can reach the north door at the top of the room:
# room interior height = ROOM_ROWS * TILESIZE = 640px; h = v²/(2g) => v = sqrt(2*1800*680) ≈ 1564
GRAVITY    = 1800   # px/s²  — downward acceleration applied every frame in platformer mode
JUMP_SPEED = -1600  # px/s   — the upward velocity given to the player when they jump (negative = upward in pygame)

#color values
BLACK        = (0, 0, 0)           # pure black; used for the start screen background and transition fade
WHITE        = (255, 255, 255)     # pure white; used for UI text labels
GRAY         = (80, 80, 80)        # medium grey; used for the start button background
DARK_GRAY    = (30, 30, 30)        # very dark grey; used to clear the screen each frame (outer border fill)
FLOOR_COLOR  = (50, 50, 50)       # dark grey; used to fill floor tiles inside the room interior
WALL_COLOR   = (20, 20, 20)       # near-black; used to draw the solid wall segments of a room
PLAYER_COLOR = (220, 220, 220)   # light grey; reserved as the player's colour (used if no sprite image is loaded)

#room values
WALL_TILES = 1                              # thickness of the border walls in tiles (1 tile = 32 px on each side)
ROOM_COLS_MIN, ROOM_COLS_MAX = 20, 50       # minimum and maximum room width in tiles (randomly chosen per room)
ROOM_ROWS_MIN, ROOM_ROWS_MAX = 10, 25       # minimum and maximum room height in tiles (randomly chosen per room)

DOOR_TILES = 3                              # width of each doorway opening in tiles (3 tiles = 96 px gap in a wall)

GAMEMODES = ["topdown", "platformer"]       # the two available physics modes a room can be assigned

DIRS = ["north", "south", "east", "west"]   # the four cardinal directions used for room exits and movement
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}  # maps each direction to its opposite for reverse-entry lookups

TRANSITION_FRAMES = 30  # total number of frames for a room transition (~0.5 seconds at 60 FPS)