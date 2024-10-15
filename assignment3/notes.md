# Notes

Lets dissect this program to see how it works. 

## fr_controller.py

The name of the program is probably sort for "frog controller". 

Everything here is in the class ```Controller```. 

```python
def __init__(self):
    self.root = Tk();
    self.windowsystem = self.root.call('tk', 'windowingsystem')
    self.views = []
    self.root.bind_all('<Key>', self.key)
    self.running = True
    self.score = -1
    self.level = -1
    self.river_objects = []
    self.cars = []
    self.model = Model(self);
    self.add_view(View(self.root, self))
    self.model.activate()
```

It defines a bunch of variables.
1. views
2. running
3. score
4. level
5. river_objects
6. cars
7. model

I don't really understand what a view is, or what is going on here. 

According to the tkinter documentation:
> Construct a frame widget with the parent MASTER.
> Valid resource names: background, bd, bg, borderwidth, class, colormap, container, cursor, height, highlightbackground, highlightcolor, highlightthickness, relief, takefocus, visual, width.

The class ```Model``` is defined in the ```fr_model.py```

This function is called exactly once at the start. 

```python
def add_view(self, view):
    self.views.append(view)
    view.register_frog(self.frog)
    for obj in self.river_objects:
        view.register_river_object(obj)
    for car in self.cars:
        view.register_car(car)
```

These functions are never called within this class:
- ```register_frog(self, frog)```
- ```register_car(self, car)```
- ```register_river_object(self, river_object)```
- ```unregister_objects(self)```


```python
def key(self, event):
        if event.char == 'a' or event.keysym == 'Left':
            self.model.move_frog(Direction.LEFT)
        elif event.char == 's' or event.keysym == 'Up':
            self.model.move_frog(Direction.UP)
        elif event.char == 'd' or event.keysym == 'Down':
            self.model.move_frog(Direction.DOWN)
        elif event.char == 'f' or event.keysym == 'Right':
            self.model.move_frog(Direction.RIGHT)
        elif event.char == 'q':
            self.running = False
        elif event.char == 'r':
            for view in self.views:
                view.clear_messages()
            self.model.restart()
```

This is familiar to me: on the previous project, we saw that the ```key``` function is called automatically by tkinter. 

```python
def run(self):
        i = 0
        last_time = time.time()
        while self.running:
            self.model.update()
            for view in self.views:
                view.update()
            self.root.update()
            i = i + 1
            if i == 60:
                t = time.time()
                elapsed = t - last_time
                last_time = t
                fps = 60/elapsed
                i = 0;
        self.root.destroy()
```

I think I sort of get what is going on here now. 

1. All the game logic is done by ```self.model.update()```
2. The ```key(self, event)``` calls special functions within the ```self.model``` corresponding to each of the keys pressed
3. After ```self.model.update()``` is called, the sprites of each of the game objects are updated

## fr_model.py

```python
def __init__(self, controller):
        self.controller = controller
        self.lives = 7
        self.end_time = time.time() + LEVEL_TIME
        self.init_score()
        self.rand = Random()

        #create game objects
        self.frog = Frog(CANVAS_WIDTH//2, GRID_SIZE*15)
        controller.register_frog(self.frog)
        self.logs = []
        self.cars = []
        self.create_logs()
        self.create_cars()
        self.create_homes()
        self.game_running = True
        self.paused = False
        self.won = False

        # initialized speed measurement (see checkspeed for use)
        self.lastframe = time.time()
        self.framecount = 0
        self.dont_update_speed = True
```

```python
def update(self):
    if self.game_running and not self.paused:
        self.move_objects()
        self.controller.update_score(self.score)
        self.check_frog()
        self.checkspeed()
    elif self.paused:
        self.check_pause()
```

This makes enough sense. 

