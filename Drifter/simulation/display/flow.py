from pygame import Rect

class VerticalFlow(object):
    def __init__(self):
        self.size_changed = lambda: None
        self._controls = []
        self.width = self.height = 0
        
    def add(self, control):
        self._controls.append(control)
        control.size_changed = self._control_size_changed
        self._control_size_changed()
        
    def draw(self, surface):
        h = 0
        for c in self._controls:
            c.draw(surface.subsurface(Rect(0, h, c.width, c.height)))
            h += c.height

    def click(self, location):
        h = 0
        for c in self._controls:
            if 0 <= location[0] < c.width and h <= location[1] < h + c.height:
                c.click((location[0], location[1] - h))
                break
            h += c.height

    def _control_size_changed(self):
        self.height = sum([c.height for c in self._controls])
        self.width = max([c.width for c in self._controls])
        self.size_changed()

class HorizontalFlow(object):
    def __init__(self):
        self.size_changed = lambda: None
        self._controls = []
        self.width = self.height = 0
        
    def add(self, control):
        self._controls.append(control)
        control.size_changed = self._control_size_changed
        self._control_size_changed()
        
    def draw(self, surface):
        w = 0
        for c in self._controls:
            c.draw(surface.subsurface(Rect(w, 0, c.width, c.height)))
            w += c.width

    def click(self, location):
        w = 0
        for c in self._controls:
            if w <= location[0] < w + c.width and 0 <= location[1] < c.height:
                c.click((location[0] - w, location[1]))
                break
            w += c.width

    def _control_size_changed(self):
        self.height = max([c.height for c in self._controls])
        self.width = sum([c.width for c in self._controls])
        self.size_changed()
