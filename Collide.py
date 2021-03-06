from shapely.geometry import MultiPoint, Point, Polygon
from shapely.ops import polygonize

from math import *

import pygame
from pygame import display, draw, event, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

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

def orient_polygon(poly):
    polygon = Polygon(poly.points)
    if poly.orientation:
        c = polygon.centroid.coords[0]
        polygon = Polygon([rotate(p, c, -poly.orientation)
                           for p in polygon.exterior.coords])
    return polygon

def orient_multipoint(poly):
    polygon = MultiPoint(poly.points)
    if poly.orientation:
        c = polygon.centroid.coords[0]
        polygon = Polygon([rotate((p.x,p.y), c, -poly.orientation)
                           for p in polygon.geoms])
    return polygon

def draw_poly(poly, surface, color=None, width=None):
    polygon = orient_polygon(poly)
    c = polygon.centroid.coords[0]
    p = poly.position
    dx, dy = [p[i] - c[i] for i in range(2)]

    if color is None:
        color = (0,255,0)
    if width is None:
        width = 1
    
    draw.polygon(surface, color,
                 [defloat(scale(offset(p, dx, dy)))
                  for p in polygon.exterior.coords],
                 width)
    if width:
        draw.circle(surface, color,
                    defloat(scale(offset(c, dx, dy))),
                    3*width)

def draw_points(poly, surface, color=None, width=None):
    polygon = orient_multipoint(poly)
    c = polygon.centroid.coords[0]
    p = poly.position
    dx, dy = [p[i] - c[i] for i in range(2)]

    if color is None:
        color = (0,255,0)
    if width is None:
        width = 1

    maxd = (0,None,None)
    for i in range(len(polygon.geoms)):
        p = polygon.geoms[i]
        draw.circle(surface, color,
                    defloat(scale(offset((p.x,p.y), dx, dy))),
                    3*width)
        for j in range(i+1, len(polygon.geoms)):
            q = polygon.geoms[j]
            d = p.distance(q)
            if d > maxd[0]:
                maxd = (d, p, q)
    if maxd[0] > 0:
        p, q = maxd[1], maxd[2]
        draw.line(surface, color,
                  defloat(scale(offset((p.x,p.y), dx, dy))),
                  defloat(scale(offset((q.x,q.y), dx, dy))), width)

def in_poly(point, poly):
    polygon = orient_polygon(poly)
    c = polygon.centroid.coords[0]
    p = poly.position
    dx, dy = [p[i] - c[i] for i in range(2)]
    return polygon.contains(Point(offset(unscale(point), -dx, -dy)))

def orient_offset_polygon(poly):
    polygon = orient_polygon(poly)
    c = polygon.centroid.coords[0]
    p = poly.position
    dx, dy = [p[i] - c[i] for i in range(2)]
    return Polygon([offset(p, dx, dy)
                    for p in polygon.exterior.coords])

def intersect(a, b):
    ap, bp = [orient_offset_polygon(p) for p in [a,b]]
    overlap = ap.intersection(bp)

    if overlap.is_empty:
        return []

    if not hasattr(overlap, 'exterior'):
        return [Poly(p.exterior.coords, p.centroid.coords[0], 0)
                for p in polygonize(overlap)]
    
    return [Poly(overlap.exterior.coords,
                 overlap.centroid.coords[0], 0)]

def intersect_boundaries(a, b):
    ap, bp = [orient_offset_polygon(p) for p in [a,b]]
    intersection = ap.boundary.intersection(bp.boundary)
    if hasattr(intersection, 'geoms'):
        points = [(p.x, p.y) for p in intersection.geoms]
        return Poly(points, intersection.centroid.coords[0], 0)
    else:
        return None

background = Surface(screen.get_size())
background.fill((128,128,128))

screen.blit(background, (0,0))

sprites = Group()

done = False

dragging = None

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True
        elif e.type == MOUSEBUTTONDOWN:
            p = mouse.get_pos()
            for i in range(len(polys)):
                if in_poly(p, polys[i]):
                    dragging = i
                    break
            else:
                dragging = None
        elif e.type == MOUSEBUTTONUP:
            dragging = None

    if not dragging is None:
        polys[dragging].position = unscale(mouse.get_pos())
        
    sprites.empty()
    for i in range(len(polys)):
        poly = polys[i]
        sprite = Sprite()
        sprite.image = Surface(screen.get_size(), flags=SRCALPHA)
        draw_poly(poly, sprite.image)
        sprite.rect = Rect((0,0), sprite.image.get_size())
        sprites.add(sprite)

        for j in range(i+1, len(polys)):
            other = polys[j]
            for intersection in intersect(poly, other):
                sprite = Sprite()
                sprite.image = Surface(screen.get_size(), flags=SRCALPHA)
                draw_poly(intersection, sprite.image, (255,255,0), 0)
                sprite.rect = Rect((0,0), sprite.image.get_size())
                sprites.add(sprite)
            boundaries = intersect_boundaries(poly, other)
            if not boundaries is None:
                common = Sprite()
                common.image = Surface(screen.get_size(), flags=SRCALPHA)
                draw_points(boundaries, common.image, (255,0,0))
                common.rect = Rect((0,0), common.image.get_size())
                sprites.add(common)

    sprites.clear(screen, background)
    sprites.draw(screen)
    display.flip()
