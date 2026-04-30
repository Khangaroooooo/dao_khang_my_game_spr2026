import pygame as pg          # imports pygame for Rect creation and vector math
import random                # imports the random module used for gamemode assignment per room
import os                    # imports os for cross-platform file path construction
from settings import *       # imports all constants (TILESIZE, WALL_TILES, ROOM_COLS_MIN, GAMEMODES, etc.)

vec = pg.math.Vector2        # aliases pygame's 2D vector class for position/velocity calculations

img_folder    = os.path.join(os.path.dirname(__file__), 'images')  # absolute path to the images/ subfolder next to this script
levels_folder = os.path.join(os.path.dirname(__file__), 'levels')  # absolute path to the levels/ folder containing all lvl1.txt through lvl50.txt maze files

# NEW: difficulty pools built by concatenating "lvl" + number + ".txt" — easy=1-20, medium=21-40, hard=41-50 — one file is picked per game session
easy_diff   = ["lvl" + str(i) + ".txt" for i in range(1,  21)]   # filenames lvl1.txt..lvl20.txt for the easy difficulty pool selected on the start screen
medium_diff = ["lvl" + str(i) + ".txt" for i in range(21, 41)]   # filenames lvl21.txt..lvl40.txt for the medium difficulty pool selected on the start screen
hard_diff   = ["lvl" + str(i) + ".txt" for i in range(41, 51)]   # filenames lvl41.txt..lvl50.txt for the hard difficulty pool selected on the start screen


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width, height))
        return image


class Room:
    def __init__(self, room_id):
        self.id       = room_id
        self.exits    = {}
        self.grid_pos = (0, 0)
        self.gamemode = "topdown"
        self.cols     = ROOM_COLS_MIN
        self.rows     = ROOM_ROWS_MIN
        self.is_start  = False   # NEW: True if this room is the 's' cell in the level file — used to identify where the player spawns at game start
        self.is_finish = False   # NEW: True if this room is the 'f' cell in the level file — used to highlight the goal room for the player


# NEW: generate_dungeon is fully replaced by load_dungeon_from_file which parses a lvlN.txt where each '0'/'s'/'f' cell IS a room and '.' cells are empty space
def generate_dungeon(difficulty='easy'):
    """Pick a random level file from the difficulty pool, parse its grid where each non-'.' cell is a room, wire exits between adjacent rooms, return rooms dict."""
    # NEW: select and randomly pick one level file from the correct difficulty pool based on the string passed from the start screen button click
    if difficulty == 'easy':
        filename = random.choice(easy_diff)     # randomly picks one of lvl1-20 for the easy pool so each playthrough uses a different easy maze layout
    elif difficulty == 'medium':
        filename = random.choice(medium_diff)   # randomly picks one of lvl21-40 for the medium pool for varied medium-difficulty maze layouts each run
    else:
        filename = random.choice(hard_diff)     # randomly picks one of lvl41-50 for the hard pool for varied hard-difficulty maze layouts each run

    path = os.path.join(levels_folder, filename)            # builds the absolute file path from the levels folder and chosen filename
    with open(path, 'r') as f:                              # opens the chosen level text file for reading
        lines = [ln.rstrip('\n') for ln in f.readlines()]   # reads all lines stripping newlines to get clean row strings for grid parsing

    # NEW: first pass — scan the grid to find every non-'.' cell and assign it a room ID; build a (col,row)->room_id lookup for exit wiring in the second pass
    cell_to_id = {}   # NEW: maps (col, row) grid coordinates to an integer room ID for every room cell found in the level file grid
    rooms      = {}   # dict mapping integer room ID to Room objects, same structure the rest of the codebase expects from the old generate_dungeon
    next_id    = 0    # counter incremented each time a new room cell is found during the first-pass scan of the grid

    for r, line in enumerate(lines):                        # iterates over each row of the level file with its row index
        for c, ch in enumerate(line):                       # iterates over each character in the row with its column index
            if ch == '.':                                   # '.' is empty space — no room here, skip it entirely
                continue
            room = Room(next_id)                            # creates a Room object for this non-empty cell with the next available ID
            room.grid_pos  = (c, r)                         # stores the (col, row) grid coordinate so exit wiring can reference neighbours
            room.gamemode  = random.choice(GAMEMODES)       # randomly assigns topdown or platformer physics to each room for variety
            room.cols      = random.randint(ROOM_COLS_MIN, ROOM_COLS_MAX)   # random room width in tiles within the configured range
            room.rows      = random.randint(ROOM_ROWS_MIN, ROOM_ROWS_MAX)   # random room height in tiles within the configured range
            room.is_start  = (ch == 's')                    # NEW: marks this room as the start room if the cell character is 's'
            room.is_finish = (ch == 'f')                    # NEW: marks this room as the finish room if the cell character is 'f'
            cell_to_id[(c, r)] = next_id                    # registers this grid coordinate as belonging to this room ID for neighbour lookup
            rooms[next_id]     = room                       # registers the Room object in the rooms dict under its integer ID
            next_id += 1                                    # increments the ID counter ready for the next room cell found in the grid

    # NEW: second pass — for every room cell check its four cardinal neighbours; if a neighbour is also a room cell wire a bidirectional exit between them
    for (c, r), room_id in cell_to_id.items():              # iterates over every room cell coordinate and its assigned room ID
        for direction, (dc, dr) in {"north": (0,-1), "south": (0,1), "east": (1,0), "west": (-1,0)}.items():  # checks all four cardinal directions
            nc, nr = c + dc, r + dr                         # computes the grid coordinate of the neighbour in this direction
            if (nc, nr) in cell_to_id:                      # checks if that neighbour coordinate also contains a room cell (not empty space)
                neighbour_id = cell_to_id[(nc, nr)]         # looks up the room ID assigned to the neighbouring cell
                rooms[room_id].exits[direction] = neighbour_id  # wires an exit from this room to the neighbour in the given direction

    # NEW: find the room marked is_start and reassign it to ID 0 so the rest of the codebase (which assumes current_id=0 is the start) works without changes
    start_room = next((rm for rm in rooms.values() if rm.is_start), rooms[0])  # finds the 's' room or falls back to room 0 if none found
    if start_room.id != 0:                                  # only remap IDs if the start room isn't already ID 0
        old_start_id = start_room.id                        # saves the start room's current ID so we can find room 0 to swap with
        old_zero     = rooms[0]                             # gets the room currently sitting at ID 0 that will be swapped to the start room's old ID
        # swap IDs and update all exits that referenced either of the two swapped rooms so the rooms dict stays internally consistent after the swap
        start_room.id = 0                                   # gives the start room ID 0 as expected by the rest of the codebase
        old_zero.id   = old_start_id                        # gives the previously-zero room the start room's old ID to complete the swap
        rooms[0]            = start_room                    # places the start room at key 0 in the rooms dict
        rooms[old_start_id] = old_zero                      # places the displaced room at the start room's old key in the rooms dict
        for room in rooms.values():                         # iterates over all rooms to fix any exits that still point to the old IDs after the swap
            for d, rid in room.exits.items():               # iterates over each exit of this room
                if   rid == 0:            room.exits[d] = old_start_id   # exit that pointed to old ID 0 now points to old_start_id after the swap
                elif rid == old_start_id: room.exits[d] = 0              # exit that pointed to old_start_id now points to 0 after the swap

    return rooms   # returns the completed rooms dict with room 0 always being the start room, ready for Game.new() to consume unchanged


def _neighbour(col, row, d):
    return {"north": (col, row-1), "south": (col, row+1),
            "east": (col+1, row), "west": (col-1, row)}[d]


# source: https://nerdparadise.com/programming/pygame/part4
def build_walls(room):
    T = TILESIZE
    W = (room.cols + WALL_TILES * 2) * T
    H = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    exits  = room.exits
    wt     = WALL_TILES * T
    gap_px = DOOR_TILES * T
    door_x0 = ox + W // 2 - gap_px // 2
    door_x1 = ox + W // 2 + gap_px // 2
    door_y0 = oy + H // 2 - gap_px // 2
    door_y1 = oy + H // 2 + gap_px // 2
    walls = []
    if "north" in exits:
        walls += [pg.Rect(ox, oy, door_x0 - ox, wt), pg.Rect(door_x1, oy, (ox+W)-door_x1, wt)]
    else:
        walls.append(pg.Rect(ox, oy, W, wt))
    if "south" in exits:
        walls += [pg.Rect(ox, oy+H-wt, door_x0-ox, wt), pg.Rect(door_x1, oy+H-wt, (ox+W)-door_x1, wt)]
    else:
        walls.append(pg.Rect(ox, oy+H-wt, W, wt))
    if "west" in exits:
        walls += [pg.Rect(ox, oy, wt, door_y0-oy), pg.Rect(ox, door_y1, wt, (oy+H)-door_y1)]
    else:
        walls.append(pg.Rect(ox, oy, wt, H))
    if "east" in exits:
        walls += [pg.Rect(ox+W-wt, oy, wt, door_y0-oy), pg.Rect(ox+W-wt, door_y1, wt, (oy+H)-door_y1)]
    else:
        walls.append(pg.Rect(ox+W-wt, oy, wt, H))
    return walls


# source: https://www.youtube.com/watch?v=WC6Yuzw7IYc
def draw_room(surface, room, walls, font, rooms):
    T  = TILESIZE
    W  = (room.cols + WALL_TILES * 2) * T
    H  = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    wt = WALL_TILES * T
    for r in range(room.rows):
        for c in range(room.cols):
            x = ox + wt + c * T
            y = oy + wt + r * T
            # NEW: finish rooms are drawn with a gold floor colour so the player can easily identify the goal room when they enter it
            colour = (180, 150, 30) if room.is_finish else FLOOR_COLOR  # gold for finish room, standard floor colour for all other rooms
            pg.draw.rect(surface, colour, (x, y, T, T))
            pg.draw.rect(surface, (40, 40, 40), (x, y, T, T), 1)
    for w in walls:
        pg.draw.rect(surface, WALL_COLOR, w)
    gap_px = DOOR_TILES * T
    hx = ox + W // 2
    vy = oy + H // 2
    if "north" in room.exits: pg.draw.rect(surface, FLOOR_COLOR, (hx - gap_px//2, oy, gap_px, wt))
    if "south" in room.exits: pg.draw.rect(surface, FLOOR_COLOR, (hx - gap_px//2, oy+H-wt, gap_px, wt))
    if "west"  in room.exits: pg.draw.rect(surface, FLOOR_COLOR, (ox, vy - gap_px//2, wt, gap_px))
    if "east"  in room.exits: pg.draw.rect(surface, FLOOR_COLOR, (ox+W-wt, vy - gap_px//2, wt, gap_px))
    label = font.render(room.gamemode, True, (120, 120, 120))

    # NEW: draw a direction arrow in the top-right corner pointing from the current room's grid position toward the finish room's grid position
    finish_room = next((r for r in rooms.values() if r.is_finish), None)        # finds the finish room by scanning all rooms for the is_finish flag
    if finish_room and not room.is_finish:                                       # only draws the arrow if a finish room exists and we are not already in it
        cr, cc = room.grid_pos                                                   # unpacks the current room's (col, row) grid position for vector calculation
        fr, fc = finish_room.grid_pos                                            # unpacks the finish room's (col, row) grid position for vector calculation
        dx, dy = fr - cr, fc - cc                                                # computes the raw direction vector from current room to finish room in grid space
        length = (dx**2 + dy**2) ** 0.5                                          # calculates the vector length to normalise it into a unit direction vector
        if length > 0:                                                           # guards against division by zero if current room IS the finish room somehow
            nx, ny   = dx / length, dy / length                                 # normalises the direction vector to unit length for consistent arrow sizing
            cx_a, cy_a = WIDTH - 60, 60                                         # sets the arrow centre position in the top-right corner of the screen
            arm      = 24                                                        # half-length of the arrow in pixels — controls how large the pointer appears
            tip      = (int(cx_a + nx * arm), int(cy_a + ny * arm))             # calculates the arrowhead tip pixel position using the normalised direction
            tail     = (int(cx_a - nx * arm), int(cy_a - ny * arm))             # calculates the arrow tail pixel position opposite the tip
            pg.draw.circle(surface, (60, 60, 60), (cx_a, cy_a), arm + 8)        # draws a dark filled circle as the compass background behind the arrow
            pg.draw.line(surface, (220, 180, 50), tail, tip, 3)                 # draws the arrow shaft as a gold line from tail to tip
            pg.draw.polygon(surface, (220, 180, 50), [                          # draws a filled triangle arrowhead at the tip pointing in the direction
                tip,
                (int(tip[0] - nx*8 + ny*5), int(tip[1] - ny*8 - nx*5)),        # left wing of the arrowhead, perpendicular offset from the shaft direction
                (int(tip[0] - nx*8 - ny*5), int(tip[1] - ny*8 + nx*5)),        # right wing of the arrowhead, perpendicular offset from the shaft direction
            ])
        
    surface.blit(label, (ox + W//2 - label.get_width()//2, oy + H//2 - label.get_height()//2))


# source: https://www.pygame.org/docs/ref/rect.html
def entry_pos(direction, room):
    T      = TILESIZE
    W      = (room.cols + WALL_TILES * 2) * T
    H      = (room.rows + WALL_TILES * 2) * T
    ox     = (WIDTH - W) // 2
    oy     = (HEIGHT - H) // 2
    margin = WALL_TILES * TILESIZE + TILESIZE + 4
    cx     = ox + W // 2
    cy     = oy + H // 2
    if direction == "north": return cx, oy + H - margin
    if direction == "south": return cx, oy + margin
    if direction == "west":  return ox + W - margin, cy
    if direction == "east":  return ox + margin, cy
    return cx, cy


def centre_pos(room):
    T  = TILESIZE
    W  = (room.cols + WALL_TILES * 2) * T
    H  = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    return ox + W // 2, oy + H // 2


# source: https://www.geeksforgeeks.org/python/collision-detection-in-pygame/
def touched_exit(player_rect, room):
    T   = TILESIZE
    W   = (room.cols + WALL_TILES * 2) * T
    H   = (room.rows + WALL_TILES * 2) * T
    ox  = (WIDTH - W) // 2
    oy  = (HEIGHT - H) // 2
    wt  = WALL_TILES * TILESIZE
    gap = DOOR_TILES * TILESIZE
    cx  = ox + W // 2
    cy  = oy + H // 2
    pr  = player_rect
    if "north" in room.exits and pr.top    <= oy+wt      and cx-gap//2 <= pr.centerx <= cx+gap//2: return "north"
    if "south" in room.exits and pr.bottom >= oy+H-wt    and cx-gap//2 <= pr.centerx <= cx+gap//2: return "south"
    if "west"  in room.exits and pr.left   <= ox+wt      and cy-gap//2 <= pr.centery <= cy+gap//2: return "west"
    if "east"  in room.exits and pr.right  >= ox+W-wt    and cy-gap//2 <= pr.centery <= cy+gap//2: return "east"
    return None