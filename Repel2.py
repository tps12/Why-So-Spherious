import math
import random

from numpy import *
from numpy.linalg import *

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

        for n in range(20):
            point = pygame.sprite.Sprite()
            point.image = pygame.Surface((10,10))
            pygame.draw.circle(point.image, (255,0,0), (5,5), 5)
            row = random.randint(1, planet.row_count-1)
            a = array([random.uniform(-1) for i in range(3)])
            point.p = a / norm(a)
            point.theta = 0 if n == 0 else random.uniform(0, 2 * math.pi)
            point.v = zeros(3)
            point.rect = pygame.Rect((0,0), point.image.get_size())
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

            midpoint.p = planet.vector_weighted_average(
                [point.p for point in points.sprites()],
                [1 for point in points.sprites()])
            midpoint.rect.topleft = planet.vector_to_xy(midpoint.p,
                midpoint.image.get_size())

            speed = sum([norm(p.v) for p in points])
            for point in points:
                diff = midpoint.p - point.p
                dist = math.acos(dot(midpoint.p, point.p))
                if not speed:
                    point.v = 0.1 * (math.pi - dist) * (dot(diff, point.p) * point.p - diff)
                point.p, point.v = planet.apply_velocity(point.p, point.v)
                if norm(point.v) < 0.001:
                    point.v = zeros(3)
                else:
                    point.v = 0.9 * point.v
                point.rect.topleft = planet.vector_to_xy(point.p,
                                                         point.image.get_size())

            points.clear(screen, background)
            points.draw(screen)

            midpoints.clear(screen, background)
            midpoints.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
