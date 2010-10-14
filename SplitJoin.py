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
            row = random.randint(1, planet.row_count-1)
            a = array([random.uniform(-1) for i in range(3)])
            point.w = random.uniform(1,10)
            pygame.draw.circle(point.image,
                               (0,255 - int(point.w*16),0),
                               (5,5), 5)
            point.p = a / norm(a)
            point.theta = 0 if n == 0 else random.uniform(0, 2 * math.pi)
            point.v = zeros(3)
            point.rect = pygame.Rect((0,0), point.image.get_size())
            points.add(point)

        midpoints = pygame.sprite.Group()
        midpoint = pygame.sprite.Sprite()
        midpoint.image = pygame.Surface((10,10))
        pygame.draw.circle(midpoint.image, (0,0,255), (5,5), 5)
        midpoint.rect = pygame.Rect((0,0), midpoint.image.get_size())

        heatpoint = pygame.sprite.Sprite()
        heatpoint.image = pygame.Surface((10,10))
        pygame.draw.circle(heatpoint.image, (255,0,0), (5,5), 5)
        heatpoint.rect = pygame.Rect((0,0), heatpoint.image.get_size())
        midpoints.add(heatpoint)
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
                [point.w for point in points.sprites()])
            midpoint.rect.topleft = planet.vector_to_xy(midpoint.p,
                midpoint.image.get_size())

            speed = sum([norm(p.v) for p in points])
            if speed < 0.05:
                heatpoint.p = midpoint.p
                heatpoint.rect.topleft = midpoint.rect.topleft
                
            for point in points:
                dist = math.acos(dot(heatpoint.p, point.p))
                decay = lambda dist: 0.01 * pow(dist - math.pi, 2)
                v = -planet.project_on_plane(heatpoint.p - point.p, point.p)
                point.v += decay(dist) * v / norm(v) / point.w
                point.p, point.v = planet.apply_velocity(point.p, point.v)
                point.v = 0.75 * point.v
                point.rect.topleft = planet.vector_to_xy(point.p,
                                                         point.image.get_size())

            merge = dict()
            for point in points:
                for other in points:
                    if point == other:
                        continue
                    if math.acos(dot(point.p, other.p)) < 0.05:
                        if other in merge:
                            merge[other].append(point)
                        else:
                            merge[point] = [other]

            newpoints = []
            seen = []
            for first,merging in merge.items():
                merging.append(first)
                for point in merging:
                    seen.append(point)
                    
                point = pygame.sprite.Sprite()
                point.image = pygame.Surface((10,10))
                point.w = sum([m.w for m in merging])/len(merging)
                pygame.draw.circle(point.image,
                                   (0,255 - int(point.w*16),0),
                                   (5,5), 5)
                point.p = array(planet.vector_weighted_average(
                    [m.p for m in merging],
                    [m.w for m in merging]))
                point.v = sum([m.v/m.w for m in merging])
                point.rect = pygame.Rect((0,0), point.image.get_size())
                newpoints.append(point)
            save = [p for p in points if not p in seen]
            points.empty()
            points.add(newpoints)
            points.add(save)

            points.clear(screen, background)
            points.draw(screen)

            midpoints.clear(screen, background)
            midpoints.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
