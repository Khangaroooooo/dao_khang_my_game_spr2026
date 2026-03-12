import pygame as pg
import random
from settings import *

vec = pg.math.Vector2


class Room:
    def __init__(self, room_id):
        self.id = room_id
        self.exits = {}
        self.grid_pos = (0, 0)
        self.movement = random.choice(MOVEMENT_MODES)


def generate_dungeon(num_rooms):
    rooms = {}
    grid = {}
    next_id = 1

    r0 = Room(0)
    r0.grid_pos = (0, 0)
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


def _neighbour(col, row, d):
    return {"north": (col, row-1), "south": (col, row+1),
            "east": (col+1, row), "west": (col-1, row)}[d]


def build_walls(exits):
    T = TILESIZE
    ox, oy = ROOM_OX, ROOM_OY
    W, H = ROOM_PX_W, ROOM_PX_H
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


def draw_room(surface, room, walls, font):
    T = TILESIZE
    ox, oy = ROOM_OX, ROOM_OY
    W, H = ROOM_PX_W, ROOM_PX_H
    wt = WALL_TILES * T

    for r in range(ROOM_ROWS):
        for c in range(ROOM_COLS):
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

    label = font.render(room.movement, True, (120, 120, 120))
    surface.blit(label, (ox + W//2 - label.get_width()//2,
                         oy + H//2 - label.get_height()//2))


def entry_pos(direction):
    ox, oy = ROOM_OX, ROOM_OY
    W, H = ROOM_PX_W, ROOM_PX_H
    margin = WALL_TILES * TILESIZE + TILESIZE + 4
    cx = ox + W // 2
    cy = oy + H // 2
    if direction == "north": return cx, oy + H - margin
    if direction == "south": return cx, oy + margin
    if direction == "west": return ox + W - margin, cy
    if direction == "east": return ox + margin, cy
    return cx, cy


def centre_pos():
    return ROOM_OX + ROOM_PX_W // 2, ROOM_OY + ROOM_PX_H // 2


def touched_exit(player_rect, exits):
    ox, oy = ROOM_OX, ROOM_OY
    W, H = ROOM_PX_W, ROOM_PX_H
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