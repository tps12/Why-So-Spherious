import pygame
from pygame import display, draw, event, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class Screen(object):
    def __init__(self, size, caption, icon_caption):
        pygame.init()
        display.set_caption(caption, icon_caption)
        self._make_screen(size)

        self._controls = []

        self._sprites = Group()

        self._drag_start = None
        self.dragged = lambda start, end: None
        self.size_changed = lambda size: None

    def _make_screen(self, size):
        self._screen = display.set_mode(size, HWSURFACE | RESIZABLE)

    @property
    def size(self):
        return self._screen.get_size()

    def step(self, dots, shapes):
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

        self._sprites.empty()

        for dot in dots:
            sprite = Sprite()
            sprite.image = pygame.Surface((2 * dot.radius, 2 * dot.radius),
                                          flags=SRCALPHA)
            draw.circle(sprite.image, dot.color,
                        (dot.radius,dot.radius), dot.radius)
            sprite.rect = Rect(tuple([int(c) - dot.radius for c in dot.location]),
                               sprite.image.get_size())
            self._sprites.add(sprite)

        for shape in shapes:
            sprite = Sprite()
            sprite.image = pygame.Surface((int(shape.width), int(shape.height)),
                                          flags=SRCALPHA)
            points = [tuple([int(c) for c in p]) for p in shape.points]
            if len(points) > 2:
                draw.polygon(sprite.image, shape.color, points)
            else:
                draw.lines(sprite.image, shape.color, False, points)
            sprite.rect = Rect(tuple([int(c) for c in shape.location]),
                               sprite.image.get_size())
            self._sprites.add(sprite)
        
        self._sprites.clear(self._screen, self._background)
        self._sprites.draw(self._screen)
        
        display.flip()

        return False

    def fill_background_rows(self, color, rows):
        self._background = Surface(self._screen.get_size())
        self._background.fill((128,128,128))
        
        for i in range(len(rows)):
            for start, length in rows[i]:
                self._background.fill(color, Rect(start, i, length, 1))

    def draw_controls(self):
        w, h = self.size
        dw = 0
        for c in self._controls:
            dw += c.width
            c.draw(self._background.subsurface(Rect(w - dw, 0, c.width, h)))

    def paint_background(self):
        self._screen.blit(self._background, (0,0))
            
    def add(self, control):
        self._controls.append(control)
