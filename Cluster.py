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
            point.w = random.uniform(1,10)
            pygame.draw.circle(point.image, (255 - point.w*12,0,0), (5,5), 5)
            a = array([random.uniform(-0.1,0.1),
                       1,
                       random.uniform(-0.1,0.1)])
            point.p = a / norm(a)
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

            # join colliding points
            for point in points:
                for other in points:
                    if point == other:
                        continue
                    if math.acos(dot(point.p, other.p)) < 0.05:
                        d = other.p - point.p
                        if (abs(math.acos(dot(d, point.v))) < math.pi /2 and
                            abs(math.acos(dot(d, other.v))) > math.pi / 2):
                            point.p = array(planet.vector_weighted_average(
                                [point.p, other.p], [point.w, other.w]))
                            v = array(planet.vector_weighted_average(
                                [point.v, other.v], [point.w, other.w]))
                            point.v = (norm(point.v) + norm(other.v)) * v
                            point.w = point.w + other.w
                            pygame.draw.circle(point.image, (255 - point.w*12,0,0), (5,5), 5)
                            points.remove(other)

            # identify clusters of nearby points
            clusters = []
            for point in points:
                for other in points:
                    if point == other:
                        continue
                    if math.acos(dot(point.p, other.p)) < 0.5:
                        for c in clusters:
                            if point in c:
                                if not other in c:
                                    c.append(other)
                                break
                            elif other in c:
                                if not point in c:
                                    c.append(point)
                                break
                        else:
                            clusters.append([point, other])

            # repel clustered points from center of cluster
            midpoints.empty()
            seen = []
            for c in clusters:
                cluster = pygame.sprite.Sprite()
                cluster.image = pygame.Surface((10,10))
                pygame.draw.circle(cluster.image, (0,0,255), (5,5), 5)
                cluster.rect = pygame.Rect((0,0), cluster.image.get_size())
                p = planet.vector_weighted_average(
                    [point.p for point in c],
                    [1 for point in c])
                cluster.rect.topleft = planet.vector_to_xy(p,
                                                           cluster.image.get_size())
                midpoints.add(cluster)

                for point in c:
                    if norm(point.v) < 0.05:
                        point.v = 0.1 * planet.repel_from_point(point.p, p) / point.w
                    seen.append(point)

            # apply velocities 
            newpoints = []
            for point in points:
                # move or split isolated points
                if not point in seen:
                    if norm(point.v) < 0.05:
                        u = zeros(3)
                        u[min(range(len(a)), key=lambda i: abs(point.p[i]))] = 1
                        v = cross(point.p, u)
                        v = 0.01 * planet.rotate(v / norm(v), point.p,
                                                  random.uniform(0, 2*math.pi))
                        
                        if point.w < 0.25:
                            point.v = v / point.w
                        else:
                            point.w /= 2
                            point.v = v / point.w
                            
                            newpoint = pygame.sprite.Sprite()
                            newpoint.image = pygame.Surface((10,10))
                            row = random.randint(1, planet.row_count-1)
                            newpoint.w = point.w
                            pygame.draw.circle(point.image, (255 - point.w*12,0,0), (5,5), 5)
                            pygame.draw.circle(newpoint.image, (255 - newpoint.w*12,0,0), (5,5), 5)
                            newpoint.p = point.p
                            newpoint.v = -point.v
                            newpoint.rect = pygame.Rect((0,0), newpoint.image.get_size())
                            newpoints.append(newpoint)
                            
                point.p, point.v = planet.apply_velocity(point.p, point.v)
                if norm(point.v) < 0.001:
                    point.v = zeros(3)
                else:
                    point.v = 0.999 * point.v
                point.rect.topleft = planet.vector_to_xy(point.p,
                                                         point.image.get_size())

            points.add(newpoints)                

            # calculate overall midpoint
            midpoint.p = planet.vector_weighted_average(
                [point.p for point in points.sprites()],
                [point.w for point in points.sprites()])
            midpoint.rect.topleft = planet.vector_to_xy(midpoint.p,
                midpoint.image.get_size())

            midpoints.add(midpoint)

            points.clear(screen, background)
            points.draw(screen)

            midpoints.clear(screen, background)
            midpoints.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
