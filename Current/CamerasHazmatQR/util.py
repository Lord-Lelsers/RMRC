import time

class ViewMode:
    GRID = 0
    ZOOM = 1

    def __init__(self, start_mode = GRID):
        self.mode = start_mode
        self.zoom_on = -1

class Toggler:
    def __init__(self, start_state=False):
        self.state = start_state

    def toggle(self):
        self.state = not self.state

    def get(self):
        return self.state
    
    def __bool__(self):
        return self.state
    
    def __str__(self):
        return str(self.state)
    
class ToggleKey:
    def __init__(self, default = False):
        self.was_down = default

    def down(self, condition):
        if not self.was_down and condition:
            self.was_down = True
            return True
        elif not condition:
            self.was_down = False
        return False
    
class FPS:
    def __init__(self, start_delta = 1/30):
        self.t0 = time.time()
        self.t1 = time.time()
        self.delta = start_delta

    def update(self):
        self.t1 = time.time()
        self.delta = self.t1 - self.t0
        self.t0 = self.t1

        return self.delta
    
    def fps(self):
        if self.delta == 0:
            return -1
        else:
            return 1 / self.delta
        

def remove_dups(list, comp):
    new_list = []
    for item in list:
        if comp(item) not in [comp(x) for x in new_list]:
            new_list.append(item)
    return new_list

def removeSpecialCharacter(s):
    t = ""
    for i in s:
        if i >= 'A' and i <= 'Z' or i == " ":
            t += i
    return t