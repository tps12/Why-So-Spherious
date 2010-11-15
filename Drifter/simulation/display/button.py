from pygame import draw
from pygame.font import *

class Button(object):
    def __init__(self, text, click):
        self._image = Font(get_default_font(), 10).render(text, 1, (0,0,0))
        self.width, self.height = self._image.get_size()
        self._click = click

    def draw(self, surface):
        surface.fill((255,255,255), self._image.get_rect())
        surface.blit(self._image, (0,0))
