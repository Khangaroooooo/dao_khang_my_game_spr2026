import pygame as pg          # imports pygame for Rect creation and vector math
import random                # imports the random module for dungeon generation randomness
import os                    # imports os for cross-platform file path construction
from settings import *       # imports all constants (TILESIZE, WALL_TILES, ROOM_COLS_MIN, GAMEMODES, etc.)

vec = pg.math.Vector2        # aliases pygame's 2D vector class for position/velocity calculations

# easier way for directing using os to images folder
img_folder = os.path.join(os.path.dirname(__file__), 'images')  # builds an absolute path to the 'images' subfolder next to this script


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()    # loads the spritesheet image from disk and converts it for fast blitting

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))                     # creates a blank surface of the requested frame size
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))  # copies the specified region from the spritesheet onto the blank surface
        new_image = pg.transform.scale(image, (width, height)) # scales the extracted region to the target dimensions (no-op if size matches)
        image = new_image                                       # replaces the original surface reference with the scaled one
        return image                                            # returns the final cropped (and optionally scaled) frame surface

    
class Room:
    def __init__(self, room_id):
        self.id = room_id               # stores this room's unique integer identifier
        self.exits = {}                 # dict mapping direction strings ("north", etc.) to the IDs of connected rooms
        self.grid_pos = (0, 0)          # the room's (col, row) position in the abstract dungeon grid
        self.gamemode = "topdown"       # the physics mode for this room; overwritten by generate_dungeon to a random value
        self.cols = ROOM_COLS_MIN       # room width in tiles; overwritten by generate_dungeon with a random value
        self.rows = ROOM_ROWS_MIN       # room height in tiles; overwritten by generate_dungeon with a random value

# source: https://tiendil.org/en/posts/dungeon-generation-from-simple-to-complex
def generate_dungeon(num_rooms):
    rooms = {}              # dict mapping room ID integers to Room objects
    grid = {}               # dict mapping (col, row) grid coordinates to room ID integers
    next_id = 1             # counter for assigning unique IDs to new rooms (room 0 is the start)

    r0 = Room(0)                                        # creates the starting room with ID 0
    r0.grid_pos = (0, 0)                                # places the starting room at the origin of the dungeon grid
    r0.gamemode = random.choice(GAMEMODES)              # randomly assigns either "topdown" or "platformer" physics to the start room
    r0.cols = random.randint(ROOM_COLS_MIN, ROOM_COLS_MAX)  # gives the start room a random width within the allowed tile range
    r0.rows = random.randint(ROOM_ROWS_MIN, ROOM_ROWS_MAX)  # gives the start room a random height within the allowed tile range
    rooms[0] = r0                                       # registers the starting room in the rooms dict
    grid[(0, 0)] = 0                                    # marks the origin grid cell as occupied by room 0
    frontier = [(0, 0)]                                 # list of grid positions that still have potential to grow new exits

    while len(rooms) < num_rooms and frontier:          # keeps generating rooms until the target count is reached or no frontier remains
        col, row = random.choice(frontier)              # picks a random grid position from the frontier to expand from
        cur_id = grid[(col, row)]                       # retrieves the room ID at the chosen frontier position
        dirs = DIRS[:]                                  # makes a copy of the direction list to shuffle without mutating the original
        random.shuffle(dirs)                            # randomises the order directions are tried to ensure varied dungeon layouts
        added = False                                   # flag to ensure at most one new room is added per frontier cell per iteration

        for d in dirs:                                  # tries each direction in shuffled order
            nc, nr = _neighbour(col, row, d)            # calculates the grid coordinates of the neighbour in direction d

            if (nc, nr) in grid:                        # checks if that neighbour cell is already occupied by an existing room
                if d not in rooms[cur_id].exits:        # checks if there isn't already a connection in that direction
                    nid = grid[(nc, nr)]                # gets the ID of the already-existing neighbour room
                    rooms[cur_id].exits[d] = nid        # creates a one-way connection from the current room to the neighbour
                    rooms[nid].exits[OPPOSITE[d]] = cur_id  # creates the matching reverse connection from the neighbour back
                continue                                # moves on to try the next direction after handling the existing neighbour

            if not added:                               # only creates a brand-new room if one hasn't been added this iteration
                new = Room(next_id)                     # creates a new Room object with the next available ID
                new.grid_pos = (nc, nr)                 # sets the new room's position in the dungeon grid
                new.gamemode = random.choice(GAMEMODES) # randomly assigns a physics mode to the new room
                new.cols = random.randint(ROOM_COLS_MIN, ROOM_COLS_MAX)  # randomly sets the new room's width
                new.rows = random.randint(ROOM_ROWS_MIN, ROOM_ROWS_MAX)  # randomly sets the new room's height
                rooms[next_id] = new                    # registers the new room in the rooms dict
                grid[(nc, nr)] = next_id                # marks the new grid cell as occupied by this room's ID
                rooms[cur_id].exits[d] = next_id        # connects the current room to the new room in direction d
                rooms[next_id].exits[OPPOSITE[d]] = cur_id  # connects the new room back to the current room in the opposite direction
                frontier.append((nc, nr))               # adds the new room's grid position to the frontier for future expansion
                next_id += 1                            # increments the ID counter for the next new room
                added = True                            # marks that a room was added this iteration to prevent adding more

            if len(rooms) >= num_rooms:                 # checks if the total room target has been met mid-loop
                break                                   # stops trying more directions for this frontier cell

        if not added:                                   # if no new room could be added from this cell
            frontier.remove((col, row))                 # removes it from the frontier since it can no longer expand

    return rooms                                        # returns the completed dict of all generated Room objects

# source: https://www.redblobgames.com/grids/parts/#neighbors
def _neighbour(col, row, d):
    return {"north": (col, row-1), "south": (col, row+1),   # north decreases row, south increases row
            "east": (col+1, row), "west": (col-1, row)}[d]  # east increases col, west decreases col; returns the adjacent grid cell for direction d

# source: https://nerdparadise.com/programming/pygame/part4
def build_walls(room):
    T = TILESIZE                                    # shorthand for the tile size in pixels
    W = (room.cols + WALL_TILES * 2) * T           # total pixel width of the room including wall borders on both sides
    H = (room.rows + WALL_TILES * 2) * T           # total pixel height of the room including wall borders on both sides
    ox = (WIDTH - W) // 2                          # horizontal pixel offset to centre the room on the screen
    oy = (HEIGHT - H) // 2                         # vertical pixel offset to centre the room on the screen
    exits = room.exits                             # shorthand reference to the room's exits dict
    wt = WALL_TILES * T                            # wall border thickness in pixels
    gap_px = DOOR_TILES * T                        # door opening width in pixels
    door_x0 = ox + W // 2 - gap_px // 2           # left pixel edge of the horizontal door gap (north/south walls)
    door_x1 = ox + W // 2 + gap_px // 2           # right pixel edge of the horizontal door gap
    door_y0 = oy + H // 2 - gap_px // 2           # top pixel edge of the vertical door gap (east/west walls)
    door_y1 = oy + H // 2 + gap_px // 2           # bottom pixel edge of the vertical door gap

    walls = []                                     # list that will collect all wall pygame.Rect segments

    if "north" in exits:                           # if the room has a north exit, split the top wall into two segments with a gap
        walls += [pg.Rect(ox, oy, door_x0 - ox, wt),               # left portion of the north wall (from room left to door left)
                  pg.Rect(door_x1, oy, (ox + W) - door_x1, wt)]    # right portion of the north wall (from door right to room right)
    else:
        walls.append(pg.Rect(ox, oy, W, wt))      # no exit: the north wall is one solid rect spanning the full room width

    if "south" in exits:                           # if the room has a south exit, split the bottom wall into two segments with a gap
        walls += [pg.Rect(ox, oy + H - wt, door_x0 - ox, wt),              # left portion of the south wall
                  pg.Rect(door_x1, oy + H - wt, (ox + W) - door_x1, wt)]   # right portion of the south wall
    else:
        walls.append(pg.Rect(ox, oy + H - wt, W, wt))  # no exit: the south wall is one solid rect spanning the full room width

    if "west" in exits:                            # if the room has a west exit, split the left wall into two segments with a gap
        walls += [pg.Rect(ox, oy, wt, door_y0 - oy),               # top portion of the west wall (above the door)
                  pg.Rect(ox, door_y1, wt, (oy + H) - door_y1)]    # bottom portion of the west wall (below the door)
    else:
        walls.append(pg.Rect(ox, oy, wt, H))      # no exit: the west wall is one solid rect spanning the full room height

    if "east" in exits:                            # if the room has an east exit, split the right wall into two segments with a gap
        walls += [pg.Rect(ox + W - wt, oy, wt, door_y0 - oy),              # top portion of the east wall (above the door)
                  pg.Rect(ox + W - wt, door_y1, wt, (oy + H) - door_y1)]   # bottom portion of the east wall (below the door)
    else:
        walls.append(pg.Rect(ox + W - wt, oy, wt, H))  # no exit: the east wall is one solid rect spanning the full room height

    return walls                                   # returns the complete list of wall rects for this room

# source: https://www.youtube.com/watch?v=WC6Yuzw7IYc
def draw_room(surface, room, walls, font):
    T = TILESIZE                                    # shorthand for tile pixel size
    W = (room.cols + WALL_TILES * 2) * T           # total room width in pixels
    H = (room.rows + WALL_TILES * 2) * T           # total room height in pixels
    ox = (WIDTH - W) // 2                          # x offset to centre the room on screen
    oy = (HEIGHT - H) // 2                         # y offset to centre the room on screen
    wt = WALL_TILES * T                            # border thickness in pixels

    for r in range(room.rows):                     # iterates over each tile row in the room interior
        for c in range(room.cols):                 # iterates over each tile column in the room interior
            x = ox + wt + c * T                   # calculates the pixel x coordinate of this floor tile (offset past the wall border)
            y = oy + wt + r * T                   # calculates the pixel y coordinate of this floor tile
            pg.draw.rect(surface, FLOOR_COLOR, (x, y, T, T))       # draws the floor tile as a filled rectangle
            pg.draw.rect(surface, (40, 40, 40), (x, y, T, T), 1)   # draws a 1-pixel dark border around each tile to create a grid look

    for w in walls:                                # iterates over all wall rect segments for this room
        pg.draw.rect(surface, WALL_COLOR, w)       # draws each wall segment as a solid dark rectangle

    gap_px = DOOR_TILES * T                        # door opening width in pixels
    hx = ox + W // 2                              # horizontal centre x of the room (door openings align here for north/south)
    vy = oy + H // 2                              # vertical centre y of the room (door openings align here for east/west)
    if "north" in room.exits:                      # if there's a north exit
        pg.draw.rect(surface, FLOOR_COLOR, (hx - gap_px//2, oy, gap_px, wt))           # paints the north doorway gap with floor colour to "open" the wall
    if "south" in room.exits:                      # if there's a south exit
        pg.draw.rect(surface, FLOOR_COLOR, (hx - gap_px//2, oy + H - wt, gap_px, wt)) # paints the south doorway gap with floor colour
    if "west" in room.exits:                       # if there's a west exit
        pg.draw.rect(surface, FLOOR_COLOR, (ox, vy - gap_px//2, wt, gap_px))           # paints the west doorway gap with floor colour
    if "east" in room.exits:                       # if there's an east exit
        pg.draw.rect(surface, FLOOR_COLOR, (ox + W - wt, vy - gap_px//2, wt, gap_px)) # paints the east doorway gap with floor colour
    
    label = font.render(room.gamemode, True, (120, 120, 120))                           # renders the room's physics mode as a grey text label
    surface.blit(label, (ox + W//2 - label.get_width()//2, oy + H//2 - label.get_height()//2))  # draws the label centred in the room

# source: https://www.pygame.org/docs/ref/rect.html
def entry_pos(direction, room):
    T = TILESIZE                                    # shorthand for tile pixel size
    W = (room.cols + WALL_TILES * 2) * T           # total pixel width of the destination room
    H = (room.rows + WALL_TILES * 2) * T           # total pixel height of the destination room
    ox = (WIDTH - W) // 2                          # x offset to centre the destination room on screen
    oy = (HEIGHT - H) // 2                         # y offset to centre the destination room on screen
    margin = WALL_TILES * TILESIZE + TILESIZE + 4  # pixel distance from the inner wall edge to place the player (just inside the door)
    cx = ox + W // 2                               # horizontal centre pixel of the room
    cy = oy + H // 2                               # vertical centre pixel of the room
    if direction == "north": return cx, oy + H - margin   # entered from north → spawn near the south wall of the new room
    if direction == "south": return cx, oy + margin       # entered from south → spawn near the north wall of the new room
    if direction == "west":  return ox + W - margin, cy   # entered from west → spawn near the east wall of the new room
    if direction == "east":  return ox + margin, cy       # entered from east → spawn near the west wall of the new room
    return cx, cy                                          # fallback: spawn at the room centre (used only for the very first room)
    # uses the direction of which entrance was exited; uses reverse mapping i.e. enter north - leave south, enter west - leave east
    # thus returns coords of reverse mapping; final return statement is if it is the first room; spawn in center


def centre_pos(room):
    T = TILESIZE                                    # shorthand for tile pixel size
    W = (room.cols + WALL_TILES * 2) * T           # total pixel width of the room
    H = (room.rows + WALL_TILES * 2) * T           # total pixel height of the room
    ox = (WIDTH - W) // 2                          # x offset to centre the room on screen
    oy = (HEIGHT - H) // 2                         # y offset to centre the room on screen
    return ox + W // 2, oy + H // 2               # returns the absolute pixel coordinates of the room's centre point

# source: https://www.geeksforgeeks.org/python/collision-detection-in-pygame/
def touched_exit(player_rect, room):
    T = TILESIZE                                    # shorthand for tile pixel size
    W = (room.cols + WALL_TILES * 2) * T           # total pixel width of the current room
    H = (room.rows + WALL_TILES * 2) * T           # total pixel height of the current room
    ox = (WIDTH - W) // 2                          # x offset to centre the room on screen
    oy = (HEIGHT - H) // 2                         # y offset to centre the room on screen
    exits = room.exits                             # shorthand for the current room's exits dict
    wt = WALL_TILES * TILESIZE                     # wall border thickness in pixels
    gap = DOOR_TILES * TILESIZE                    # door opening width in pixels
    cx = ox + W // 2                              # horizontal centre x of the room (used to check if player is aligned with a north/south door)
    cy = oy + H // 2                              # vertical centre y of the room (used to check if player is aligned with an east/west door)
    pr = player_rect                              # shorthand alias for the player's hit rect

    if "north" in exits and pr.top <= oy + wt and cx - gap//2 <= pr.centerx <= cx + gap//2: return "north"  # player's top edge crossed the north wall AND is horizontally within the door gap
    if "south" in exits and pr.bottom >= oy + H - wt and cx - gap//2 <= pr.centerx <= cx + gap//2: return "south"  # player's bottom edge crossed the south wall AND is within the door gap
    if "west" in exits and pr.left <= ox + wt and cy - gap//2 <= pr.centery <= cy + gap//2: return "west"  # player's left edge crossed the west wall AND is vertically within the door gap
    if "east" in exits and pr.right >= ox + W - wt and cy - gap//2 <= pr.centery <= cy + gap//2: return "east"  # player's right edge crossed the east wall AND is within the door gap
    return None                                    # returns None if the player hasn't touched any exit this frame