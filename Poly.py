import math
import random

from numpy import *
from numpy.linalg import *

import pygame
from pygame.locals import *

from shapely.geometry import Polygon

from Planet import Planet

def offset(p, dx, dy):
    x,y = p
    return x + dx, y + dy

def rotate(p, loc, th):
    x,y = [p[i]-loc[i] for i in range(2)]
    s,c = sin(th),cos(th)
    return x*c - y*s + loc[0], x*s + y*c + loc[1]

def defloat(p):
    x,y = p
    return int(x+0.5), int(y+0.5)

def ranges(ps):
    return [[f([p[i] for p in ps])
             for i in range(2)]
            for f in (min,max)]

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

        def add_shape_coords(coords, cmin, cmax, px, py):
            sprite = pygame.sprite.Sprite()
            sprite.image = pygame.Surface((cmax[0]-cmin[0],cmax[1]-cmin[1]))
            pygame.draw.polygon(sprite.image, (0,255,0),
                                [(c[0]-cmin[0], c[1]-cmin[1])
                                 for c in coords], 1)
            sprite.rect = pygame.Rect((px-sprite.image.get_width()/2,
                                       py-sprite.image.get_height()/2),
                                      sprite.image.get_size())
            shapes.add(sprite)

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

                shape = Polygon(point.shape)
                c = shape.centroid.coords[0]

                coords = []
                for vertex in point.shape:
                    # find distance from centroid
                    d = math.sqrt(sum([(vertex[i]-c[i])*(vertex[i]-c[i])
                                       for i in range(2)]))
                    # find angle from local north
                    th = math.atan2(vertex[0]-c[0],vertex[1]-c[1])

                    # axis of rotation separating point from orientation point
                    u = cross(point.p, point.o.p)
                    u = u / norm(u)

                    # rotate point around it by d
                    p = planet.rotate(point.p, u, d)

                    # and then around point by -theta
                    p = planet.rotate(p, point.p, -th)

                    coords.append(planet.vector_to_xy(p))

                cmin, cmax = ranges(coords)
                px,py = planet.vector_to_xy(point.p)
                inproj = [planet.in_projection(px+x-(cmin[0]+cmax[0])/2,
                                               py+y-(cmin[1]+cmax[1])/2)
                          for (x,y) in coords]
                if all(inproj):
                    add_shape_coords(coords, cmin, cmax, px, py)
                else:
                    left = []
                    right = []
                    for c in coords:
                        (left if c[0] < planet.max_row/2 else right).append(c)
                    if (len(left) > 1):
                        cmin, cmax = ranges(left)
                        add_shape_coords(left, cmin, cmax, px, py)
                    if (len(right) > 1):
                        cmin, cmax = ranges(right)
                        add_shape_coords(right, cmin, cmax, px, py)

            points.clear(screen, background)
            orients.clear(screen, background)
            shapes.clear(screen, background)
            shapes.draw(screen)
            points.draw(screen)
            orients.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
