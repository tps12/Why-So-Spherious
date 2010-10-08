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

        for n in range(10):
            point = pygame.sprite.Sprite()
            point.image = pygame.Surface((10,10))
            pygame.draw.circle(point.image, (255,0,0), (5,5), 5)
            row = random.randint(1, planet.row_count-1)
            column = random.randint(0, planet.row_lengths[row]-1)
            point.raw_coords = planet.get_coordinates(row, column,
                                                      point.image.get_size())
            point.theta = random.uniform(0, 2 * math.pi)
            point.speed = 0
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

            midpoint.rect.topleft = planet.weighted_average(
                [s.raw_coords for s in points.sprites()],
                [1 for s in points.sprites()],
                [s.image.get_size() for s in points.sprites()],
                midpoint.image.get_size())
                        
            for point in points:
                x, y = point.raw_coords

                mp_theta = planet.xy_bearing(midpoint.rect.left,
                                             midpoint.rect.top,
                                             midpoint.image.get_size(),
                                             x, y, point.image.get_size())
                if point.speed == 0:
                    point.speed = 0.001
                    point.theta = mp_theta
                else:
                    d = planet.distance(midpoint.rect.left,
                                        midpoint.rect.top,
                                        midpoint.image.get_size(),
                                        x, y, point.image.get_size())
                    xs = (point.speed * math.cos(point.theta) +
                          0.001 * math.cos(d/2) * math.cos(mp_theta))
                    ys = (point.speed * math.sin(point.theta) +
                          0.001 * math.cos(d/2) * math.sin(mp_theta))
                    point.speed = min(1, math.sqrt(xs*xs + ys*ys))
                    point.theta = math.atan2(ys, xs)
                
                theta, x2, y2 = planet.apply_bearing(point.speed, point.theta,
                                                     x, y,
                                                     point.image.get_size())
                point.theta = theta
                point.raw_coords = x2,y2
                point.rect.topleft = point.raw_coords

            points.clear(screen, background)
            points.draw(screen)

            midpoints.clear(screen, background)
            midpoints.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
