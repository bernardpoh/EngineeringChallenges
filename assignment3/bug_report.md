# 1 You die when you go on the turtles

Fix: changed all occurences of ```on_long``` to ```on_log``` in *fr_model.py*


# 2 When you die, you respawn in the same position

Fix: added new line which sends the frog back to the original position on a new life

*fr_model.py, Model*
```python
def new_life(self):
        self.frog.x, self.frog.y = self.frog.start_position
        self.controller.update_lives(self.lives)
```

# 3 After losing all lives, the skull still changes to a normal frog after 1 second

Fix:
Made it such that the frog no longer undergoes the death animation when losing the last life.  (It would've taken too much effort to make the frog just die permanently)

*fr_model.py, Model*
```python
def died(self):
        self.lives = self.lives - 1
        if self.lives == 0:
            self.game_over()
        else:
            self.controller.died()
            self.pause_start(1, "self.new_life()")
```

# 4 Python throws an exception when you close the window manually

Fix: Added this code

*fr_controller.py, Controller*
```python
def quit(self):
        self.running = False
```


*fr_controller.py, Controller.\__init__*
```python
self.root.protocol("WM_DELETE_WINDOW", self.quit)
```

# 5 You can move below the screen

Fix: you now die when you go below the screen

```python
def check_frog(self):
        if self.frog.moving:
            self.frog.finish_move()
            return
        
        (x, y) = self.frog.get_position()
        if x < 0 or x > CANVAS_WIDTH or y > CANVAS_HEIGHT:
            self.died()
            return
```

# 6 You die upon entering the leftmost frog home

Fix: changed Controller.create_homes() so the x values are added correctly, instead of missing out the first one

*fr_model.py, Model*
```python
    def create_homes(self):
        # init where the frog homes are at the top of the screen
        self.frogs_home = 0
        self.homes_x = []
        self.homes_occupied = []
        spacing = (CANVAS_WIDTH - GRID_SIZE*5)//5
        # the left hand home has centre position of spacing/2 (green to
        # the left of the home) + GRID_SIZE/2 (to get the centre of the
        # grid square)
        x = (spacing + GRID_SIZE)//2
        for i in range(0,6):
	    self.homes_x.append(x)
            x = x + GRID_SIZE + spacing
            self.homes_occupied.append(False)
```

# 7 You can't win the game

Fix: There are an incorrect number of frog homes generated at the start of the game. 

Change all occurences of "6" to "5" in *fr_model.py*

# 8 The turtle sprites are misaligned by 1 tile to the left

Fix: added line of code ```i += 1``` to shift sprites by 1 to the right

*fr_view.py, TurtleView*
```python
def draw(self):
        width = self.turtle.get_width()
        self.pngnum = 1 - self.pngnum #alternate images
        (x,y) = self.turtle.get_position()
        self.moveto(0, 0)
        for i in range(0, width//GRID_SIZE):
            i += 1
            image = self.canvas.create_image(i * GRID_SIZE, 0, image=self.pngs[self.pngnum], anchor="c")
            self.items.append(image)
        self.moveto(x, y)
```

# 9 The timer doesn't display properly

Fix: changed line of code displaying bar so that the bar is filled a fraction of the remaining time

*fr_view.py*
```python
from fr_model import LEVEL_TIME
```

*fr_view.py, TimeView*
```python
def update(self, time_now):
        remaining = self.end_time - time_now
        print(remaining)
        if remaining > 0:
            self.canvas.delete(self.bar)
            self.bar = self.canvas.create_rectangle((CANVAS_WIDTH - 100) * (1-remaining/LEVEL_TIME), GRID_SIZE*16.25,
                                               CANVAS_WIDTH - 100, GRID_SIZE*16.75, fill="green")
```

# 10 Sprites can briefly be seen on the top left corner of the screen if you repeatedly press 'r' fast enough

Fix: this is not a bug worth fixing

