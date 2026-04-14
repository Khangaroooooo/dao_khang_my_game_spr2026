import pygame as pg
import random
import os
from settings import *

vec = pg.math.Vector2

img_folder = os.path.join(os.path.dirname(__file__), 'images')

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x,y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        return image
    
class Room:
    def __init__(self, room_id):
        self.id = room_id
        self.exits = {}
        self.grid_pos = (0, 0)
        self.gamemode = "topdown"  # gets overwritten by generate_dungeon
        self.cols = ROOM_COLS_MIN  # width in tiles, overwritten by generate_dungeon
        self.rows = ROOM_ROWS_MIN  # height in tiles, overwritten by generate_dungeon

# source: https://tiendil.org/en/posts/dungeon-generation-from-simple-to-complex
def generate_dungeon(num_rooms):
    rooms = {}
    grid = {}
    next_id = 1

    r0 = Room(0)
    r0.grid_pos = (0, 0)
    r0.gamemode = random.choice(GAMEMODES) # pick a random physics mode for the starting room
    r0.cols = random.randint(ROOM_COLS_MIN, ROOM_COLS_MAX) # pick a random width for the starting room
    r0.rows = random.randint(ROOM_ROWS_MIN, ROOM_ROWS_MAX) # pick a random height for the starting room
    rooms[0] = r0
    grid[(0, 0)] = 0
    frontier = [(0, 0)]

    while len(rooms) < num_rooms and frontier:
        col, row = random.choice(frontier)
        cur_id = grid[(col, row)]
        dirs = DIRS[:]
        random.shuffle(dirs)
        added = False

        for d in dirs:
            nc, nr = _neighbour(col, row, d)

            if (nc, nr) in grid:
                if d not in rooms[cur_id].exits:
                    nid = grid[(nc, nr)]
                    rooms[cur_id].exits[d] = nid
                    rooms[nid].exits[OPPOSITE[d]] = cur_id
                continue

            if not added:
                new = Room(next_id)
                new.grid_pos = (nc, nr)
                new.gamemode = random.choice(GAMEMODES) # each room gets a random physics mode
                new.cols = random.randint(ROOM_COLS_MIN, ROOM_COLS_MAX) # each room gets a random width
                new.rows = random.randint(ROOM_ROWS_MIN, ROOM_ROWS_MAX) # each room gets a random height
                rooms[next_id] = new
                grid[(nc, nr)] = next_id
                rooms[cur_id].exits[d] = next_id
                rooms[next_id].exits[OPPOSITE[d]] = cur_id
                frontier.append((nc, nr))
                next_id += 1
                added = True

            if len(rooms) >= num_rooms:
                break

        if not added:
            frontier.remove((col, row))

    return rooms

# source: https://www.redblobgames.com/grids/parts/#neighbors
def _neighbour(col, row, d):
    return {"north": (col, row-1), "south": (col, row+1),
            "east": (col+1, row), "west": (col-1, row)}[d]

# source: https://nerdparadise.com/programming/pygame/part4
def build_walls(room):
    T = TILESIZE
    W = (room.cols + WALL_TILES * 2) * T # pixel width of this room
    H = (room.rows + WALL_TILES * 2) * T # pixel height of this room
    ox = (WIDTH - W) // 2 # center the room horizontally on screen
    oy = (HEIGHT - H) // 2 # center the room vertically on screen
    exits = room.exits
    wt = WALL_TILES * T
    gap_px = DOOR_TILES * T
    door_x0 = ox + W // 2 - gap_px // 2
    door_x1 = ox + W // 2 + gap_px // 2
    door_y0 = oy + H // 2 - gap_px // 2
    door_y1 = oy + H // 2 + gap_px // 2

    walls = []

    if "north" in exits:
        walls += [pg.Rect(ox, oy, door_x0 - ox, wt),
                  pg.Rect(door_x1, oy, (ox + W) - door_x1, wt)]
    else:
        walls.append(pg.Rect(ox, oy, W, wt))

    if "south" in exits:
        walls += [pg.Rect(ox, oy + H - wt, door_x0 - ox, wt),
                  pg.Rect(door_x1, oy + H - wt, (ox + W) - door_x1, wt)]
    else:
        walls.append(pg.Rect(ox, oy + H - wt, W, wt))

    if "west" in exits:
        walls += [pg.Rect(ox, oy, wt, door_y0 - oy),
                  pg.Rect(ox, door_y1, wt, (oy + H) - door_y1)]
    else:
        walls.append(pg.Rect(ox, oy, wt, H))

    if "east" in exits:
        walls += [pg.Rect(ox + W - wt, oy, wt, door_y0 - oy),
                  pg.Rect(ox + W - wt, door_y1, wt, (oy + H) - door_y1)]
    else:
        walls.append(pg.Rect(ox + W - wt, oy, wt, H))

    return walls

# source: https://www.youtube.com/watch?v=WC6Yuzw7IYc
def draw_room(surface, room, walls, font):
    T = TILESIZE
    W = (room.cols + WALL_TILES * 2) * T
    H = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    wt = WALL_TILES * T

    for r in range(room.rows):
        for c in range(room.cols):
            x = ox + wt + c * T
            y = oy + wt + r * T
            pg.draw.rect(surface, FLOOR_COLOR, (x, y, T, T))
            pg.draw.rect(surface, (40, 40, 40), (x, y, T, T), 1)

    for w in walls:
        pg.draw.rect(surface, WALL_COLOR, w)

    gap_px = DOOR_TILES * T
    hx = ox + W // 2
    vy = oy + H // 2
    if "north" in room.exits:
        pg.draw.rect(surface, FLOOR_COLOR, (hx - gap_px//2, oy, gap_px, wt))
    if "south" in room.exits:
        pg.draw.rect(surface, FLOOR_COLOR, (hx - gap_px//2, oy + H - wt, gap_px, wt))
    if "west" in room.exits:
        pg.draw.rect(surface, FLOOR_COLOR, (ox, vy - gap_px//2, wt, gap_px))
    if "east" in room.exits:
        pg.draw.rect(surface, FLOOR_COLOR, (ox + W - wt, vy - gap_px//2, wt, gap_px))
    
    label = font.render(room.gamemode, True, (120, 120, 120)) # shows the current room's physics mode
    surface.blit(label, (ox + W//2 - label.get_width()//2, oy + H//2 - label.get_height()//2))

# source: https://www.pygame.org/docs/ref/rect.html
def entry_pos(direction, room):
    T = TILESIZE
    W = (room.cols + WALL_TILES * 2) * T
    H = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    margin = WALL_TILES * TILESIZE + TILESIZE + 4
    cx = ox + W // 2
    cy = oy + H // 2
    if direction == "north": return cx, oy + H - margin
    if direction == "south": return cx, oy + margin
    if direction == "west": return ox + W - margin, cy
    if direction == "east": return ox + margin, cy
    return cx, cy
    # uses the direction of which entrance was exited; uses reverse mapping i.e. enter north - leave south, enter west - leave east
    # thus returns coords of reverse mapping; final return statement is if it is the first room; spawn in center


def centre_pos(room):
    T = TILESIZE
    W = (room.cols + WALL_TILES * 2) * T
    H = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    return ox + W // 2, oy + H // 2

# source: https://www.geeksforgeeks.org/python/collision-detection-in-pygame/
def touched_exit(player_rect, room):
    T = TILESIZE
    W = (room.cols + WALL_TILES * 2) * T
    H = (room.rows + WALL_TILES * 2) * T
    ox = (WIDTH - W) // 2
    oy = (HEIGHT - H) // 2
    exits = room.exits
    wt = WALL_TILES * TILESIZE
    gap = DOOR_TILES * TILESIZE
    cx = ox + W // 2
    cy = oy + H // 2
    pr = player_rect

    if "north" in exits and pr.top <= oy + wt and cx - gap//2 <= pr.centerx <= cx + gap//2: return "north"
    if "south" in exits and pr.bottom >= oy + H - wt and cx - gap//2 <= pr.centerx <= cx + gap//2: return "south"
    if "west" in exits and pr.left <= ox + wt and cy - gap//2 <= pr.centery <= cy + gap//2: return "west"
    if "east" in exits and pr.right >= ox + W - wt and cy - gap//2 <= pr.centery <= cy + gap//2: return "east"
    return None