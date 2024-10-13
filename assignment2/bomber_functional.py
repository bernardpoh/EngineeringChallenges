from typing import *
from tkinter import *
from tkinter import font
from time import time
from random import *


class vector2(NamedTuple):
    x: float
    y: float

    def __add__(self, other) -> Self:
        x1, y1 = self
        x2, y2 = other
        return vector2(x1 + x2, y1 + y2)

    def __sub__(self, other) -> Self:
        x1, y1 = self
        x2, y2 = other
        return vector2(x1 - x2, y1 - y2)

    def __mul__(self, value) -> Self:
        x, y = self
        return vector2(x * value, y * value)

    def __rmul__(self, value) -> Self:
        return self * value

    def __div__(self, value) -> Self:
        return (self * 1/value)

    def __neg__(self) -> Self:
        return self * -1


def flatten(xss):
    return [x for xs in xss for x in xs]


CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700

BUILDING_WIDTH_MULTIPLIER = 0.8
TOTAL_BUILDINGS = 10

MIN_BUILDING_HEIGHT = 10
MAX_BUILDING_HEIGHT = 500
BUILDING_WIDTH_MULTIPLIER = 0.9

HEIGHT_REMOVED_WHEN_BOMBED = 80
BOMB_FALL_VELOCITY = vector2(0, 8)

PLANE_VELOCITY = vector2(-4, 0)
PLANE_FALL_AMOUNT = 100

# Scores are redesigned now
# POINTS_EACH_TIME_THE_PLANE_MOVES_DOWN = 10
# WIN_SCORE_BONUS = 1000

BUILDING_DAMAGE_SCORE = 10
BUILDING_DESTRUCTION_SCORE = 100

BOMB_SHAPE = [(0, 0), (10, 0), (5, 5), (10, 10), (10, 20),
              (5, 22), (0, 20), (0, 10), (5, 5),]

PLANE_BODY_SHAPE = [(0, 28), (20, 16), (120, 16), (94, 32), (12, 32)]
PLANE_WING1_SHAPE = [(40, 28), (76, 28), (94, 48), (80, 48)]
PLANE_WING2_SHAPE = [(52, 16), (78, 8), (94, 8), (81, 16)]
PLANE_TAIL_SHAPE = [(90, 16), (110, 0), (124, 0), (116, 16)]

PLANE_SHAPES = [("red", PLANE_BODY_SHAPE), ("grey", PLANE_WING1_SHAPE),
                ("grey", PLANE_WING2_SHAPE), ("grey", PLANE_TAIL_SHAPE)]

PLANE_WIDTH = 124
PLANE_START = vector2(CANVAS_HEIGHT + PLANE_WIDTH, 0)

PLANE_NOSE = vector2(0, 28)
PLANE_BOTTOM = vector2(12, 32)
PLANE_WING = vector2(94, 48)
PLANE_HITBOX = [PLANE_NOSE, PLANE_BOTTOM, PLANE_WING]

# Smoothing is disabled for now
# FRAMES_PER_CALIBRATION = 10
# STANDARD_FRAMES_PER_SECOND = 60
# SPEED_CALIBRATION_CONSTANT = STANDARD_FRAMES_PER_SECOND / FRAMES_PER_CALIBRATION
# EXPONENTIAL_SMOOTHING_FACTOR = 0.9


class Sprite():
    colour: str
    polygon: list[vector2]
    is_hidden: bool
    canvas_object_ids: list

    def __init__(self, colour: str, polygon: list[vector2]) -> Self:
        self.colour = colour
        self.polygon = polygon
        self.is_hidden = False
        self.canvas_object_ids = []

    def cleanup(self, canvas: Canvas):
        for id in self.canvas_object_ids:
            canvas.delete(id)
        self.canvas_object_ids = []

    def draw(self, canvas: Canvas, offset: vector2):
        # I have no idea why
        # ```[offset + position for position in self.polygon]``` works
        # ```[position + offset for position in self.polygon]``` doesn't
        polygon = [offset + position for position in self.polygon]
        polygon = flatten([[x, y] for x, y in polygon])
        polygon = [int(x) for x in polygon]
        object_id = canvas.create_polygon(*polygon, fill=self.colour)
        self.canvas_object_ids.append(object_id)


class Plane():
    position: vector2
    velocity: vector2

    fall_amount: float
    sprites: list[Sprite]
    hitbox = PLANE_HITBOX

    def __init__(self):
        sprites = [
            Sprite(colour, [vector2(x, y) for x, y in plane_shape]) for colour, plane_shape in PLANE_SHAPES
        ]

        self.position = PLANE_START
        self.velocity = PLANE_VELOCITY
        self.fall_amount = PLANE_FALL_AMOUNT
        self.sprites = sprites.copy()

    def cleanup(self, canvas: Canvas):
        for sprite in self.sprites:
            sprite.cleanup(canvas)

    def draw(self, canvas: Canvas):
        for sprite in self.sprites:
            sprite.draw(canvas, self.position)


class Bomb():
    position: vector2
    velocity: vector2
    sprite: Sprite

    def __init__(self, position: vector2) -> Self:
        sprite = Sprite("black", BOMB_SHAPE)
        self.position = position
        self.velocity = BOMB_FALL_VELOCITY
        self.sprite = sprite

    def cleanup(self, canvas: Canvas):
        self.sprite.cleanup(canvas)

    def draw(self, canvas: Canvas):
        self.sprite.draw(canvas, self.position)


class Building():
    start_x: float
    width: float
    height: float
    sprite: Sprite

    def get_rect(start_x: float, width: float, height: float) -> list[vector2]:
        bl = vector2(start_x, CANVAS_HEIGHT)
        br = vector2(start_x + width, CANVAS_HEIGHT)
        tl = vector2(start_x, CANVAS_HEIGHT - height)
        tr = vector2(start_x + width, CANVAS_HEIGHT - height)
        rectangle = [tl, tr, br, bl]
        return rectangle

    def __init__(self, start_x: float, width: float, height: float):
        self.start_x = start_x
        self.width = width
        self.height = height

        rectangle = Building.get_rect(start_x, width, height)
        self.sprite = Sprite("brown", rectangle)

    def cleanup(self, canvas: Canvas):
        self.sprite.cleanup(canvas)

    def draw(self, canvas: Canvas):
        rectangle = Building.get_rect(self.start_x, self.width, self.height)
        self.sprite.polygon = rectangle
        self.sprite.draw(canvas, vector2(0, 0))

    def detect_collision(self, point: vector2) -> bool:
        """Checks if there is a point inside the building rectangle"""
        midpoint_x = self.start_x + self.width/2
        is_within_x = abs(midpoint_x - point.x) < self.width
        is_within_y = point.y > CANVAS_HEIGHT - self.height
        return is_within_x & is_within_y

    def is_destroyed(self):
        return self.height <= 0


def generate_buildings(num: int, width_multiplier: float) -> list[Building]:

    spacing = CANVAS_WIDTH // num
    width = spacing * width_multiplier
    buildings = []
    for i in range(0, num):
        start_x = i * spacing
        height = randint(MIN_BUILDING_HEIGHT, MAX_BUILDING_HEIGHT)
        building = Building(start_x, width, height)
        buildings.append(building)
    return buildings


class DisplayData(NamedTuple):
    """Used for the World class to commmunicate to the Display class"""
    game_over: bool
    plane_landed: bool
    small_text: str


class World():
    """Game logic goes here"""
    plane: Plane
    bombs: list[Bomb]
    buildings: list[Building]
    score: int
    level: int
    game_over: bool
    plane_landing: bool
    plane_landed: bool
    awaiting_new_level: bool

    def __init__(self):
        self.plane = Plane()
        self.bombs = []
        self.buildings = generate_buildings(
            TOTAL_BUILDINGS, BUILDING_WIDTH_MULTIPLIER)
        self.score = 0
        self.level = 1
        self.plane_landing = False
        self.plane_landed = False
        self.awaiting_new_level = False
        self.game_over = False

    def on_space_pressed(self):
        if self.plane_landing or self.game_over:
            return
        # if len(self.bombs) > 0:
        #     return
        bomb = Bomb(self.plane.position)
        self.bombs.append(bomb)

    def on_n_pressed(self):
        if self.plane_landed:
            self.awaiting_new_level = True

    def process(self, delta: float) -> DisplayData:
        self.plane.position += self.plane.velocity * delta

        if self.plane.position.x < -PLANE_WIDTH:
            new_x = CANVAS_WIDTH + PLANE_WIDTH
            new_y = self.plane.position.y + PLANE_FALL_AMOUNT
            self.plane.position = vector2(new_x, new_y)

        distance_from_ground = CANVAS_HEIGHT - \
            (self.plane.position + PLANE_BOTTOM).y

        if distance_from_ground < 0:
            self.plane.position += vector2(0, distance_from_ground)
            self.plane_landing = True
    

        if self.plane_landing and self.plane.position.x < CANVAS_WIDTH * 2/3:
            self.plane.velocity += vector2(0.04 * delta, 0)
            if self.plane.velocity.x > 0:
                self.plane.velocity *= 0
        self.plane_landed = self.plane.velocity.x == 0

        for bomb in self.bombs:
            bomb.position += bomb.velocity * delta

        deletion_queue = []
        for i, bomb in enumerate(self.bombs):
            for building in self.buildings:
                if building.detect_collision(bomb.position):
                    building.height -= HEIGHT_REMOVED_WHEN_BOMBED
                    self.score += BUILDING_DAMAGE_SCORE if building.height > 0 else BUILDING_DESTRUCTION_SCORE
                    deletion_queue.append(i)
            if bomb.position.y > CANVAS_HEIGHT:
                deletion_queue.append(i)

        self.buildings = [
            building for building in self.buildings if building.height > 0]

        self.bombs = [bomb for i, bomb in enumerate(
            self.bombs) if i not in deletion_queue]

        game_over = any([building.detect_collision(self.plane.position + offset)
                        for offset in self.plane.hitbox for building in self.buildings])

        if game_over:
            self.game_over = True
            self.plane.velocity = vector2(0, 0)
        # all([building.height <= 0 for building in self.buildings])

        if self.awaiting_new_level:
            self.plane = Plane()
            self.bombs = []
            self.level += 1
            new_total_buildings = TOTAL_BUILDINGS + (self.level - 1) * 2
            self.buildings = generate_buildings(
                new_total_buildings, BUILDING_WIDTH_MULTIPLIER)
            self.plane_landing = False
            self.plane_landed = False
            self.victory_lap = False
            self.game_over = False
            self.awaiting_new_level = False

        return DisplayData(
            game_over=game_over,
            plane_landed=self.plane_landed,
            small_text=f"Level: {self.level} Score: {self.score}"
        )

    def draw(self, canvas: Canvas):
        [building.draw(canvas) for building in self.buildings]
        [bomb.draw(canvas) for bomb in self.bombs]
        self.plane.draw(canvas)

    def cleanup(self, canvas: Canvas):
        [building.cleanup(canvas) for building in self.buildings]
        [bomb.cleanup(canvas) for bomb in self.bombs]
        self.plane.cleanup(canvas)


class Display(Frame):
    """Handles diplaying graphics"""

    def __init__(self, root):
        root.wm_title("Bomber")
        self.windowsystem = root.call('tk', 'windowingsystem')
        self.frame = root
        self.canvas = Canvas(self.frame, width=CANVAS_WIDTH,
                             height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=FALSE)
        self.init_fonts()
        self.init_score()
        self.rand = Random()

    def init_fonts(self):
        self.bigfont = font.nametofont("TkDefaultFont")
        self.bigfont.configure(size=48)
        self.scorefont = font.nametofont("TkDefaultFont")
        self.scorefont.configure(size=20)

    def init_score(self):
        self.score_text = self.canvas.create_text(5, 5, anchor="nw")
        self.canvas.itemconfig(
            self.score_text, text="Score:", font=self.scorefont)

    def display_score(self, text):
        self.canvas.itemconfig(self.score_text, text=text, font=self.scorefont)

    def game_over(self):
        self.text = self.canvas.create_text(
            CANVAS_WIDTH/2, CANVAS_HEIGHT/2, anchor="c")
        self.canvas.itemconfig(self.text, text="GAME OVER!", font=self.bigfont)

    def plane_landed(self):
        self.text = self.canvas.create_text(
            CANVAS_WIDTH/2, CANVAS_HEIGHT/2, anchor="c")
        self.canvas.itemconfig(self.text, text="SUCCESS!", font=self.bigfont)
        self.text2 = self.canvas.create_text(
            CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 100, anchor="c")
        self.canvas.itemconfig(
            self.text2, text="Press n for next level.", font=self.scorefont)

class Game():
    """Handles input and initialises tkinter"""

    def __init__(self):
        self.root = Tk()
        self.windowsystem = self.root.call('tk', 'windowingsystem')
        self.disp = Display(self.root)
        self.root.bind_all('<Key>', self.key)
        # added below line of code because chat-gpt told me so
        # It makes it so the game doesn't crash when you close the window my pressing the x button
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.update()
        self.is_running = True
        self.world = World()

    def quit(self):
        self.is_running = False

    def key(self, event):
        ''' key is called by tkinter whenever a key is pressed '''
        if event.char == 'q':
            self.quit()
        elif event.char == ' ':
            self.world.on_space_pressed()
        elif event.char == 'n':
            self.world.on_n_pressed()
        elif event.char == 'r':
            self.world.cleanup(self.disp.canvas)
            self.world = World()

    def run(self):
        while self.is_running:
            self.world.cleanup(self.disp.canvas)
            display_data = self.world.process(1)

            self.disp.display_score(display_data.small_text)
            if display_data.game_over:
                self.disp.game_over()
            elif display_data.plane_landed:
                self.disp.plane_landed()

            self.world.draw(self.disp.canvas)
            self.root.update()
        self.root.destroy()

game = Game()
game.run()