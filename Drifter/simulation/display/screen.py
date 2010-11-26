import pygame
from pygame import display, draw, event, mouse, Rect, Surface
from pygame.locals import *

class Screen(object):
    def __init__(self, size, caption, icon_caption):
        pygame.init()
        display.set_caption(caption, icon_caption)
        self._make_screen(size)

        self._controls = []

        self._drag_start = None
        self.dragged = lambda start, end: None
        self.size_changed = lambda size: None

    def _make_screen(self, size):
        self._screen = display.set_mode(size, HWSURFACE | RESIZABLE)

    @property
    def size(self):
        return self._screen.get_size()

    def step(self):
        for e in event.get():
            if e.type == QUIT:
                return True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return True
            elif e.type == VIDEORESIZE:
                self._make_screen(e.size)
                self.size_changed(self.size)
            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                self._drag_start = mouse.get_pos()
            elif e.type == MOUSEMOTION and 1 in e.buttons:
                if self._drag_start is not None:
                    p = mouse.get_pos()
                    if p != self._drag_start:
                        self.dragged(self._drag_start, p)
                        self._drag_start = p
            elif e.type == MOUSEBUTTONUP and e.button == 1:
                self._drag_start = None

                p = mouse.get_pos()
                w, h = self.size
                dw = 0
                for c in self._controls:
                    dw += c.width
                    if w - dw <= p[0] < w - dw + c.width:
                        c.click((p[0] - (w - dw), p[1]))
                        break

        self._screen.blit(self._background, (0,0))
        display.flip()

        return False

    def fill_background_rows(self, color, rows):
        self._background = Surface(self._screen.get_size())
        self._background.fill((128,128,128))
        
        for i in range(len(rows)):
            for start, length in rows[i]:
                self._background.fill(color, Rect(start, i, length, 1))

    def draw_dot(self, color, location):
        draw.circle(self._background, color,
                    tuple([int(c) for c in location]), 3)

    def draw_controls(self):
        w, h = self.size
        dw = 0
        for c in self._controls:
            dw += c.width
            c.draw(self._background.subsurface(Rect(w - dw, 0, c.width, h)))
            
    def add(self, control):
        self._controls.append(control)
