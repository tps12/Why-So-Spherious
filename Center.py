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

        for n in range(2):
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

        midpoints = pygame.sprite.Group()
        midpoint = pygame.sprite.Sprite()
        midpoint.image = pygame.Surface((10,10))
        pygame.draw.circle(midpoint.image, (0,255,0), (5,5), 5)
        midpoint.rect = pygame.Rect((0,0), midpoint.image.get_size())
        midpoints.add(midpoint)

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
                theta, x2, y2 = planet.apply_bearing(0.1, point.theta, x, y,
                                                     point.image.get_size())
                point.theta = theta
                point.raw_coords = x2,y2
                point.rect.topleft = point.raw_coords

            for i in range(len(midpoints.sprites())):
                x1,y1 = points.sprites()[2*i].raw_coords
                x2,y2 = points.sprites()[2*i+1].raw_coords
                midpoints.sprites()[i].rect.topleft = planet.weighted_average(
                    [(x1,y1),(x2,y2)], [1,1],
                    [points.sprites()[2*i].image.get_size(),
                     points.sprites()[2*i+1].image.get_size()],
                    midpoints.sprites()[i].image.get_size())

            points.clear(screen, background)
            points.draw(screen)

            midpoints.clear(screen, background)
            midpoints.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
