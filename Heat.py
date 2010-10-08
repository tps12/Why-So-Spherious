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
            pygame.draw.circle(point.image, (0,255,0), (5,5), 5)
            row = random.randint(1, planet.row_count-1)
            column = random.randint(0, planet.row_lengths[row]-1)
            point.raw_coords = planet.get_coordinates(row, column,
                                                      point.image.get_size())
            point.theta = random.uniform(0, 2 * math.pi)
            point.speed = 0
            point.rect = pygame.Rect(point.raw_coords, point.image.get_size())
            points.add(point)

        metapoints = pygame.sprite.Group()
        
        midpoint = pygame.sprite.Sprite()
        midpoint.image = pygame.Surface((10,10))
        pygame.draw.circle(midpoint.image, (0,0,255), (5,5), 5)
        midpoint.rect = pygame.Rect((0,0), midpoint.image.get_size())
        metapoints.add(midpoint)

        heatpoint = pygame.sprite.Sprite()
        heatpoint.image = pygame.Surface((10,10))
        pygame.draw.circle(heatpoint.image, (128,128,128), (5,5), 5)
        heatpoint.rect = pygame.Rect((0,0), heatpoint.image.get_size())
        heatpoint.inited = False
        heatpoint.speed = 0.001
        heatpoint.heat = 0
        metapoints.add(heatpoint)

        decay = 0.001

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

            # heat point starts out at initial midpoint
            if not heatpoint.inited:
                heatpoint.rect.topleft = midpoint.rect.topleft
                heatpoint.inited = True

            redraw = False
            if heatpoint.rect.topleft == midpoint.rect.topleft:
                if heatpoint.heat < 127:
                    heatpoint.heat = min(127, heatpoint.heat + 10)
                    redraw = True
            else:
                if heatpoint.heat > 0:
                    heatpoint.heat -= 1
                    redraw = True
                else:
                    heatpoint.rect.topleft = midpoint.rect.topleft

            if redraw:
                pygame.draw.circle(heatpoint.image, (128 + heatpoint.heat,
                                                     127 - heatpoint.heat,
                                                     127 - heatpoint.heat),
                                   (5,5), 5)

                
            for point in points:
                x, y = point.raw_coords

                if heatpoint.heat:
                    hp_theta = planet.xy_bearing(heatpoint.rect.left,
                                                 heatpoint.rect.top,
                                                 heatpoint.image.get_size(),
                                                 x, y, point.image.get_size())
                    d = planet.distance(heatpoint.rect.left,
                                        heatpoint.rect.top,
                                        heatpoint.image.get_size(),
                                        x, y, point.image.get_size())

                    impulse = heatpoint.heat * math.cos(d/2) / 128 / 10
                    if point.speed == 0:
                        point.speed = impulse
                        point.theta = hp_theta
                    else:
                        xs = (point.speed * math.cos(point.theta) +
                              impulse * math.cos(hp_theta))
                        ys = (point.speed * math.sin(point.theta) +
                              impulse * math.sin(hp_theta))
                        point.speed = min(1, math.sqrt(xs*xs + ys*ys))
                        point.theta = math.atan2(ys, xs)
                else:
                    if point.speed > 0:
                        point.speed = max(0, point.speed - decay)
                
                theta, x2, y2 = planet.apply_bearing(point.speed, point.theta,
                                                     x, y,
                                                     point.image.get_size())
                point.theta = theta
                point.raw_coords = x2,y2
                point.rect.topleft = point.raw_coords

            points.clear(screen, background)
            points.draw(screen)

            metapoints.clear(screen, background)
            metapoints.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
