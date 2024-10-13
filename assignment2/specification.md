
# Documentation

## Specification for the bomber game

My goal here is to find a list of bugs, and fix them. But how do we know what counts as a bug? You first need to know how the game is originally meant to function, before you can begin trying to fix it. 

However, the provided information is a bit lacking:


> The objective of the game is to level the city by dropping bombs on the buildings so you can land the plane. The plane gets lower each time it crosses the screen. If you fly into a building, you die. If you succeed in flattening all the buildings, you can land the plane and score 1000 points. Your reward is to start all over again, but with narrower buildings that are harder to hit

So I decided it was necessary to do some additional research. 

### Research I did

I looked 
[here](https://www.sinclairzxworld.com/viewtopic.php?t=5160)
and
[here](https://www.youtube.com/watch?v=Jpn6iLa1QlI).
The versions of the game all seem to be very different to the one we were given in the assigment, so I don't think this is really worth looking into. 

### Looking at the code

I think it would be more practical to try and examine the code to see how the game looks like its meant to run. Which is not the best solution, but its better than nothing. 

I'm primarily going to be looking at the OO version, since it should be the easiest to work with. 

Lets start by looking at the constants:

*From line 8:*

``` python
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700
SPACING = 100
```

I assume everything is measured in pixels? CANVAS_WIDTH and CANVAS_HEIGHT are pretty self-explanatory. 

I think spacing refers to the spacing between buildings. I'm going to look at all instances of where SPACING is using in the program. 

#### What does SPACING do?

*From line 64:*

``` python
class Building():
    def __init__(self, canvas, building_num, height, width):
        self.canvas = canvas
        self.height = height
        self.x = building_num*SPACING
        self.width = width
        self.main_rect = canvas.create_rectangle(self.x, CANVAS_HEIGHT, self.x + self.width, CANVAS_HEIGHT-self.height, fill="brown")

```

*From line 198:*

``` python
#create game objects
self.plane = Plane(self.canvas, CANVAS_WIDTH - 100, 0)
self.bomb = Bomb(self.canvas)
self.buildings = []
self.building_width = SPACING * 0.8
self.create_buildings()
self.game_running = True
self.won = False
```

*From line 226:*

``` python
#create the new ones
for building_num in range(0, 1200//SPACING):
    height = self.rand.randint(10,500) #random number between 10 and 500
    self.buildings.append(Building(self.canvas, building_num, height,
                                   self.building_width))
```

*From line 288:*

``` python
def restart(self):
    self.canvas.delete(self.text)
    self.level = 1
    self.score = 0
    self.plane.reset_position()
    self.building_width = SPACING * 0.8
    self.create_buildings()
    self.won = False
    self.game_running = True
```

I think that spacing does several different things. 

1. It is the spacing between buildings
2. It determines the total number of buildings, calculated by ```1200//SPACING```
3. It determines the width of buildings, calculated by ```SPACING * 0.8```

This is a really strange way to do things in my opinion. 

#### The main game loop

``` python
def run(self):
    while self.running:
        self.disp.update()
        self.root.update()
        self.checkspeed()
    self.root.destroy()
```

From the names I alone can't really tell what each of the things do. But I do know that ```self.root.update()``` does something mysterious I don't need to worry about since it just leads me to some tkinter library code.

```self.root.destroy()``` is self-explanatory. 

#### checkspeed

```python
''' adjust game speed so it's more or less the same on different machines '''
def checkspeed(self):
    global speed
    self.framecount = self.framecount + 1
    # only check every ten frames
    if self.framecount == 10:
        now = time()
        elapsed = now - self.lastframe
        # speed will be 1.0 if we're achieving 60 fps
        if speed == 0:
            #initial speed value
            # At 60fps, 10 frames take 1/6 of a second.
            speed = 6 * elapsed
        else:
            # use an EWMA to damp speed changes and avoid excessive jitter
            speed = speed * 0.9 + 0.1 * 6 * elapsed
        self.lastframe = now
        self.framecount = 0
```

The code increases the framecount each time its called. Then, once every 10 frames, it does something. 

```python
# use an EWMA to damp speed changes and avoid excessive jitter
    speed = speed * 0.9 + 0.1 * 6 * elapsed
```

I think I found what
[EWMA](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average)
stands for. 
I still not sure what exactly this code is trying to do though. 

Speed is a global variable. It seems it is meant to be some sort of measure of framerate. 

```python
if speed == 0:
    #initial speed value
    # At 60fps, 10 frames take 1/6 of a second.
    speed = 6 * elapsed
```

I remember seeing that speed is declared at the start to be exactly zero. 
So it seems the code ```speed = 6 * elapsed``` is meant to be run exactly once. 
I think I now know what is going on here:

1. For 10 frames, speed is 0 and so the game is effectively paused
2. The game uses the time elapsed since it started counting to determine your computer's framerate. 
It uses this to calibrate the speed the game is running at. 
3. For every subsequent 10 frames, it calcuates an exponential moving average with a smoothing factor of 0.9


Speed has a value of 1 when the computer is running at 60fps, and the speed is higher the longer between each frame. 

I think I'm going to stop here for now. I'm going to continue looking through the code without writing any additional comments since I think this is easy enough to understand by itself. 

## Refactoring the code

There are alot of unnamed numerical constants in this program. I really want to fix these before I do anything else. 

There are also many parts of this code which are written in an inconsistent manner, e.g.
- Sometimes it uses separate x and y co-ordinates, sometimes points
- Speed is a global variable, but everything else is a property of the ```Game``` object
- The plane ```plane.move()``` method returns a score
- ```display.check_plane()``` and ```display.check_bomb()``` doesn't tell you if the plane or bomb has collided or not, it just does unexplained stuff in the background
- There is a variable named ```display.is_running``` and ```game.running``` which is slightly confusing and unclear as to what each of them do (```display.is_running``` freezes the game)
- The ```game.running``` state only occurs when the program stops running, at which point there is no point of it being a state at all
- same problem with ```display.won```: it is read exactly once, at which point it is immediately changed to false

```python
''' restart is called after game over to start a new game '''
def restart(self):
    self.canvas.delete(self.text)
    self.level = 1
    self.score = 0
    self.plane.reset_position()
    self.building_width = INITIAL_BUILDING_WIDTH
    self.create_buildings()
    self.won = False
    self.game_running = True
```

```python
def next_level(self):
    #don't move to next level unless we've actually won!
    if self.won == False:
        return
    
    self.level = self.level + 1
    self.canvas.delete(self.text)
    self.canvas.delete(self.text2)
    self.plane.reset_position()
    # buildings get narrower with each level
    self.building_width = self.building_width * BUILDING_WIDTH_MULTIPLIER
    self.create_buildings()
    self.won = False
    self.game_running = True
```

- The ```display.restart()```, ```display.next_level()``` and ```Display(Frame)``` all share duplicated code

```python
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700
SPACING_BETWEEN_BUILDINGS = 100

INITIAL_BUILDING_WIDTH = 0.8 * SPACING_BETWEEN_BUILDINGS
TOTAL_BUILDINGS = 1200//SPACING_BETWEEN_BUILDINGS

MIN_BUILDING_HEIGHT = 10
MAX_BUILDING_HEIGHT = 500
BUILDING_WIDTH_MULTIPLIER = 0.9

HEIGHT_REMOVED_WHEN_BOMBED = 50
BOMB_FALL_VELOCITY_Y = 8

PLANE_MOVE_VELOCITY_X = -4
PLANE_MOVE_HEIGHT = 40
POINTS_EACH_TIME_THE_PLANE_MOVES_DOWN = 10
WIN_SCORE_BONUS = 1000

FRAMES_PER_CALIBRATION = 10
STANDARD_FRAMES_PER_SECOND = 60
SPEED_CALIBRATION_CONSTANT = STANDARD_FRAMES_PER_SECOND / FRAMES_PER_CALIBRATION 
EXPONENTIAL_SMOOTHING_FACTOR = 0.9

BOMB_SHAPE = [0,0, 10,0, 5,5, 10,10, 10,20, 5,22, 0,20, 0,10, 5,5]

PLANE_BODY_SHAPE = [0,28, 20,16, 120,16, 94,32, 12,32]
PLANE_WING1_SHAPE = [40,28, 76,28, 94,48, 80,48]
PLANE_WING2_SHAPE = [52,16, 78,8, 94,8, 81,16]
PLANE_TAIL_SHAPE = [90,16, 110,0, 124,0, 116,16]
PLANE_WIDTH = 124

PLANE_START_Y = 0
PLANE_START_X = CANVAS_WIDTH - 100

PLANE_NOSE_X = 0
PLANE_NOSE_Y = 28
PLANE_BOTTOM_X = 12
PLANE_BOTTOM_Y = 32
PLANE_WING_X = 94
PLANE_WING_Y = 48
PLANE_LANDING_HEIGHT = 20

STARTING_SPEED = 0.0
```

## I actually just give up, I'm just re-writing the code from scratch

Ok, time to explain from my understanding how the game works. 

1. The canvas is 1000x700 pixels big
2. The plane spawns at a co-ordinate of (900, 0)
3. At 60fps, the plane moves at -4 pixels per frame
4. The plane moves 40 pixels down when the entire width of the plane leaves the canvas
5. The bomb is dropped from the centre of the plane by pressing space. It can only be dropped when a bomb is not currently falling
6. The bomb explodes if the centre of the bomb goes inside the building
7. At 60fps, the bomb falls at 8 pixels per frame
8. There are 12 buildings
9. The height of each building in pixels is determined by ```randint(10,500)```
10. The start of each building is spaced apart by 100 pixels
11. Each building has a width of 80 pixels
12. When the bomb hits a building, its height is reduced by 50 pixels
13. The game pauses when you win or game over
14. You can press 'r' to restart
15. You can press 'q' to quit the game
16. You win when the plane sucessfully lands: when the bottom of the plane touches the ground
17. When you win, you move onto the next level which is identical except that buildings are 0.9 times as wide
18. You earn 10 points each time the plane moves down
19. You earn 1000 each level you complete