from shapely.geometry import Point, Polygon

from math import *

import pygame
from pygame import display, draw, event, mouse, Surface
from pygame.locals import *

pygame.init()

screen = display.set_mode((800,600),HWSURFACE)
display.set_caption('Polygons')

class Poly:
    def __init__(self, points, position, orientation):
        self.points = points
        self.position = position
        self.orientation = orientation

polys = [Poly(points, (1,1), 0) for points in
         [(.1,.23),(.12,.43),(.13,.52),(.25,.54),
          (.3,.43),(.43,.48),(.53,.31),(.48,.14),
          (.5,.1)],
         [(.14,.4),(.19,.6),(.43,.63),(.34,.5),
          (.48,.37),(.27,.24),(.23,.1),(.04,.13),
          (.06,.19),(.17,.26),(.21,.3)]]

polys[0].position = (1.2, 1.1)
polys[1].orientation = pi/2

def offset(p, dx, dy):
    x,y = p
    return x + dx, y + dy

def scale(p):
    scale = 300
    offset = 500
    x,y = p
    return scale*x,offset-scale*y

def unscale(p):
    scale = 300.0
    offset = 500.0
    x,y = p
    return x/scale,(offset-y)/scale

def rotate(p, loc, th):
    x,y = [p[i]-loc[i] for i in range(2)]
    s,c = sin(th),cos(th)
    return x*c - y*s + loc[0], x*s + y*c + loc[1]

def defloat(p):
    x,y = p
    return int(x+0.5), int(y+0.5)

def draw_poly(poly):
    polygon = Polygon(poly.points)
    if poly.orientation:
        c = polygon.centroid.coords[0]
        polygon = Polygon([rotate(p, c, -poly.orientation)
                           for p in polygon.exterior.coords])
    c = polygon.centroid.coords[0]
    p = poly.position
    dx, dy = [p[i] - c[i] for i in range(2)]
    draw.polygon(screen, (0,255,0),
                 [defloat(scale(offset(p, dx, dy)))
                  for p in polygon.exterior.coords],
                 1)
    draw.circle(screen, (0,255,0),
                defloat(scale(offset(c, dx, dy))),
                3)

def in_poly(point, poly):
    polygon = Polygon(poly.points)
    if poly.orientation:
        c = polygon.centroid.coords[0]
        polygon = Polygon([rotate(p, c, -poly.orientation)
                           for p in polygon.exterior.coords])
    c = polygon.centroid.coords[0]
    p = poly.position
    dx, dy = [p[i] - c[i] for i in range(2)]
    return polygon.contains(Point(offset(unscale(point), -dx, -dy)))

draw.circle(screen, (255,0,0), scale((1,1)), 5, 1)
for poly in polys:
    draw_poly(poly)

done = False

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True
        elif e.type == MOUSEBUTTONDOWN:
            p = mouse.get_pos()
            for poly in polys:
                if in_poly(p, poly):
                    print poly.position

    display.flip()
