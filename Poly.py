import math
import random

from numpy import *
from numpy.linalg import *

import pygame
from pygame.locals import *

from shapely.geometry import Polygon

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
        orients = pygame.sprite.Group()
        shapes = pygame.sprite.Group()

        for n in range(3):
            point = pygame.sprite.Sprite()
            point.image = pygame.Surface((10,10))
            pygame.draw.circle(point.image, (255,0,0), (5,5), 5)

            # random location
            a = array([random.uniform(-1) for i in range(3)])
            point.p = a / norm(a)

            # best unit vector
            u = zeros(3)
            u[min(range(len(a)), key=lambda i: abs(point.p[i]))] = 1

            # random velocity vector
            v = cross(point.p, u)
            point.v = 0.01 * planet.rotate(v / norm(v), point.p,
                                           random.uniform(0, 2*math.pi))

            # random orienting point
            (o, ov) = planet.apply_velocity(point.p,
                                            0.05 * planet.rotate(v / norm(v),
                                                                 point.p,
                                                                 random.uniform(0, 2*math.pi)))
            point.o = pygame.sprite.Sprite()
            point.o.p = o
            point.o.image = pygame.Surface((6,6))
            pygame.draw.circle(point.o.image, (0,0,255), (3,3), 3)
            point.o.rect = pygame.Rect((0,0), point.o.image.get_size())
            orients.add(point.o)

            # polygon points
            point.shape = [(.1,.23),(.12,.43),(.13,.52),(.25,.54),
                           (.3,.43),(.43,.48),(.53,.31),(.48,.14),
                           (.5,.1)]
            
            point.rect = pygame.Rect((0,0), point.image.get_size())
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

            shapes.empty()
            for point in points:
                point.p, point.v = planet.apply_velocity(point.p, point.v)
                point.o.p, ov = planet.apply_velocity(point.o.p, point.v)
                point.rect.topleft = planet.vector_to_xy(point.p,
                                                         point.image.get_size())
                point.o.rect.topleft = planet.vector_to_xy(point.o.p,
                                                           point.o.image.get_size())

            points.clear(screen, background)
            orients.clear(screen, background)
            shapes.clear(screen, background)
            points.draw(screen)
            orients.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
