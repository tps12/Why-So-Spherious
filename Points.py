import math
import random

import pygame
from pygame.locals import *

from Planet import Planet

class Display:

    def main_loop(self):

        planet = Planet(100,1,0)

        pygame.init()    

        screen = pygame.display.set_mode((planet.max_row,planet.row_count),
                                         HWSURFACE)
        pygame.display.set_caption('Planet')

        background = pygame.Surface(screen.get_size())
        background.fill((128,128,128))

        def in_bounds(x,y):
            return (x > planet.row_offsets[y] and
                    x < planet.row_offsets[y] + planet.row_lengths[y])

        background.lock()
        for y in range(0, screen.get_height()):
            for x in range(0, screen.get_width()):
                if in_bounds(x,y):
                    value = planet.rows[y][x - planet.row_offsets[y]]
                    background.set_at((x,y),(value,value,value))
        background.unlock()

        screen.blit(background, (0,0))

        points = pygame.sprite.Group()

        for n in range(5):
            point = pygame.sprite.Sprite()
            point.image = pygame.Surface((10,10))
            pygame.draw.circle(point.image, (255,0,0), (5,5), 5)
            row = random.randint(1, planet.row_count-1)
            column = random.randint(0, planet.row_lengths[row]-1)
            point.raw_coords = planet.get_coordinates(row, column,
                                                      point.image.get_size())
            point.theta = random.uniform(0, 2 * math.pi)
            point.rect = pygame.Rect(point.raw_coords, point.image.get_size())
            points.add(point)

        limit = pygame.time.Clock()

        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        done = True
                        
            for point in points:
                x, y = point.raw_coords
                theta, x, y = planet.apply_heading(0.25, point.theta, x, y,
                                                   point.image.get_size())
                point.theta = theta
                point.raw_coords = x,y
                point.rect.topleft = point.raw_coords

            points.clear(screen, background)
            points.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
