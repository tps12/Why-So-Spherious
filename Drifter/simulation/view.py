from display.button import Button
from display.flow import *
from display.screen import Screen

class View(object):
    def __init__(self):
        self._screen = Screen((800,600),
                              _('Why So Spherious: Tokyo Drift'),
                              _('Drifter'))

        self._controls = VerticalFlow()
        self._projection_buttons = HorizontalFlow()
        self._controls.add(self._projection_buttons)

        self._screen.add(self._controls)

        self.map_dragged = lambda start, end: None
        self.map_size_changed = lambda size: None

        self._controls.size_changed = lambda: self.map_size_changed(self.map_size)

        self._screen.dragged = lambda start, end: self.map_dragged(start, end)
        self._screen.size_changed = self._screen_size_changed

    @property
    def map_size(self):
        screen_size = self._screen.size
        return (screen_size[0] - self._controls.width, screen_size[1])

    def step(self, dots, shapes):
        return self._screen.step(dots, shapes)

    def fill_background_rows(self, color, rows):
        self._screen.fill_background_rows(color, rows)

    def draw_controls(self):
        self._screen.draw_controls()

    def paint_background(self):
        self._screen.paint_background()

    def _screen_size_changed(self, size):
        self.map_size_changed(self.map_size)

    def set_projection_options(self, projections, handler):
        for p in projections:
            def bind_handler(p):
                return lambda: handler(p)
            self._projection_buttons.add(Button(p.name, bind_handler(p)))
            
